"""
This file implement utility functions to work with ollama server.
Author: fvilmos
https://github.com/fvilmos

"""

from utils import tools
from typing import get_type_hints

import ollama
import inspect
import json
import os
import cv2

def answer_a_question_msg(msg =[{"role":"user", "content":""}], 
                          model='llama2', format='',
                          tool_list=[],
                          opt= {'temperature': 0.0,'num_ctx': 4096,'seed': 42,'num_predict': 4096},
                          return_raw=False):
    """
    Usefull to answer a guestion.
    msg - list of system and user message context
    model - the desired model to be used, served by ollama
    opt - model configuration options, i.e. temperature
    """
    
    ret = ollama.chat(model=model,
                      format=format,
                      tools=tool_list,
                      options=opt,
                      messages=msg,
                     )
    if return_raw == False:
        ret = ret['message']['content']

    return ret


def answer_on_image_content(msg =[{"role":"user", "content":"", "images":[]}], 
                          model='llava', format='',
                          tool_list=[],
                          opt= {'temperature': 0.0,'num_ctx': 4096,'seed': 42,'num_predict': 4096},
                          return_raw=False, use_encoded=False):
    """
    Taks an image as input and descibs it.
    Input can be:
    - a string list
    - a source i.e. 0 = webcam
    - encoded string list, when return_raw - flag is activated

    Args:
        msg (list, optional): the prompt. Defaults to [{"role":"user", "content":"", "images":[]}].
        model (str, optional): the model used for image to text generation. Defaults to 'llava'.
        format (str, optional): '' or json. Defaults to ''.
        tool_list (list, optional): tools to be used in ollama format. Defaults to [].
        opt (dict, optional): model options. Defaults to {'temperature': 0.0,'num_ctx': 4096,'seed': 42,'num_predict': 4096}.
        return_raw (bool, optional): if to reun the model putput directly. Defaults to False.
        use_encoded (bool, optional): if input is an encoded string or a string path. Defaults to False.

    Returns:
        result: depending on the return_raw parameter can be a text of a dictionarry
    """

    # use encodeing if needed
    if use_encoded == False:
        # load files
        img_list = []
        source_list=[]

        # get the source list
        for el in msg:
            if 'images' in el:
                source_list = el['images']
                break

        # generate the encoded image list
        for fimg in source_list:
            try:
                if '.' in fimg:
                    img = cv2.imread(fimg)
                else:
                    #use another source
                    img = get_cam_image(int(fimg))
            except BaseException as err:
                print (f"Error with: {fimg}, {err}")
                continue

            en_img = cv2.imencode('.jpg', img)[1].tobytes()
            img_list.append(en_img)

        
        # check if input available
        if len(img_list)==0:
            print ("No input! Exiting")
            exit()
        
        #update message with encoded image list
        for el in msg:
            if 'images' in el:
                el['images'] = img_list
                break
    else:
        # use directly the input
        pass

    ret = ollama.chat(model=model,
                    options=opt,
                    messages=msg,
                    format=format,
                    tools=tool_list
                    )
    
    if return_raw == False:
        ret = ret['message']['content']

    return ret

def get_cam_image(source:int=0, skipp_frames=15, delay:int=10):
    """
    Get a picture from a source specified

    Args:
        source (int, optional): By defaul use webcam. Defaults to 0.
        skipp_frames (int, optional): Number of frames skipped before image returned. Defaults to 15.

    Returns:
        array: image
    """
    cam = cv2.VideoCapture(source)
    rimg = None
    _,img = cam.read()
    
    count = skipp_frames
    get_images = True

    while get_images:
        _,img = cam.read()
        #cv2.waitKey(delay)
        if (img is None):
            continue
        if count >=0: 
            count -=1
        else:
            get_images = False
    del(cam)

    # test if image exist
    if img is not None:
        # show image
        rimg = img
    else:
        print ("something went wrong, check camera source!")
    return rimg


def get_tools(docstr=False):
    """
    return a set with the availble tool names
    used the docstring information if requred
    """
    item_list = dir(tools)
    fn_names = {}
    if docstr:
        for it in item_list:
            if it[0]!="_":
                dstr = eval("tools."+ it).__doc__.strip().replace("\n","").replace("\\","").replace("\t","").replace("  ","")
                fn_names[it] = dstr
    else:
        fn_names = {f"{it}" for it in item_list if it[0]!="_"}
        
        
    return fn_names
get_tools(docstr=True)

def function2json(fn):
    """
    Transforms a function to ollma function call structure.
    https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-completion

    i.e. def get_weather(city: str="") ==>
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "current weather for a location",
        "parameters": {
          "type": "object",
          "properties": {
            "city": {
              "type": "string",
              "description": "city"
            },
          },
          "required": ["city"]
        }
      }
    }
    """
    # get function signature
    signature = inspect.signature(fn)
    type_hints = get_type_hints(fn)

    # create the function structure, ollama style
    function_structure = {
        "type": "function",
        "function": {
            "name": fn.__name__,
            "description": str(fn.__doc__).strip().replace("\n","").replace("\\","").replace("\t",""),
            "parameters": {
                "type":"object",
                "properties":{},
            },
        },
        #"return": type_hints.get("return", "void").__name__ if str(type_hints.get("return", "void")) != "void" else None,
    }
    
    # fill function parameters
    for name, _ in signature.parameters.items():
        
        # get type of the function parameter
        p_type = type_hints.get(name, type(None))
        p_type_filtered = p_type.__name__ if 'class' in str(p_type) else p_type

        # update function dict
        function_structure["function"]["parameters"]["properties"][name] = {"type": p_type_filtered}
    p_temp  =  function_structure["function"]["parameters"]["properties"]
    
    p_param = function_structure["function"]["parameters"]
    p_param["required"]=list(dict(p_temp).keys())

    return json.dumps(function_structure, indent=2)