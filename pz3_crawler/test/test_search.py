# -*- coding: utf-8 -*-
__author__ = 'commissar'
import unittest
import json
from pz3_crawler.core.search_crawler import SearchCrawler

class TestSearch(unittest.TestCase):

    def test_search_get_result_urls(self):
        '''
        测试通过传一个搜索页面的起始URL，得到所有的结果URL
        :return:
        '''

        url = "http://tieba.baidu.com/f/search/res?isnew=1&kw=&qw=%C3%C0%CD%BC%D0%E3%D0%E3%20%C3%C0%CD%BC%CA%D6%BB%FA2&un=&rn=10&pn=1&sd=&ed=&sm=1&only_thread=1"
        # url = "http://tieba.baidu.com/f/search/res?isnew=1&kw=&qw=%B8%E8%CA%D6%20%C2%B9%EA%CF&un=&rn=10&pn=1&sd=&ed=&sm=1&only_thread=1"

        end_cond = {
            "end_time":"2014-01-01 00:00:00",
            "max_count":10
        }

        header = {
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding":"gzip, deflate, sdch",
                "Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6",
                "Cache-Control":"max-age=0",
                "Connection":"keep-alive",
                "Host":"tieba.baidu.com",
                "Upgrade-Insecure-Requests":"1",
                "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"
             }
            # end_rule = [
            #     'div\sclass=\"s_post\"',
            # ],

        encode = 'gbk'

        parse_rule = {
            "domain":"baidu.com",
            "type":"search",               #其有两个值，article或comment
            "parse_rules":[
                { "url_match": [
                    "^http[s]?://tieba.baidu.com/f/search/res\?"
                ],
                "rule_uuid": "27d0440e04b8cc1d82b0edf17f85fa39",
                "search_items": {
                    "property": {
                        "media_name": [
                            {
                                "express": "//font[@class='p_violet'][2]",
                                "type": "xpath",
                                "func": "text"
                            }
                        ],
                        "title": [
                            {
                                "express": "//a[@class='bluelink']",
                                "type": "xpath",
                                "func": "html"
                            },
                            {
                                "express": ">([\\S\\s\\w]+)?<\\/a>",
                                "type": "regex",
                                "param": 1,
                                "func": "search"
                            }
                        ],
                        "url": [
                            {
                                "express": "//a[@class='bluelink']/@href",
                                "type": "xpath",
                                "func": ""
                            },
                            {
                                "express": "http://tieba.baidu.com",
                                "type": "postfix"
                            }
                        ],
                        "create_at": [
                            {
                                "express": "font.p_date",
                                "type": "css",
                                "func": "text"
                            }
                        ],
                        "channel": [
                            {
                                "express": "//font[@class='p_violet'][1]",
                                "type": "xpath",
                                "func": "text"
                            }
                        ],
                        "media_url": [
                            {
                                "express": "//font[@class='p_violet'][2]/../@href",
                                "type": "xpath",
                                "func": ""
                            },
                            {
                                "express": "http://tieba.baidu.com",
                                "type": "postfix"
                            }
                        ]
                    },
                    "express": [
                        {
                            "express": "div.s_post",
                            "type": "css",
                            "func": "html"
                        }
                    ]
                },
                "cur_page_num": [
                    {
                        "express": "span.cur",
                        "type": "css",
                        "func": "text"
                    }
                ],
                "next_url": [
                    {
                        "express": "span.cur + a",
                        "type": "css",
                        "func": "html"
                    },
                    {
                        "express": "href=[\"']([^\"']+?)[\"']",
                        "type": "regex",
                        "param": 1,
                        "func": "search"
                    },
                    {
                        "express": "http://tieba.baidu.com",
                        "type": "postfix"
                    },
                    {
                        "express": "",
                        "type": "other",
                        "func": "unescape"
                    }
                ]
                 }
            ]
        }

        param = {
            "start_url":url,
            "end_cond":end_cond,
            "paser_rule":parse_rule,
            "header":header,
            "proxy":None,
            "encode":encode,
            "keyword":"雷军"}
        crawler = SearchCrawler(**param)

        result = crawler.get_page_urls()

        print(json.dumps(result,ensure_ascii=False, indent=4))

    def test_sina_search(self):
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
            "max_count": 20
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
            "keyword": "小米"}
        crawler = SearchCrawler(**param)

        result = crawler.get_page_urls()

        print(json.dumps(result, ensure_ascii=False, indent=4))


if __name__ == '__main__':
    unittest.main()


