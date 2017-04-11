import lxml.html.soupparser
import requests
from bs4 import BeautifulSoup

url = "http://finance.sina.com.cn/zl/stock/2017-04-11/zl-ifyecezv3083345.shtml"
resp = requests.get(url)

print(resp.content.decode())
# doc = lxml.html.soupparser.fromstring(resp.content, features='html5lib')
# print(doc.xpath("//div[@class='artInfo']")[0].xpath(""))
