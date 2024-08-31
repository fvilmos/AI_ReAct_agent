"""
This file implements a Reasoning and Acting (ReAct) Agent
Author: fvilmos
https://github.com/fvilmos

"""
from utils.prompts import *
from utils.utils import *
from enum import Enum
import re
import json



class ReActAgent():
    class NextAction(Enum):
        INIT=1
        RUN=2
        FN_CALL=3
        EXIT=4
    def __init__(self,model, sys_prompt:str,
                 init_histroy_prompt:str,
                 summariziation_prompt:str,
                 tool_signatures:list, 
                 options:dict={'temperature': 0.0, 'num_ctx': 8132, 'seed': 42, 'num_predict': 8132, 'stop':['\nObservation:',],  'mirostat_tau':0.0, "top_p":0.0} , max_iterations=5, verbose=0) -> None:
        self.model = model
        self.sys_prompt=sys_prompt
        self.__init_sys_prompt = sys_prompt
        self.options = options
        self.max_iterations = max_iterations
        self.summariziation_prompt = summariziation_prompt
        self.verbose = verbose
        self.history = init_histroy_prompt
        self.__init_histroy_prompt = init_histroy_prompt
        self.tool_signatures = tool_signatures
        self.tool_names = [str(t['function']['name']) for t in tool_signatures]
        self.tool_docs = "".join([t['function']['name'] + ":" + t['function']['description'] + "\n" for t in tool_signatures])
        
        # init ReAct state machine
        self.next_action = self.NextAction.INIT

    def get_actions(self, msg:str):
        """
        pharse model output for action tags
        return 2 lists of action, and action input list 
        """
        action = re.findall(r"Action: (.+)\n", msg, re.IGNORECASE)
        action_input = re.findall(r"Action Input: (.+)", msg, re.IGNORECASE)
        
        return action, action_input
        
    def decide_next_action(self, msg:str) -> None:
        """
        Used by the state machine to define the next action.
        Targets: transition to a functiona call or to final answer, from the RUN state
        """

        if self.next_action == self.NextAction.RUN:
            # check if we need to do a functioan call
            for t in self.tool_names:
                if t in msg:
                    self.next_action = self.next_action.FN_CALL
                    break

            # pharse input for actions
            actions, action_inputs = self.get_actions(msg)
            
            if "Final Answer" in actions:
                self.next_action = self.NextAction.EXIT
    
    def function_pharser(self,action,action_input, tools_json_signatures, verbose=0):
        """
        generates a dictionary accroding to ollama function call API, or as fallback, pharses the action and action input with regular expression  
        NOTE: currently ollma function call generates an empty message for assistant, therefore 2 calls are used:
        1st - to generate the assistant message
        2nd - to pharse the output and generate the function call
        """
        
        local_prompt = [{"role": "system", "content": "You use as best you can the input information from user, to call one of the functions. Analyze the input if it has another function call, call it separately."},
                 {"role":"user", "content":"Functions name: " + str(action) + "\n" + "Parameters: " + str(action_input)}]

        # generate function call structure
        answer = answer_a_question_msg(msg=local_prompt,model=self.model,opt=self.options,tool_list=self.tool_signatures, return_raw=True)

        # make the functiona call
        if 'tool_calls' in answer['message']:
            for t in answer['message']['tool_calls']:
                
                # get function elements
                f_name = t['function']['name']
                f_params = t['function']['arguments']
    
                # validate param types
                fn_signature = json.loads(function2json(eval('tools.' + f_name)))
                fn_val_prop = fn_signature['function']['parameters']['properties']
                
                # create argument list
                arg_list = [f'{a[0]}' for a in dict(f_params).items()]
    
                arg_type_list = []
                for a in arg_list:
                    if a in fn_val_prop:
                        arg_type = fn_val_prop[str(a)]['type']
                        arg_type_list.append(arg_type)
                    else:
                        pass
    
                # generate arg string
                arg_string = ""
                for i,a in enumerate(dict(f_params).items()):
                    if arg_type_list[i]=='str':
                        arg_filtered = a[1].replace("\"","")
                        arg_string += f'{a[0]}="{arg_filtered}", '
                    else:
                        arg_string += f'{a[0]}={a[1]}, '
    
                # function call
                f_return = []
                try:
                    f_return = eval(f'tools.{f_name}({arg_string})')
                    if self.verbose:
                        print (f'function call: tools.{f_name}({arg_string}) \n')
    
                except BaseException as err:
                    f_return = [str("re-formulate the Action Input to solve this issue " + str(err.args))]
        return f_return
        
    def update_prompt_list(self,sys_prompt:str,history:str, question:str):
        """
        Update system prompt over the time, with history messages
        """
        return [{"role": "system", "content":sys_prompt + history}, {"role": "user", "content": question}]

    def reinit(self):
        """
        Restore original state for a new run
        """
        self.sys_prompt = self.__init_sys_prompt
        self.history = self.__init_histroy_prompt
        self.next_action = self.NextAction.INIT
            
    def __call__(self, question, verbose=0):
        """
        ReAct loop, at the end generates the final answer to the input question
        """
        msg = []
        answer = ""
        self.reinit()

        # skipp empty calls
        if len(question) == 0:
            answer = "empty call, return exit"
            self.next_action = self.NextAction.EXIT
            
        # start the ReAct loop
        for i in range (self.max_iterations):
            
            # determin the next action to be done
            # check if Final Answer is given => exit
            # check if function call needed to be done => call function
            # check if end of itereation is reached => exit
            # summarize the activity

            # state machine INIT state handler 
            if self.next_action == self.NextAction.INIT:
                
                # parse system prompt
                self.sys_prompt = self.sys_prompt.replace("{tool_docs}",self.tool_docs)
                
                self.tool_names.append("Final Answer")
                self.sys_prompt = self.sys_prompt.replace("{tool_names}",f'[{"".join([tn + "," for tn in self.tool_names])}]')
                
                self.history = self.history.replace("{question}",question)
                msg = self.update_prompt_list(self.sys_prompt, self.history + "Thought: \n", question)

                if verbose==1:
                    print (f"NextAction.INIT {i}: ", "INIT")

                # change state
                self.next_action = self.NextAction.RUN
            
            # state machine RUN state handler   
            if self.next_action == self.NextAction.RUN:
                # generate a set of thoughts, action based on the current input
                answer = answer_a_question_msg(msg=msg,model=self.model,opt=self.options,tool_list=[], return_raw=False)

                #update history
                self.history += answer

                if verbose==1:
                    print (f"NextAction.RUN {i}: ", answer)

                # decide on the next action
                self.decide_next_action(answer)

            # state machine FN_CALL state handler 
            if self.next_action == self.NextAction.FN_CALL:
                # pharse input for actions
                actions, action_inputs = self.get_actions(answer)
                
                if len(actions)>0 and len(action_inputs)>0:
                    fn_name_to_call = actions[-1]
                    fn_parameters_to_call = action_inputs[-1]
                    
                    fn_call_result = ""

                    # fist try to use ollama structure, fallback to regular expression search
                    fn_parameters_to_call = fn_parameters_to_call.replace("\"","")
                    try:
                        fn_call_result = self.function_pharser(fn_name_to_call,fn_parameters_to_call,self.tool_signatures)
                    except:
                        fn_call_result = ""

                    if fn_call_result == "":
                        try:
                            fn_call_result = eval(f"tools.{fn_name_to_call}(\"{fn_parameters_to_call}\")")
                        except:
                            fn_call_result = "Function call unsuccessfull, try with other parameters!"
                            
                    # generate function return
                    f_return = ""
                    
                    if isinstance(fn_call_result, list):
                        f_return = "-".join([a + "\n" for a in fn_call_result])
                    else:
                        f_return = str(fn_call_result)
                    
                    ret = f"\nObservation: {f_return}\n"
                    self.history += ret
                    
                    msg = self.update_prompt_list(self.sys_prompt, self.history + "Thought: \n", ret)

                    #change state
                    self.next_action = self.NextAction.RUN

                    if verbose==1:
                        print (f"NextAction.RUN {i}: ", actions[-1], action_inputs[-1] )
            
            # state machine EXIT state handler         
            if self.next_action == self.NextAction.EXIT:
                    break

        
        # summarize what we learned and break
        msg = self.update_prompt_list(self.sys_prompt, 
                                      self.history + answer, self.summariziation_prompt)
        answer = answer_a_question_msg(msg=msg,model=self.model,opt=self.options,tool_list=[], return_raw=False)

        return answer