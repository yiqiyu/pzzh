# -*- coding: utf-8 -*-
__author__ = 'commissar'
from pz_download.handler.log import get_log
import unittest
import json
from pz_download.handler.select import SearchCrawler

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

        encode = 'utf8'

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

        print json.dumps(result,ensure_ascii=True, indent=4)


if __name__ == '__main__':
    unittest.main()


