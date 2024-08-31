"""
Utility file, that implements tools for a ReAct agent
Function names for the file will be used to create dynamically the available tools list.
Function comments will be used to create the prompt for tool usage

NOTE: All imports from this module scope shall be hidden (under the function) othervise will be imported in the global scope!

Author: fvilmos
https://github.com/fvilmos
"""

def get_local_datetime()->str:
    """
    Provide hte local date and time. 
    """
    import time
    return str(time.ctime())

def calculate(expr:str)->str:
    """
    evaluats matematical expressions and caluclates the result.
    """
    return eval(expr)

# def search_wikipedia(search:str)->list:
#     """
#     Searches the wikipedia for an answer.
#     """
#     #modified from : https://api.wikimedia.org/wiki/Searching_for_Wikipedia_articles_using_Python
#     import requests
#     import json
#     language_code = 'en'
#     number_of_results = 1


#     base_url = 'https://api.wikimedia.org/core/v1/wikipedia/'
#     endpoint = '/search/page'
#     url = base_url + language_code + endpoint
#     parameters = {'q': search, 'limit': number_of_results}
#     response = requests.get(url, params=parameters)

#     # process results
#     response = json.loads(response.text)
#     return str(response['pages'][0]['excerpt'].strip().replace('<span class="searchmatch">','').replace('</span>','').replace('(&quot;','').replace('.&quot;)',''))

def search_duckduckgo(search:str, top_k:bool=True, verbose=0)->list:
    """
    Searches the web for a precise answer from many sources, all purpuse search.
    """
    # modified from: https://stackoverflow.com/questions/11722465/duckduckgo-api-not-returning-results

    import re
    from urllib import parse,request
    from bs4 import BeautifulSoup

    query = parse.quote_plus(search)

    site = request.urlopen("http://duckduckgo.com/html/?q="+query)
    data = site.read()
    soup = BeautifulSoup(data, "html.parser")

    # force to provide top 5 results
    if top_k:
        result_list = soup.find("div", {"id": "links"}).find_all("div", {'class': re.compile('.*web-result*.')})[0:5]
    else:
        result_list = soup.find("div", {"id": "links"}).find_all("div", {'class': re.compile('.*web-result*.')})[0:1]
    
    results = []

    for rl in result_list:
        try:
                results.append(rl.find("a", {"class": "result__snippet"}).get_text().strip("\n").strip())
        except:
                results.append(None)
    if verbose:
        print ("search_duckduckgo:", results)
    
    return results
