### ReAct (Reasoning and Acting) agent with local LLM

The implements a Reasoning and Acting[3] agent with local LLM and tools usage in Python. The ReAct prompts LLMs via a chain of thoughts approach [4] to generate local reasoning traces independent from the environment in the first step and then derive answers or decisions based on previous thoughts and history, in the final step.

```mermaid
graph LR
A(N reasoning traces) -->B(LLM) -->C(Environment)
  B-->A
  C-->B

```
Sample trasoning traces:
```code
Question:  What is the last pet's name of the current USA president? If there are more, list all of them.
NextAction.INIT 0:  INIT
NextAction.RUN 0:  Thought: The question asks for the last pet's name of the current USA president and possibly other pets they may have had.
Action: search_duckduckgo
Action Input: last pet of current USA president
NextAction.RUN 0:  search_duckduckgo last pet of current USA president
NextAction.RUN 1:  Thought: I have found information about the 
pets of past and current USA presidents.
Action: search_duckduckgo
Action Input: pets of Joe Biden
NextAction.RUN 1:  search_duckduckgo pets of Joe Biden
NextAction.RUN 2:  Thought: I now know the name of Joe Biden's 
first dog, which was adopted in 2008.
Action: Final Answer
Final Answer: The current USA president's last pet's name is Champ, and they also have a German Shepherd named Major, who was 
born on January 17, 2018.
```


Currently available tools (utils.tools), see also[5]:  get_local_datetime, calculate, search_dudkduckgo

#### Prerequisites

1. install ollama[1]
2. pull ollama moldes: llama3.1 [2]
```NOTE: you can use different LLMs from the ollama model zoo, but, for tool usage / function call is needed one that support this feature i.e. llama3.1```

#### Test results

```lua
Question:  where was born Romania's faimous fotball star Hagi's son?
Answer: I learned that Ianis Hagi, the son of Romanian famous football star Gheorghe Hagi, was born on October 22, 1998, in Istanbul, Turkey.

Question:  Janet's ducks lay 16 eggs per day, She eats 3 for breakfast averry 
morning and bakes muffins for her friends every day with 4. She sells the reminder for 2$ per egg. How much money does she make in a single day?
Answer: Janet makes $18 in a single day from selling her remaining eggs after eating and baking some.

Question:  What is the last pet's name of the current USA president? If there 
are more, list all of them.
Answer: The current USA president, Joe Biden, has two German Shepherds as pets, named 
Major and Commander.
```

#### Resources
1. [Ollama - local model server](https://ollama.com/)
2. [llama3.1 new state-of-the-art model from Meta](https://ollama.com/library/llama3.1)
3. [REACT: SYNERGIZING REASONING AND ACTING IN LANGUAGE MODELS, Yao et all, arXiv:2210.03629v3 [cs.CL]](
https://doi.org/10.48550/arXiv.2210.03629)
4. [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models, Wei et all, arXiv:2201.11903 [cs.CL]](https://arxiv.org/abs/2201.11903)
5. [Local LLM utilities](https://github.com/fvilmos/local_llm_utilities)


/Enjoy.
