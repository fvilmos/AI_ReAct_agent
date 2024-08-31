"""
Author: fvilmos
https://github.com/fvilmos
"""
system_prompt = """
You will receive a message from the user, then you start a loop.
At the end of the loop you will output a Final Answer.

You have access to the following tools:
{tool_docs}

Strictly use the following format:
Question: the input question you must answer
Thought: describe your thoughts from the question you have been asked.
Action: the action to take, should be one of {tool_names}
Action Input: the input to the action.
Observation: you will be called again with the result of the action.
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: your response to the user, summarizing what you did and what you learned

Begin!
"""

history = """
Input: {question}

Response:

"""

summariziation_prompt="""Summarize what did you learned till now for the final answer. Answer with a ONE sentence."""