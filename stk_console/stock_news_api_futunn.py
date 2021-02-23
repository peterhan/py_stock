import requests
import pdb
# https://www.futunn.com/new-quote/index-quote
# https://www.futunn.com/new-quote/top-heat-stock?market_type=1&_=1614059874996
# https://www.futunn.com/new-quote/quote-basic?security_id=63934883169938&market_type=1&_=1614059874995
# https://www.futunn.com/new-quote/quote-minute?security_id=63934883169938&market_type=1&_=1614059874997
# https://www.futunn.com/stock/01682-HK/company-profile#company
# https://www.futunn.com/stock/01682-HK/news
# https://www.futunn.com/stock/01682-HK/dividends#financing
# https://finance.futunn.com/api/finance/company-info?code=01682&label=hk
# https://finance.futunn.com/api/finance/dividend?code=01682&label=hk
# https://www.futunn.com/new-quote/quote-basic?security_id=63934883169938&market_type=1&_=1614060387395
# https://www.futunn.com/new-quote/news-list?page=0&page_size=10&_=1614060549335

# GET /questions/750604/freeing-up-a-tcp-ip-port HTTP/1.1
headers = {"Host": "stackoverflow.com"
,"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
,"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
,"Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2"
,"Accept-Encoding": "gzip, deflate, br"
,"Referer": "https://www.google.com.hk/"
,"Upgrade-Insecure-Requests": '1'
,"Cache-Control": "max-age=0"}
url='https://www.futunn.com/stock/01682-HK/company-profile'
resp = requests.get(url,headers=headers)
# print resp.text
pdb.set_trace()