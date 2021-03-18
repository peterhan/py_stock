import datetime
import time
import json
import pdb
from collections import OrderedDict
from requests import get,post
from bs4 import BeautifulSoup
import pandas as pd
import locale
ENCODE = locale.getpreferredencoding()
def to_timestamp(ts):
    return datetime.datetime.fromtimestamp(float(ts))

DATE_FORMAT='%Y-%m-%d %H:%M'
def ts2unix(str_date,mask=DATE_FORMAT):
    return int(time.mktime(
         time.strptime(str_date, mask)
        )) 

def unix2ts(uxts,mask=DATE_FORMAT,base=10):
    return \
        datetime.datetime.fromtimestamp( 
         int(uxts,base)/1000 
        ).strftime(mask)

def get_date(fmt=DATE_FORMAT,base= datetime.datetime.now(), isobj=False, **kwargs ):
    i_str2date=lambda str_date,fmt: datetime.datetime.fromtimestamp(time.mktime(time.strptime(str_date,fmt)))
    if type(base)==str:
        dateobj= i_str2date(base,fmt)+ datetime.timedelta( **kwargs)
    else:
        dateobj = base + datetime.timedelta( **kwargs)
    if isobj: 
        return dateobj
    else: 
        return dateobj.strftime(fmt)
    
def js_dumps(obj,encode='gbk'):    
    return json.dumps(obj,indent=2,ensure_ascii=False).encode(encode,'ignore')
    
    
def gen_random(n=16):
    from random import randint
    start = 10 ** (n - 1)
    end = (10 ** n) - 1
    return str(randint(start, end))
    
def get_article_detail(url,tag='article'):
    print url
    url = url
    html = get(url).content
    # pdb.set_trace()
    soup = BeautifulSoup(html,"lxml")
    tags = soup.find_all(tag)
    # pdb.set_trace()
    texts =  filter(lambda x:len(x)>0,map(lambda x:x.text.strip().replace('\n','') ,tags))
    return texts,tags

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
    
def time_count(func):
    def wrapper(*arg, **kw):
        t1 = time.time()
        res = func(*arg, **kw)
        t2 = time.time()
        tcnt = (t2-t1)*1000
        if tcnt>1000:
            print '#[%s] take %0.2f ms'%(func.__name__, tcnt)
        return res
    return wrapper
    
def cli_select_menu(select_dic, default_input=None, menu_columns=5, column_width=22, control_flag_map = None):
    '''
    cli menu
    return select_keys,control_flags
    '''
    default_control_flag_map = {
        'q':'quit','d':'detail','i':'pdb','s':'onestock','top':'top','inst':'inst'
        ,'r':'realtime','f':'fullname','g':'graph','u':'us','z':'zh','e':'emd','c':'catboost'
        ,'n':'news_sina'
    }
    select_map = {}
    control_flags = []
    ## generate menu
    stype = 'list'
    if isinstance(select_dic,pd.Series):
        stype='series'        
        for i, key in select_dic.iteritems():            
            select_map[i] = key
    else:
        if isinstance(select_dic,OrderedDict):
            stype='list'
        elif isinstance(select_dic,dict):
            stype='dict'
        for i, key in enumerate(select_dic):
            idx = i+1
            select_map[idx] = key
    for idx,key in select_map.items():
        print ('(%s) %s'%(idx,key.encode(ENCODE,'ignore'))).ljust(column_width),
        if (idx)%menu_columns == 0:
            print ''
    print ''
    if default_input is None:
        this_input = raw_input('SEL>')
    else:
        this_input = default_input
    input_words = this_input.strip().replace(',',' ').replace('  ',' ').split(' ')    
    
    if control_flag_map is None:
        control_flag_map = default_control_flag_map
    ## extract sub select list
    if '>' in input_words:
        idx = input_words.index('>') 
        wd = input_words[idx:]
        input_words = input_words[:idx]
        control_flags.append( wd )
    ## extract control flag
    for key,vlu in control_flag_map.items():
        for word in input_words:
            if key == word:
                control_flags.insert(0,vlu)
                input_words.remove(key)
    ## extract select_keys
    try:
        selected_keys = []
        for word in input_words:
            if len(word)==0:
                continue
            if len(word)<=3 and word.isdigit():
                if stype=='dict':
                    selected_keys.append(select_dic[ select_map[int(word)] ]) 
                elif stype=='series':
                    selected_keys.append(int(word)) 
                else:
                    selected_keys.append(select_map[int(word)]) 
            else:
                selected_keys.append(word)
        return selected_keys, control_flags
    except Exception as e:
        print(e)
        return [], control_flags
        
if __name__=='__main__':
    # print cli_select_menu(pd.Series('a b c d'.split(' ')))
    # print cli_select_menu({'a':['b','c'],'c':['d','e']})
    # print cli_select_menu(['a','b','c'])
    text,tags= get_article_detail('https://news.futunn.com/flash/12271149','div')
    pdb.set_trace()
    # print get_article_detail('https://news.futunn.com/flash/12271149','div')