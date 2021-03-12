import urllib2
import json
import bs4
import pdb
url = 'http://www.bjbus.com/home/ajax_rtbus_data.php?act=busTime&selBLine=681&selBDir=5420906457452494752&selBStop=2'
fd  = urllib2.urlopen(url)
txt = fd.read()
# print txt
html = json.loads(txt)['html']
soup= bs4.BeautifulSoup(html,'lxml')# html.encode('gbk')
# print soup.prettify().encode('gbk','ignore')
pdb.set_trace()
for d in soup.find_all('div'):
    print d.find_all('i')
    print d.find_all('i',class_='busc')
    print d.text.encode('gbk','ignore')
