from pz3_crawler.core.crawler import Crawler
from pz3_crawler.core.search_crawler import SearchCrawler
from pz3_crawler.core.crawler_mgr import CrawlerMgr
from pz3_crawler.conf.setting import log


def sina_list_crawler(key):
    header = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Cookie': 'UOR=www.baidu.com,www.sina.com.cn,; SINAGLOBAL=183.48.243.58_1490754786.942741; Apache=183.48.243.58_1490754787.200075; SGUID=1490754787485_59067253; vjuids=5e96c53d.15b17e8d9f5.0.50f26de15aba2; ULV=1490754788074:2:2:2:183.48.243.58_1490754787.200075:1490754787350; SUB=_2AkMvh5I2f8NhqwJRmP4Qz2LraIRzyArEieKZ22PtJRMyHRl-yD83qlEbtRDDSXejvLr3SNFBJccNeVcArgPyKw..; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WW.hF-G5Bgv.pNR0ra1PneR; U_TRS1=0000003a.2ada593e.58db1d2a.f45e7918; U_TRS2=0000003a.2aec593e.58db1d2a.235df27e; WEB2_OTHER=86b3c3bb2c3b4f93e9d072c16c59cb0f; rotatecount=1; SessionID=b7mqeo3i1thp0dt3f2cil3kdi7; vjlast=1490757084; lxlrttp=1490686119',
        'Host': 'api.search.sina.com.cn',
        'Referer': 'http://www.sina.com.cn/mid/search.shtml?q=%E4%B8%96%E7%95%8C%E6%9C%80%E5%A4%A7%E9%87%91%E5%B8%81%E8%A2%AB%E5%81%B7',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36'
    }

    url = "http://api.search.sina.com.cn/?c=news&t=&q=%E5%B0%8F%E7%B1%B3&pf=2131425521&ps=2130770168&page=2&stime=2016-04-11&etime=2017-04-13&sort=rel&highlight=1&num=10&ie=utf-8&callback="

    end_cond = {
        # "end_time": "2014-01-01 00:00:00",
        "max_count": 10
    }
    encode = "gbk"

    parse_rule = {
        "domain": "sina.com.cn",
        "type": "search",
        "parse_py": [
            {
                "rule_uuid": "xxxx",  # 这条匹配规则的ID，
                "url_match": ["^http[s]?://api.search.sina.com.cn/\?", ],
                "modulepath": "pz3_crawler.parse_py.sina_search",  # python类的命名空间
                "class": "sina_search",
                "function": "main"
            }
        ],
    }
    param = {
        "start_url": url,
        "end_cond": end_cond,
        "paser_rule": parse_rule,
        "header": header,
        "proxy": None,
        "encode": encode,
        "keyword": key}
    crawler = SearchCrawler(**param)

    return crawler.get_page_urls()


def main():
    cm = CrawlerMgr()
    for item in sina_list_crawler("小米"):
