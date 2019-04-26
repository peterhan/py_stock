#!coding:utf8
import requests
import bs4
import pdb
url='https://blog.evianzhow.com/explanation-of-candlesticks-pattern-recognization-in-ta-lib/'
resp = requests.get(url)
soup=bs4.BeautifulSoup(resp.text,"lxml")

h2s=soup.find_all('h2')
tlis=soup.find_all('li')

infos={}
keys=u'函数原型: 定义: 最少所需的蜡烛线数量: 形态: 信号:'.split(' ')
for key in keys:
    infos[key]=[tli.text.strip() for tli in tlis if tli.text.find(key)!=-1]


def p(*objs):
    print '  |  '.join(objs).encode('gbk')
    
ta_info={}
for i,h2t  in enumerate(h2s):
    if i>60:
        break
    name = h2t.text
    fdesc = infos[keys[0]][i]
    ftag = fdesc.split('CDL')[1].split('(')[0]
    intro = infos[keys[1]][i]
    cdlcnt = infos[keys[2]][i]
    figure = infos[keys[3]][i]
    sig = infos[keys[4]][i]
    p('No:%s'%i, ftag, name,intro,fdesc)
    ta_info[ftag]={'name':name.encode('utf8'),'intro':intro.encode('utf8'),'desc':fdesc.encode('utf8'),
        'figure':figure.encode('utf8'),'cdlcnt':cdlcnt.encode('utf8'),'signal':sig.encode('utf8')}
    
import json
json.dump(ta_info,open('talib_pattern_name.json','w'),indent=2,ensure_ascii=False)
# pdb.set_trace()