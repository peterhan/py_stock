import datetime
import time
import json
import pdb
from requests import get,post
from bs4 import BeautifulSoup

def to_timestamp(ts):
    return datetime.datetime.fromtimestamp(float(ts))

DATE_FORMAT='%Y-%m-%d %H:%M'
def ts2unix(str_date,mask=DATE_FORMAT):
    return int(time.mktime(
         time.strptime(str_date, mask)
        )) 
    
def js_dumps(obj,encode='gbk'):    
    return json.dumps(obj,indent=2,ensure_ascii=False).encode(encode,'ignore')
    
def gen_random(n=16):
    from random import randint
    start = 10 ** (n - 1)
    end = (10 ** n) - 1
    return str(randint(start, end))
    
def get_article_detail(url,tag='article'):
    url = url
    html = get(url).text
    # pdb.set_trace()
    soup = BeautifulSoup(html,"lxml")
    # pdb.set_trace()
    text =  map(lambda x:x.text ,soup.find_all(tag))
    return '\n'.join(text)

def json_extract(obj, key):
    """Recursively fetch values from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    values = extract(obj, arr, key)
    return values

def flatten_json(y,mode='plain',sep='.'): 
    out = {}   
    def flatten(x, name =''):           
        # If the Nested key-value  
        # pair is of dict type 
        if type(x) is dict:               
            for a in x: 
                if mode=='plain':
                    flatten(x[a], name + "%s"%a + sep)
                else:
                    flatten(x[a], name + "['%s']"%a + '')                   
        # If the Nested key-value 
        # pair is of list type 
        elif type(x) is list:               
            i = 0              
            for a in x:                 
                if mode=='plain':
                    flatten(a, name + "%s"%str(i) + sep) 
                else:
                    flatten(a, name + "[%s]"%str(i) + '') 
                i += 1
        else: 
            if mode=='plain':
                out[name[:-1]] = x   
            else:
                out[name[:]] = x   
    flatten(y) 
    return out 
 

def dict_selector(dic,keys=None,mode='keys'):
    res = dict()
    if keys!=None:
        lst = [(k,v) for k,v in dic.items() if k in keys]
        res = dict(lst)
    if mode=='plain':
        for key,sel in dic.items():
            if isinstance(sel,dict) or isinstance(sel,list):
                continue
            res[key] = sel
    return res
    
def nest_selector(obj,path):
    patharr=path.split('.')    
    sel = obj
    for pathpart in patharr:
        if isinstance(sel,dict):
            sel=sel.get(pathpart,'')
        elif isinstance(sel,list):
            sel=sel[int(pathpart)]
        else:
            try:sel=getattr(sel,pathpart)
            except:sel=''
    return sel