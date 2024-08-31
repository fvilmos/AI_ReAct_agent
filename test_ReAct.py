"""
Test the ReAct agent
Author: fvilmos
https://github.com/fvilmos

"""

from utils.ReAct_agent import ReActAgent
from utils.utils import *
from utils.prompts import *
import json


# load config data
jf = open(".\\data\\config.json",'r')
cfg_data=json.load(jf)

MODEL=cfg_data['LLM_MODEL']
MAX_TRIES=cfg_data['MAX_TRIES']
VERBOSE=cfg_data['VERBOSE']


# process available tools
tools_names = get_tools()
tools_names_docs = get_tools(docstr=True)
tools_functions = [eval('tools.'+ str(n)) for n in tools_names]
tools_json_signatures = [json.loads(function2json(f)) for f in tools_functions]

if VERBOSE:
    print ("available tools:",tools_names)
    print("sample - tool signature:",json.dumps(tools_json_signatures[0], sort_keys=True, indent=4, default=str))


question = ["where was born Romania's faimous fotball star Hagi's son?",
            "Janet's ducks lay 16 eggs per day, She eats 3 for breakfast averry morning and bakes muffins for her friends every day with 4. She sells the reminder for 2$ per egg. How much money does she make in a single day?",
            "What is the last pet's name of the current USA president? If there are more, list all of them.",
           ]

simple_ReAct_agent = ReActAgent(model=MODEL, sys_prompt=system_prompt, 
                                init_histroy_prompt=history,
                                summariziation_prompt=summariziation_prompt,
                                tool_signatures=tools_json_signatures,
                                max_iterations=MAX_TRIES,verbose=VERBOSE)

for q in question:
    print ("\nQuestion: ",q)
    answer = simple_ReAct_agent(q, verbose=VERBOSE)
    print ("Answer: ",answer)