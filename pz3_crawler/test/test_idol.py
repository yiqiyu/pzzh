# -*- coding: utf-8 -*-

__author__ = 'commissar'

import json
from pzcode.mongocrawler.test_base import TestClass

from pz_download.handler.select import SearchCrawler

class TestIdol(TestClass):

    def setUp(self):
        self.header = {
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding":"gzip, deflate, sdch",
            "Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6",
            "Cache-Control":"max-age=0",
            "Connection":"keep-alive",
            "Host":"idol001.com",
            "Upgrade-Insecure-Requests":"1",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36"
        }

    def test_list(self):
        url = "https://idol001.com/news/zhangjie/list/1/"

        end_cond = {
            "max_count":20,
        }
        encode = 'utf8'

        header = {
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding":"gzip, deflate, sdch",
            "Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6",
            "Cache-Control":"max-age=0",
            "Connection":"keep-alive",
            "Host":"idol001.com",
            "Upgrade-Insecure-Requests":"1",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36"
        }

        parse_rule = {
            "domain":"idol001.com",
            "type":"search",               #其有两个值，article或comment
            "parse_rules":[
                {
                    "url_match": [
                    "^http[s]?://idol001.com/news/(?:[^/]+)/list/"
                ],
                "rule_uuid": "",
                "search_items": {
                    "property": {

                        "media_name": [{
                                "type":"const",
                                "express":"爱豆网"
                            }],
                        "title": [
                            {
                                "express": "//a[@class='amask']/@title",
                                "type": "xpath",
                                "func": ""
                            },
                            # {
                            #     "express": ">([\\S\\s\\w]+)?<\\/a>",
                            #     "type": "regex",
                            #     "param": 1,
                            #     "func": "search"
                            # }
                        ],
                        "url": [
                            {
                                "express": "//a[@class='amask']/@href",
                                "type": "xpath",
                                "func": ""
                            },
                            {
                                "express": "https://idol001.com",
                                "type": "postfix"
                            }
                        ],
                        "create_at": [
                            {
                                "express": "span.news-time",
                                "type": "css",
                                "func": "text"
                            },{
                                "type":"regex",
                                "express":"[\s\r\t]",
                                "func":"sub",
                                "param":""

                            }
                        ],
                #         "channel": [
                #             {
                #                 "express": "//font[@class='p_violet'][1]",
                #                 "type": "xpath",
                #                 "func": "text"
                #             }
                #         ],
                #         "media_url": [
                #             {
                #                 "express": "//font[@class='p_violet'][2]/../@href",
                #                 "type": "xpath",
                #                 "func": ""
                #             },
                #             {
                #                 "express": "http://tieba.baidu.com",
                #                 "type": "postfix"
                #             }
                #         ]
                    },
                    "express": [
                        {
                            "express": "ul.card-news-list > li",
                            "type": "css",
                            "func": "html"
                        }
                    ]
                },
                "cur_page_num": [
                    {
                        "express": "li.cur > a",
                        "type": "css",
                        "func": "text"
                    }
                ],
                "next_url": [
                    {
                        "express": "//a[@class='next']/@href",
                        "type": "xpath",
                        "func": ""
                    },
                    {
                        "express": "https://idol001.com",
                        "type": "postfix"
                    }
                #     {
                #         "express": "href=[\"']([^\"']+?)[\"']",
                #         "type": "regex",
                #         "param": 1,
                #         "func": "search"
                #     },
                #     {
                #         "express": "http://tieba.baidu.com",
                #         "type": "postfix"
                #     },
                #     {
                #         "express": "",
                #         "type": "other",
                #         "func": "unescape"
                #     }
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
            "keyword":"张杰"}
        crawler = SearchCrawler(**param)

        result = crawler.get_page_urls()

        print json.dumps(result,ensure_ascii=False, indent=4)


    def test_news(self):
        url = "https://idol001.com/news/luhan/detail/58d03ccd7a117315428b45a3/"

        rule = {
            "domain":"idol001.com",
            "type":"article",               #其有两个值，article或comment
            "parse_rules":[
                {
                    "rule_uuid":"xxxx",                             #这条匹配规则的ID，
                    "url_match":["^http[s]?://(?:www.)?idol001.com/news/(?:[^/]+)/detail/[\S]*",
                                 ],        #[必填]url的适配正则表达式。其是或的关系，只有要有一个成功就代表当前页面可以抓取。
                    "title":[{"type":"css","express":'h1.news-title','func':"text"},],     #代表标题的获取方式，将依次执行后面的表达式，regex代表后面的表达式是一个正则表达式，xpath代表后面是一个路径获取。
                    "author":[{
                                "type":"xpath",
                                "express":"//div[@class='news-info clearfix']/span[2]",
                                "func":"text"
                              },{
                                    "type":"regex",
                                    "express":u"来源：",
                                    "func":"sub",
                                    "param":""
                                }
                              ],    #代表作者
                    # "origin_meida_name":[
                    #     {
                    #               "type":"css",
                    #                 "express":'.src',
                    #                 "func":"text"
                    #           },{
                    #                 "type":"regex",
                    #                 "express":"[\s\r\t]",
                    #                 "func":"sub",
                    #                 "param":""
                    #
                    #             }
                    #           ],    #媒体名。
                    # "origin_url":[{
                    #     "type":"const",
                    #     "express":""
                    # }],       #原始链接。
                    #
                    "content":[
                            {
                                "type":"css",
                                "express":'div.article-detail > p',
                                "func":"html",
                              }
                    ],                            #[必填]内容
                    "publish_at":[{
                                "type":"xpath",
                                "express":"//div[@class='news-info clearfix']/span[1]",
                                "func":"text"
                              }],    #代表发布时间。
                    "reader":[      #阅读数
                        {
                            "type":"xpath",
                            "express":"//div[@class='news-info clearfix']/span[3]",
                            "func":"text"
                        },{
                            "type":"regex",
                            "express":"([\d]*)",
                            "func":"search",
                            "param":1
                        }
                    ],
                    # "tags":[{"type":"css",
                    #          "express":"a.label-link",
                    #          "func":"text"
                    #          }],                                    #文章原始Tag
                    #
                    # "media_home":[{
                    #     "type":"xpath",
                    #     "express":"//a[@class='pgc-link']/@href",
                    #     "func":""
                    # }],
                    # "code":[{
                    #     "type":"xpath",
                    #     "express":"//a[@class='pgc-link']/@href",
                    #     "func":""
                    # },{
                    #     "type":"regex",
                    #     "express":"http://(?:www.)?toutiao.com/[m]([\d]*)",
                    #     'func':'search',
                    #     'param':1
                    # }]
                    "imgs":[
                        {
                            "type":"xpath",
                            "express":"//div[@class='article-detail']/p/img/@src",
                            "func":"",
                        }
                    ],
                }
            ]
        }

        self.crawler_and_parser(url,rule=rule,type="article",header=self.header)