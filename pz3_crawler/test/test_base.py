# -*- coding: utf-8 -*-

__author__ = 'commissar'

import unittest
import json
from pz_crawler.core.crawler import Crawler
from pz_crawler.core.parser import ParserRuleDb,UrlParserJudge,HtmlParserBase
from pz_crawler.tools.mongoutils import mongo
# from pz_download.handler.base import Crawler as
import pymongo


class TestParserHtml(unittest.TestCase):

    def setUp(self):
        self.mongo_connect = "mongodb://192.168.1.202:27017/"
        # self.mongo_user = "pzzh"
        # self.mongo_passwd = "pzzh123456"
        self.mongo_db = "crawler_rules"
        self.mc = mongo(self.mongo_connect).getclient(self.mongo_db)
        self.crawler = Crawler("","")
        self.mongo_client = pymongo.MongoClient(self.mongo_connect)
        self.db = self.mongo_client["crawler_rules"]

    def tearDown(self):
        print('I am tearDown')

    def test_read_datetime_from_mg(self):
        from dateutil import tz
        from dateutil.tz import tzlocal
        from datetime import datetime
        test_db = self.mongo_client['star_cloud']

        # UTC Zone
        from_zone = tz.gettz('UTC')

        # China Zone
        to_zone = tz.gettz('CST')
        utc = datetime.utcnow()

        # Tell the datetime object that it's in UTC time zone
        utc = utc.replace(tzinfo=from_zone)

        # Convert time zone
        local = utc.astimezone(to_zone)
        print(datetime.strftime(local, "%Y-%m-%d %H:%M:%S"))

        print(local)
        _id = "123"
        table = test_db["test"]
        table.remove({"_id":_id})
        table.insert({"_id":_id,"create_at":local})

        item = table.find_one({"_id":_id})
        create_at = item["create_at"]

        print(create_at)

        create_at = create_at.replace(tzinfo=from_zone)
        create_at = create_at.astimezone(to_zone)

        print(create_at)


    def __crawler_and_parser_from_db(self,url,type,header=None):
        code, content = self.crawler.content(url,header)

        if code == 200:

            # parser = HtmlParserBase(rule)
            judge = UrlParserJudge(self.db)
            parser = judge.test_parser(url,type)
            if parser:
                result = parser.parser(url,content)
                print(json.dumps(result,indent=4))
            else:
                print("judge.test is None")

        else:
            print(code,content)

    def __crawler_and_parser(self,url,rule,header=None):

        code , content = self.crawler.get(url,header)
        # if isinstance(content,unicode):
        #     content = content.encode("utf-8")
        if code== 200:

            parser = HtmlParserBase(rule)

            # judge = UrlParserJudge(self.mongo_connect,self.mongo_db)
            # parser = judge.test_parser(url,HtmlParserBase.TYPE_ARTICLE)

            # print content

            if parser:
                result = parser.parser(url, content)
                print(json.dumps(result, indent=4, ensure_ascii=False))
            else:
                print("judge.test is None")

        else:
            print(code, content)

    def test_init_rules(self):
        rule = {
            "domain": "1905.com",
            "type": "article",               # 其有两个值，article或comment
            "parse_rules":[
                {
                    "rule_uuid": "xxxx",                             # 这条匹配规则的ID，
                    "url_match":["^http[s]?://www.1905.com/news/[\d]{8}/[\d]*.",],        # [必填]url的适配正则表达式。其是或的关系，只有要有一个成功就代表当前页面可以抓取。
                    "title":[{"type": "xpath","express":'//h1','func':"text"},],     # 代表标题的获取方式，将依次执行后面的表达式，regex代表后面的表达式是一个正则表达式，xpath代表后面是一个路径获取。
                    "author":[{"type": "css",
                               "express": "div.pic-base>span.autor-name",
                               "func": "text"},
                              {"type": "regex",
                               "express": "：(.*?)$",
                               "func":'search',
                               "param": "1",
                              }],    # 代表作者
                    "origin_meida_name":[{
                        "type": "css",
                        "express": ".pic-source > .copyfrom",
                        "func": "text"
                    },],                       # 转载自,原始媒体名。
                    "origin_url":[{
                        "type": "css",
                        "express": ".pic-source > .copyfrom",
                        "func": "html"
                    },{
                        "type": "xpath",
                        "express": "//@href",
                        "func": ""
                    }],                            # 原始链接。
                    "content":[
                        {"type": "css",
                         "express": "div.pic-content > p",
                         "func": "html"
                         },
                    ],                            # [必填]内容
                    "publish_at":[{"type": "css",
                                   "express": ".pic-base > span:first-child",
                                   'func':"text"},
                                  {"type": "regex",
                                   "express": "[\d]{4}.[\d]{2}.[\d]{2}",
                                   "func":'search',
                                   "param": "0"}],    # 代表发布时间。
                    "tags":[{"type": "css",
                             "express": "div.rel-label > a",
                             "func": "text"
                             }],                                    # 文章原始Tag
                    # imgs:[],
                    # comment_num:[]
                    # like_num:[]
                    # dislike_num:[]
                    # filters:[]
                    # comments:{
                    #
                    # }
                }
            ]
        }


        db = ParserRuleDb(self.mongo_connect,self.mongo_db)
        db.add_parser_rule(rule,"parse_rules",HtmlParserBase.TYPE_ARTICLE)


    # def test_init_weibo_meida(self):
    #     rule = {
    #         "domain": "weibo.com",
    #         "type": "media",               # 其有两个值，article或comment
    #         "parse_py":[
    #             {
    #                 "rule_uuid": "xxxx",                             # 这条匹配规则的ID，
    #                 "url_match":["^http[s]?://weibo.com/u/[^/]+","^http[s]?://weibo.com/[^/]+"],
    #                 "modulepath": "pzcode.parserpy.weibomedia",
    #                 "class": "weibomedia",
    #                 "main": "main"
    #             }
    #         ]
    #     }
    #     url = 'http://weibo.com/645123577?is_all=1'
    #     parser = HtmlParserBase(rule)
    #
    #     # judge = UrlParserJudge(self.mongo_connect,self.mongo_db)
    #     # parser = judge.test_parser(url,HtmlParserBase.TYPE_ARTICLE)
    #     if parser:
    #         result = parser.parser(url,"")
    #         print json.dumps(result,indent=True,ensure_ascii=False)
    #     else:
    #         print "judge.test is None"
    #
    #
    #     db = ParserRuleDb(self.mongo_connect,self.mongo_db)
    #     db.add_parser_rule(rule,"parse_py",HtmlParserBase.TYPE_MEDIA)


    def test_init_yidian_meida(self):
        rule = {
            "domain":'yidianzixun.com',
            "type": "media",               # 其有两个值，article或comment
            "parse_py":[
                {
                    "rule_uuid": "xxxx",                             # 这条匹配规则的ID，
                    "url_match":["http[s]?://www.yidianzixun.com/home\?page=channel&id=m[\d]+"],
                    "modulepath": "pzcode.parserpy.yidianmedia",
                    "class": "yidianmedia",
                    "main": "main"
                }
            ]
        }

        db = ParserRuleDb(self.mongo_connect,self.mongo_db)
        db.add_parser_rule(rule,"parse_py",HtmlParserBase.TYPE_MEDIA)

    def test_init_yidian_art(self):
        rule = {
            "domain":'yidianzixun.com',
            "type": "article",               # 其有两个值，article或comment
            "parse_py":[
                {
                    "rule_uuid": "xxxx",                             # 这条匹配规则的ID，
                    "url_match":["http[s]?://www.yidianzixun.com/home\?page=article(.*)"],
                    "modulepath": "pzcode.parserpy.yidianmedia",
                    "class": "yidianmedia",
                    "main": "main_art"
                }
            ]
        }

        db = ParserRuleDb(self.mongo_connect, self.mongo_db)
        db.add_parser_rule(rule, "parse_py", HtmlParserBase.TYPE_ARTICLE)

    def test_1905_article_from_mongo(self):

        url = "http://www.1905.com/news/20161129/1133561.shtml"

        header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "www.1905.com",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36"
        }

        code, content = self.crawler.get(url, header)

        if code == 200:
            judge = UrlParserJudge(self.mc)
            parser = judge.test_parser(url, HtmlParserBase.TYPE_ARTICLE)
            if parser:
                result = parser.parser(url, content)
                print(json.dumps(result, indent=True))
            else:
                print("judge.test is None")

        else:
            print(content)

    def test_1905_article_debug(self):
        rule = {
            "domain": "1905.com",
            "type": "article",               # 其有两个值，article或comment
            "parse_rules": [            # 针对同一个域名下不同页面的分析规则列表，每个项目是一个字典t_rule
                {
                    "rule_uuid": "xxxx",                             # 这条匹配规则的ID，
                    "url_match":["^http[s]?://www.1905.com/news/[\d]{8}/[\d]*.",],        # [必填]url的适配正则表达式。其是或的关系，只有要有一个成功就代表当前页面可以抓取。
                    "title":[{"type": "xpath","express":'//h1','func':"text"},],     # 代表标题的获取方式，将依次执行后面的表达式，regex代表后面的表达式是一个正则表达式，xpath代表后面是一个路径获取。
                    "author":[{"type": "css",
                               "express": "div.pic-base>span.autor-name",
                               "func": "text"},
                              {"type": "regex",
                               "express": "：(.*?)$",
                               "func":'search',
                               "param": "1",
                              }],    # 代表作者
                    "origin_meida_name":[{
                        "type": "css",
                        "express": ".pic-source > .copyfrom",
                        "func": "text"
                    },],                       # 转载自,原始媒体名。
                    "origin_url":[{
                        "type": "css",
                        "express": ".pic-source > .copyfrom",
                        "func": "html"
                    },{
                        "type": "xpath",
                        "express": "//@href",
                        "func": ""
                    }],                            # 原始链接。
                    "content":[
                        {"type": "css",
                         "express": "div.pic-content > p",
                         "func": "html"
                         },
                    ],                            # [必填]内容
                    "publish_at":[{"type": "css",
                                   "express": ".pic-base > span:first-child",
                                   'func':"text"},
                                  {"type": "regex",
                                   "express": "[\d]{4}.[\d]{2}.[\d]{2}",
                                   "func":'search',
                                   "param": "0"}],    # 代表发布时间。
                    "tags":[{"type": "css",
                             "express": "div.rel-label > a",
                             "func": "text"
                             }],                                    # 文章原始Tag
                    # imgs:[],
                    # comment_num:[]
                    # like_num:[]
                    # dislike_num:[]
                    # filters:[]
                    # comments:{
                    #
                    # }
                }
            ]
        }

        url = "http://www.1905.com/news/20161129/1133561.shtml"

        header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "www.1905.com",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36"
        }

        code, content = self.crawler.get(url, header)

        if code == 200:

            parser = HtmlParserBase(rule)

            # judge = UrlParserJudge(self.mongo_connect,self.mongo_db)
            # parser = judge.test_parser(url,HtmlParserBase.TYPE_ARTICLE)
            if parser:
                result = parser.parser(url, content)
                print(json.dumps(result, indent=True, ensure_ascii=False))
            else:
                print("judge.test is None")

        else:
            print(code, content)

    def test_toutiao_article(self):
        rule = {
            "domain": "toutiao.com",
            "type": "media",               # 其有两个值，article或comment
            "parse_rules":[
                {
                    "rule_uuid": "xxxx",                             # 这条匹配规则的ID，
                    "url_match":["^http[s]?://(?:www.)?toutiao.com/(?:item|group)/[\d]*.",
                                 "^http[s]?://(?:www.)?toutiao.com/[ia][\d]*.",
                                 ],        # [必填]url的适配正则表达式。其是或的关系，只有要有一个成功就代表当前页面可以抓取。
                    "title":[{"type": "css","express":'h1.article-title','func':"text"},],     # 代表标题的获取方式，将依次执行后面的表达式，regex代表后面的表达式是一个正则表达式，xpath代表后面是一个路径获取。
                    "author":[{
                                  "type": "css",
                                    "express":'.src',
                                    "func": "text"
                              },{
                                    "type": "regex",
                                    "express": "[\s\r\t]",
                                    "func": "sub",
                                    "param": ""

                                }
                              ],    # 代表作者
                    "origin_meida_name":[
                        {
                                  "type": "css",
                                    "express":'.src',
                                    "func": "text"
                              },{
                                    "type": "regex",
                                    "express": "[\s\r\t]",
                                    "func": "sub",
                                    "param": ""

                                }
                              ],    # 媒体名。
                    "origin_url":[{
                        "type": "const",
                        "express": ""
                    }],       # 原始链接。

                    "content":[
                            {
                                "type": "css",
                                "express":'div# article-main > .article-content > *',
                                "func": "html",
                              }
                    ],                            # [必填]内容
                    "publish_at":[{"type": "regex",
                               "express": "class=\"time\">([\d]{4}-[\d]{1,2}-[\d]{1,2}\s[\d]{1,2}:[\d]{1,2})<",
                               "func": "search",
                               "param":1
                               }],    # 代表发布时间。
                    "tags":[{"type": "css",
                             "express": "a.label-link",
                             "func": "text"
                             }],                                    # 文章原始Tag

                    "media_home":[{
                        "type": "xpath",
                        "express": "//a[@class='pgc-link']/@href",
                        "func": ""
                    }],
                    "code":[{
                        "type": "xpath",
                        "express": "//a[@class='pgc-link']/@href",
                        "func": ""
                    },{
                        "type": "regex",
                        "express": "http://(?:www.)?toutiao.com/[m]([\d]*)",
                        'func':'search',
                        'param':1
                    }]
                    # imgs:[],
                }
            ]
        }

        url = "http://www.toutiao.com/i6366436759131128321/"

        self.__crawler_and_parser(url, rule)

        # db = ParserRuleDb(self.mongo_connect,self.mongo_db)
        # db.add_parser_rule(rule,HtmlParserBase.PARSE_RULES,HtmlParserBase.TYPE_ARTICLE)

        # self.__crawler_and_parser_from_db(url,HtmlParserBase.TYPE_ARTICLE)


    def test_toutiao_media(self):

        rule = {
            "domain": "toutiao.com",
            "type": "media",               # 其有两个值，article或comment
            "parse_rules":[
                {
                    "rule_uuid": "xxxx",                             # 这条匹配规则的ID，
                    "url_match":["^http[s]?://(?:www.)?toutiao.com/m(?:[\d]+)?/",],
                    "code": [{
                        "type":'regex',
                        "express": "media_id:\s(\d+)?,",
                        "func":'search',
                        "param": "1"
                    }],
                    "name": [{
                            "type":'regex',
                            "express": "name:\s'(\W+?)'",
                            "func":'search',
                            "param": "1"
                    }],
                    "unique_name":[
                        {
                            "type":'regex',
                            "express": "name:\s'(\W+?)'",
                            "func":'search',
                            "param": "1"
                        },
                        {
                            "type": "postfix",
                            "express": "toutiao.com:"
                        }
                    ],
                    "tags": [{
                        "type": "const",
                        "express":[
                            "_cat_new"
                        ],
                    }],
                    'url':[
                        {
                            "type":'regex',
                            "express": "media_id:\s(\d+)?,",
                            "func":'search',
                            "param": "1"
                        },{
                            "type": "postfix",
                            "express": "http://www.toutiao.com/m"
                        }
                    ],
                    "create_way": [{
                        "type": "const",
                        "express": "自媒体"
                    }],
                    "rank": [{
                        "type": "const",
                        "express":4
                    }],
                    "crawler": [{
                        "type": "const",
                        "express":{
                            "crawler_at": "1970-01-01 08:00:00",
                            "crawler_status": 1
                        }
                    }],
                    "platform": [{
                        "type": "const",
                        "express": {
                            "avater": "",
                            "platform_url": "",
                            "mid": "",
                            "name": ""
                        }
                    }],
                    "auth":[{
                        "type": "const",
                        "express": ""
                    }],
                    "hostname" : [{
                        "type": "const",
                        "express": "www.toutiao.com"
                    }],
                    "product_form":  [{
                        "type": "const",
                        "express": "新闻客户端"
                    }],
                    "avater": [
                        {
                            "type": "regex",
                            "express": "avartar_url:\s\'([^\']*)",
                            "func":'search',
                            "param": "1"
                        }
                    ],
                    "desc": [{
                        "type": "regex",
                        "express":'description:[\S\s]*?\"([^\"]*)\"',
                        "func":'search',
                        "param": "1"
                    }],
                    "channel": [{
                        "type": "const",
                        "express":[]
                    }],
                    "circulation_medium": [{
                        "type": "const",
                        "express": "移动互联网"
                    }]
                }
            ]
        }


        url = "http://www.toutiao.com/m50098085017/"

        # db = ParserRuleDb(self.mongo_connect,self.mongo_db)
        # db.add_parser_rule(rule,HtmlParserBase.PARSE_RULES,HtmlParserBase.TYPE_MEDIA)

        self.__crawler_and_parser(url,rule)

        # self.__crawler_and_parser_from_db(url,HtmlParserBase.TYPE_MEDIA)


    def test_huxiu_article(self):

        rule = {
            "domain": "huxiu.com",
            "type": "article",               # 其有两个值，article或comment
            "parse_rules":[
                {
                    "rule_uuid": "xxxx",                             # 这条匹配规则的ID，
                    "url_match":["^http[s]?://(?:www.)?huxiu.com/article/(?:[\d]*?).html$",
                                 "^http[s]?://(?:www.)?huxiu.com/article/(?:[\d]*?)/1.html$"
                                 ],        # [必填]url的适配正则表达式。其是或的关系，只有要有一个成功就代表当前页面可以抓取。
                    "title":[{"type": "css","express":'h1.t-h1','func':"text"},],     # 代表标题的获取方式，将依次执行后面的表达式，regex代表后面的表达式是一个正则表达式，xpath代表后面是一个路径获取。
                    "author":[{
                            "type": "css",
                            "express":'div.article-author > span.author-name > a',
                            "func": "text"
                    }],    # 代表作者
                    "origin_meida_name":[
                        {
                            "type": "css",
                            "express":'div.article-author > span.author-name > a',
                            "func": "text"
                        }],    # 媒体名。
                    "origin_url":[{
                        "type": "xpath",
                        "express": "//meta[@property='og:url']/@content",
                        "func": ""
                    }],       # 原始链接。
                    #
                    "content":[
                        {
                            "type": "xpath",
                            "express": "//div[@class='article-wrap']/div[@class='article-img-box']/img | //div[@class='article-wrap']/div[@id='article_content']/p | //div[@class='article-wrap']/div[@id='article_content']/blockquote",
                            "func": "html",
                        },{
                            "type": "regex",
                            "express": "<br/></p>",      # 将多个换行删除一个
                            "func": "sub",
                            "param": "</p>"
                        },{
                            "type": "regex",
                            "express": "<p/>",      # 将多个换行删除一个
                            "func": "sub",
                            "param": ""
                        }
                    ],                            # [必填]内容
                    "publish_at":[{"type": "css",
                               "express":'div.article-author > span.article-time',
                               "func": "text"
                               }],    # 代表发布时间。
                    "tags":[{"type": "css",
                             "express": "ul.transition li.transition",
                             "func": "text"
                             }],                                    # 文章原始Tag
                    "media_home":[{
                            "type": "xpath",
                            "express": "//div[@class='article-author']/span[@class='author-name']/a/@href",
                            "func": ""
                    },{
                        "type": "postfix",
                        "express": "https://www.huxiu.com"
                    }],
                    "code":[{
                            "type": "xpath",
                            "express": "//div[@class='article-author']/span[@class='author-name']/a/@href",
                            "func": ""
                    },{
                        "type": "regex",
                        "express": "/([\d]*)?.html",
                        'func':'search',
                        'param':1
                    }]
                    #  imgs:[],
                }
            ]
        }

        # url = "http://www.huxiu.com/article/175581.html"
        # url = "http://www.huxiu.com/article/157829.html"
        url = "http://www.huxiu.com/article/175695.html"

        header = {
              # "Expect": "100-continue",
              # 'Accept-Encoding':'gzip, deflate',
              # 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36',
              # 'Content-Type': 'application/x-www-form-urlencoded; charset=gbk',
              # 'Accept': ' */*',
              # 'Referer': url ,
              # 'X-Requested-With': 'XMLHttpRequest' ,
              # 'Cache-Control': 'max-age=0'
            }



        self.__crawler_and_parser(url,rule,header=header)


        # db = ParserRuleDb(self.mongo_connect,self.mongo_db)
        # db.add_parser_rule(rule,HtmlParserBase.PARSE_RULES,HtmlParserBase.TYPE_ARTICLE)

        # self.__crawler_and_parser_from_db(url,HtmlParserBase.TYPE_ARTICLE,header)

    def test_huxiu_media(self):

        rule = {
            "domain": "huxiu.com",
            "type": "media",               # 其有两个值，article或comment
            "parse_rules":[
                {
                    "rule_uuid": "xxxx",                             # 这条匹配规则的ID，
                    "url_match":["^http[s]?://(?:www.)?huxiu.com/member/(?:[\d]+)?\.html",],
                    "code": [{
                        "type":'xpath',
                        "express": "//div[@class='user-head-box']/a/@uid",
                        "func":''
                    }],
                    "name": [{
                        "type":'xpath',
                        "express": "//div[@class='user-head-box']/a/@name",
                        "func":''
                    }],
                    "unique_name":[
                        {
                            "type":'xpath',
                            "express": "//div[@class='user-head-box']/a/@name",
                            "func":''
                        },
                        {
                            "type": "postfix",
                            "express": "huxiu.com:"
                        }
                    ],
                    "tags": [{
                        "type": "const",
                        "express":[
                            "_cat_new"
                        ],
                    }],
                    'url':[
                        {
                            "type":'xpath',
                            "express": "//div[@class='user-head-box']/a/@uid",
                            "func":''
                        },{
                            "type": "postfix",
                            "express": "https://www.huxiu.com/member/"
                        },{
                            "type": "prefix",
                            "express": ".html"
                        }
                    ],
                    "create_way": [{
                        "type": "const",
                        "express":u"自媒体"
                    }],
                    "rank": [{
                        "type": "const",
                        "express":4
                    }],
                    "crawler": [{
                        "type": "const",
                        "express":{
                            "crawler_at": "1970-01-01 08:00:00",
                            "crawler_status": 1
                        }
                    }],
                    "platform": [{
                        "type": "const",
                        "express": {
                            "avater": "",
                            "platform_url": "",
                            "mid": "",
                            "name": ""
                        }
                    }],
                    "auth":[{
                        "type": "const",
                        "express": ""
                    }],
                    "hostname" : [{
                        "type": "const",
                        "express": "www.huxiu.com"
                    }],
                    "product_form":  [{
                        "type": "const",
                        "express":u"新闻客户端"
                    }],
                    "avater": [
                        {
                            "type": "xpath",
                            "express": "//div[@class='user-face']/img/@src",
                            "func":''
                        }
                    ],
                    "desc": [{
                        "type": "xpath",
                        "express": "//div[@class='user-info-box']/div[@class='col-lg-5']/div[@class='user-info'][2]",
                        "func":'html',
                    },{
                        "type": "regex",
                        "express": "[\s\n<a-z\-\=\">\/]",
                        "func":'sub',
                        "param": ""
                    }],
                    "channel": [{
                        "type": "const",
                        "express":[]
                    }],
                    "circulation_medium": [{
                        "type": "const",
                        "express":u"移动互联网"
                    }]
                }
            ]
        }

        header = {
              # "Expect": "100-continue",
              # 'Accept-Encoding':'gzip, deflate',
              # 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36',
              # 'Content-Type': 'application/x-www-form-urlencoded; charset=gbk',
              # 'Accept': ' */*',
              # 'Referer': url ,
              # 'X-Requested-With': 'XMLHttpRequest' ,
              # 'Cache-Control': 'max-age=0'
            }

        url = "https://www.huxiu.com/member/322384.html"

        # db = ParserRuleDb(self.mongo_connect,self.mongo_db)
        # db.add_parser_rule(rule,HtmlParserBase.PARSE_RULES,HtmlParserBase.TYPE_MEDIA)

        self.__crawler_and_parser(url,rule,header)

        # self.__crawler_and_parser_from_db(url,HtmlParserBase.TYPE_MEDIA,header)


    def test_leiphone_article(self):

        url = "http://www.leiphone.com/latest/index/id/3721"
        url = "http://www.leiphone.com/news/201612/09HecjzLRdGX3r81.html"

        rule = {
            "domain": "leiphone.com",
            "type": "article",               # 其有两个值，article或comment
            "parse_rules":[
                {   #http://www.leiphone.com/news/201612/09HecjzLRdGX3r81.html
                    "rule_uuid": "xxxx",                             # 这条匹配规则的ID，
                    "url_match":["^http[s]?://(?:www.)?leiphone.com/latest/index/id/(?:[\d]+?)$",
                                 "^http[s]?://(?:www.)?leiphone.com/news/(?:[\d]+?)/(?:[\S]+?).html$"
                                 ],        # [必填]url的适配正则表达式。其是或的关系，只有要有一个成功就代表当前页面可以抓取。
                    "title":[
                        {"type": "css","express":'div.article-title h1','func':"text"},
                        {
                            "type": "regex",
                            "express": "[\n\s]",
                            "func":'sub',
                            "param": ""
                        }
                             ],     # 代表标题的获取方式，将依次执行后面的表达式，regex代表后面的表达式是一个正则表达式，xpath代表后面是一个路径获取。
                    "author":[{
                            "type": "xpath",
                            "express":'//meta[@property="article:author"]/@content',
                            "func": ""
                    }],    # 代表作者
                    "origin_meida_name":[
                        {
                            "type": "xpath",
                            "express":'//meta[@property="article:author"]/@content',
                            "func": ""
                        }],    # 媒体名。
                    "origin_url":[{
                        "type": "const",
                        "express": "",
                    }],       # 原始链接。
                    #
                    "content":[
                        {
                            "type": "css",
                            "express": "div.lph-article-comview > *",
                            "func": "html",
                        }
                    ],                            # [必填]内容
                    "publish_at":[{
                            "type": "css",
                            "express":'div.msg td.time',
                            "func": "text"
                        },{
                        "type": "regex",
                        "express": "[\s]{2}",
                        "func": "sub",
                        "param": ""
                    },{
                        "type": "regex",
                        "express": "^\s",
                        "func": "sub",
                        "param": ""
                    }],    # 代表发布时间。
                    "tags":[{"type": "css",
                             "express": "div.related-link > a",
                             "func": "text"
                             }],                                    #文章原始Tag
                    "media_home":[{
                            "type": "xpath",
                            "express": "//td[@class='aut']/a/@href",
                            "func": ""
                    }],
                    "code":[{
                            "type": "regex",
                            "express": "var\sauthor_id[\s]+?=[^\d]+([\d]+?)[^\d]",
                            "func": "search",
                            "param":1
                    }]
                    # imgs:[],
                }
            ]
        }
        # url = "http://www.leiphone.com/latest/index/id/3721"
        url = "http://www.leiphone.com/news/201612/09HecjzLRdGX3r81.html"

        header = {
              # "Expect": "100-continue",
              # 'Accept-Encoding':'gzip, deflate',
              # 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36',
              # 'Content-Type': 'application/x-www-form-urlencoded; charset=gbk',
              # 'Accept': ' */*',
              # 'Referer': url ,
              # 'X-Requested-With': 'XMLHttpRequest' ,
              # 'Cache-Control': 'max-age=0'
            }



        self.__crawler_and_parser(url,rule,header=header)

        #
        # db = ParserRuleDb(self.mongo_connect,self.mongo_db)
        # db.add_parser_rule(rule,HtmlParserBase.PARSE_RULES,HtmlParserBase.TYPE_ARTICLE)

        # self.__crawler_and_parser_from_db(url,HtmlParserBase.TYPE_ARTICLE,header)

    def test_leiphone_media(self):

        rule = {
            "domain": "leiphone.com",
            "type": "media",               # 其有两个值，article或comment
            "parse_rules":[
                {
                    "rule_uuid": "xxxx",                             # 这条匹配规则的ID，
                    "url_match":["^http[s]?://(?:www.)?leiphone.com/author/(?:[\S]+?)$",],
                    "code": [{
                            "type": "regex",
                            "express": "var\sauthor_id[\s]+?=[^\d]+([\d]+?)[^\d]",
                            "func": "search",
                            "param":1
                    }],
                    "name": [{
                        "type":'css',
                        "express": "div.lphauthor-main div.name",
                        "func":'text'
                    }],
                    "unique_name":[{
                        "type":'css',
                        "express": "div.lphauthor-main div.name",
                        "func":'text'
                        },
                        {
                            "type": "postfix",
                            "express": "leiphone.com:"
                        }
                    ],
                    "tags": [{
                        "type": "const",
                        "express":[
                            "_cat_new"
                        ],
                    }],
                    'url':[
                        {
                            "type":'css',
                            "express": "div.lphauthor-main div.name",
                            "func":'text'
                        },{
                            "type": "postfix",
                            "express": "https://www.leiphone.com/author/"
                        }
                    ],
                    "create_way": [{
                        "type": "const",
                        "express":u"自媒体"
                    }],
                    "rank": [{
                        "type": "const",
                        "express":4
                    }],
                    "crawler": [{
                        "type": "const",
                        "express":{
                            "crawler_at": "1970-01-01 08:00:00",
                            "crawler_status": 1
                        }
                    }],
                    "platform": [{
                        "type": "const",
                        "express": {
                            "avater": "",
                            "platform_url": "",
                            "mid": "",
                            "name": ""
                        }
                    }],
                    "auth":[{
                        "type": "css",
                        "express": "div.jobtit",
                        "func": "text"
                    },{
                        "type": "regex",
                        "express": "[\n\s]",
                        "func":'sub',
                        "param": ""
                    }],
                    "hostname" : [{
                        "type": "const",
                        "express": "www.leiphone.com"
                    }],
                    "product_form":  [{
                        "type": "const",
                        "express":u"新闻客户端"
                    }],
                    "avater": [
                        {
                            "type": "xpath",
                            "express": "//div[@class='avater']/img/@src",
                            "func":''
                        }
                    ],
                    "desc": [{
                        "type": "css",
                        "express": "div.author-right div.des",
                        "func":'text',
                    },{
                            "type": "regex",
                            "express": "[\n\s]",
                            "func":'sub',
                            "param": ""
                        }],
                    "channel": [{
                        "type": "const",
                        "express":[]
                    }],
                    "circulation_medium": [{
                        "type": "const",
                        "express":u"移动互联网"
                    }]
                }
            ]
        }

        header = {
              # "Expect": "100-continue",
              # 'Accept-Encoding':'gzip, deflate',
              # 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36',
              # 'Content-Type': 'application/x-www-form-urlencoded; charset=gbk',
              # 'Accept': ' */*',
              # 'Referer': url ,
              # 'X-Requested-With': 'XMLHttpRequest' ,
              # 'Cache-Control': 'max-age=0'
            }

        url = u"http://www.leiphone.com/author/于欣烈"
        url = "http://www.leiphone.com/author/niu2208"

        # db = ParserRuleDb(self.mongo_connect,self.mongo_db)
        # db.add_parser_rule(rule,HtmlParserBase.PARSE_RULES,HtmlParserBase.TYPE_MEDIA)

        self.__crawler_and_parser(url,rule,header)

        # self.__crawler_and_parser_from_db(url,HtmlParserBase.TYPE_MEDIA,header)

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

        url = "http://api.search.sina.com.cn/?c=news&t=&q=%E5%BC%A0%E5%AD%A6%E5%8F%8B%E8%A2%AB%E5%96%8A%E5%88%98%E5%BE%B7%E5%8D%8E&pf=2130835692&ps=2130770162&page=1&stime=2016-04-09&etime=2017-04-11&sort=rel&highlight=1&num=10&ie=utf-8&callback=&_=1491802690533"

        rule = {
            "domain": "sina.com.cn",
            "type": "search",
            "parse_py": [
                {
                    "rule_uuid": "xxxx",  # 这条匹配规则的ID，
                    "url_match": ["^http[s]?://api.search.sina.com.cn/\?.", ],
                    "modulepath": "pz_crawler.parse_py.sina_search",  # python类的命名空间
                    "class": "sina_search",
                    "function": "main"
                }
            ],
            "item": [
                {
                    "name": "default",
                    "url_template": [
                        "^http[s]?://tieba.baidu.com/f/search/res?"
                    ],
                    "end_rule": [ ],
                    "header": {
                        'Accept': '*/*',
                        'Accept-Encoding': 'gzip, deflate, sdch',
                        'Accept-Language': 'zh-CN,zh;q=0.8',
                        'Connection': 'keep-alive',
                        'Host': 'api.search.sina.com.cn',
                        'Referer': 'http://www.sina.com.cn/mid/search.shtml?q=%E4%B8%96%E7%95%8C%E6%9C%80%E5%A4%A7%E9%87%91%E5%B8%81%E8%A2%AB%E5%81%B7',
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36'
                    },
                    "cookie" : "UOR=www.baidu.com,www.sina.com.cn,; SINAGLOBAL=183.48.243.58_1490754786.942741; Apache=183.48.243.58_1490754787.200075; SGUID=1490754787485_59067253; vjuids=5e96c53d.15b17e8d9f5.0.50f26de15aba2; ULV=1490754788074:2:2:2:183.48.243.58_1490754787.200075:1490754787350; SUB=_2AkMvh5I2f8NhqwJRmP4Qz2LraIRzyArEieKZ22PtJRMyHRl-yD83qlEbtRDDSXejvLr3SNFBJccNeVcArgPyKw..; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WW.hF-G5Bgv.pNR0ra1PneR; U_TRS1=0000003a.2ada593e.58db1d2a.f45e7918; U_TRS2=0000003a.2aec593e.58db1d2a.235df27e; WEB2_OTHER=86b3c3bb2c3b4f93e9d072c16c59cb0f; SessionID=b7mqeo3i1thp0dt3f2cil3kdi7; lxlrtst=1491548881_o; ArtiFSize=14; rotatecount=2; vjlast=1491802683; lxlrttp=1491745006",
                    "url_type" : "search",
                    "encode" : "gbk",
                    "url_build_rule" : {
                        "param" : {
                            "key_type" : "_tbk_",
                            "keyword" : {
                                "encode": "gbk",
                                "quote": "true"
                            }
                        },
                    }
                }
            ],
        }
        self.__crawler_and_parser(url, rule, header)

    def test_ent_sina_article(self):
        url = "http://ent.sina.com.cn/zl/discuss/2017-04-10/doc-ifyeceza1837231.shtml"
        header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            "Cache - Control": "max - age = 0",
            'Connection': 'keep-alive',
            'Host': 'ent.sina.com.cn',
            'Referer': 'http://www.sina.com.cn/mid/search.shtml?q=%E5%BC%A0%E5%AD%A6%E5%8F%8B%E8%A2%AB%E5%96%8A%E5%88%98%E5%BE%B7%E5%8D%8E',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
            'Upgrade - Insecure - Requests': '1'
        }

        rule = {
            "domain": "ent.sina.com.cn",
            "type": "article",  # 其有两个值，article或comment
            "parse_rules": [
                {
                    "rule_uuid": "xxxx",  # 这条匹配规则的ID，
                    "url_match": [r"^http[s]?://ent.sina.com.cn/.+?/\d{4}-\d{2}-\d{2}/.*?\d{1,10}.shtml$", ],
                    "title": [{"type": "xpath", "express": '//h1', 'func': "text"}, ],
                # 代表标题的获取方式，将依次执行后面的表达式，regex代表后面的表达式是一个正则表达式，xpath代表后面是一个路径获取。
                    "author": [{"type": "xpath", "express": "//*[@id='author_ename']/a", "func": "text"},],  # 代表作者
                    "origin_meida_name": [{"type": "xpath", "express": "//*[@id='J_Article_Wrap']/div[1]/div[1]/div[1]/a[1]", "func": "text"}, ],
                # 转载自,原始媒体名。
                    "origin_url": [{"type": "css", "express": ".pic-source > .copyfrom", "func": "html"},
                                   {"type": "xpath", "express": "//@href", "func": ""}],  # 原始链接。
                    "content": [{"type": "xpath", "express": "//*[@id='artibody']", "func": "html"}, ],  # [必填]内容
                    "publish_at": [{"type": "xpath", "express": "//*[@id='pub_date']", 'func': "text"},
                                   {"type": "regex", "express": "[\d]{4}.[\d]{2}.[\d]{2}.", "func": 'search',
                                    "param": "0"}],  # 代表发布时间。//*[@id="page-tools"]/span/span[1]
                    "tags": [{"type": "css", "express": ".art_keywords a", "func": "text"},
                             ],  # 文章原始Tag
                    # imgs:[],
                    # comment_num:[]
                    # like_num:[]
                    # dislike_num:[]
                    # filters:[]
                    # comments:{
                    #
                    # }
                }
            ]
        }
        self.__crawler_and_parser(url, rule, header)

    def test_news_sina_article(self):
        url = "http://news.sina.com.cn/o/2017-04-10/doc-ifyeayzu7379575.shtml"
        url= "http://news.sina.com.cn/china/xlxw/2017-04-09/doc-ifyeceza1697491.shtml"
        header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            "Cache - Control": "max - age = 0",
            'Connection': 'keep-alive',
            'Host': 'news.sina.com.cn',
            'Referer': 'http://gov.sina.com.cn/',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
            'Upgrade - Insecure - Requests': '1'
        }
        rule = {
            "domain": "news.sina.com.cn",
            "type": "article",  # 其有两个值，article或comment
            "parse_rules": [
                {
                    "rule_uuid": "xxxx",  # 这条匹配规则的ID，
                    "url_match": [r"^http[s]?://news.sina.com.cn/.+?/\d{4}-\d{2}-\d{2}/.*?\d{1,10}.shtml$", ],
                    "title": [{"type": "xpath", "express": '//h1', 'func': "text"}, ],
                    # 代表标题的获取方式，将依次执行后面的表达式，regex代表后面的表达式是一个正则表达式，xpath代表后面是一个路径获取。
                    "author": [{"type": "xpath", "express": "//*[@id='author_ename']/a", "func": "text"}, ],  # 代表作者
                    "origin_meida_name": [
                        {"type": "css", "express": ".time-source > span > span > a",
                         "func": "text"}, ],
                    # # 转载自,原始媒体名。
                    "origin_url": [{"type": "css", "express": ".time-source > span > span > a",
                                    "func": "html"},
                                   {"type": "xpath", "express": "//@href", "func": ""}
                                   ],  # 原始链接。
                    "content": [{"type": "xpath", "express": "//*[@id='artibody']", "func": "html"}, ],  # [必填]内容
                    "publish_at": [{"type": "css", "express": ".time-source", 'func': "text"},
                                   {"type": "regex", "express": "[\d]{4}.[\d]{2}.[\d]{2}.", "func": 'search',
                                    "param": "0"}],  # 代表发布时间。//*[@id="page-tools"]/span/span[1]
                    "tags": [{"type": "css", "express": ".article-keywords a", "func": "text"},
                             ],  # 文章原始Tag
                    "imgs":[{"type": "css", "express": "#artibody img", "func": "html"},
                            {"type": "xpath", "express": "//@src", "func": ""}],
                    # "comment_num":[{"type": "xpath", "express": "//*[@id='commentCount1']", "func": "text"}]
                    # like_num:[]
                    # dislike_num:[]
                    # filters:[]
                    # comments:{
                    #
                    # }
                }
            ]
        }
        self.__crawler_and_parser(url, rule, header)

    def test_tech_sina_article(self):
        url = "http://tech.sina.com.cn/i/2017-04-10/doc-ifyecezv2933520.shtml"
        # url= "http://tech.sina.com.cn/it/2017-04-10/doc-ifyeceza1914635.shtml"
        header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            "Cache - Control": "max - age = 0",
            'Connection': 'keep-alive',
            'Host': 'tech.sina.com.cn',
            'Referer': 'http://tech.sina.com.cn/',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
            'Upgrade - Insecure - Requests': '1'
        }
        rule = {
            "domain": "tech.sina.com.cn",
            "type": "article",  # 其有两个值，article或comment
            "parse_rules": [
                {
                    "rule_uuid": "xxxx",  # 这条匹配规则的ID，
                    "url_match": [r"^http[s]?://tech.sina.com.cn/^(/zl/).+?/\d{4}-\d{2}-\d{2}/.*?\d{1,10}.shtml$", ],
                    "title": [{"type": "xpath", "express": '//h1', 'func': "text"}, ],
                    # 代表标题的获取方式，将依次执行后面的表达式，regex代表后面的表达式是一个正则表达式，xpath代表后面是一个路径获取。
                    "author": [{"type": "xpath", "express": "//*[@id='author_ename']/a", "func": "text"}, ],  # 代表作者
                    "origin_meida_name": [
                        {"type": "css", "express": "#media_name > a.ent1.fred",
                         "func": "text"}, ],
                    # # 转载自,原始媒体名。
                    "origin_url": [{"type": "css", "express": "#media_name > a.ent1.fred",
                                    "func": "html"},
                                   {"type": "xpath", "express": "//@href", "func": ""}
                                   ],  # 原始链接。
                    "content": [{"type": "xpath", "express": "//*[@id='artibody']", "func": "html"}, ],  # [必填]内容
                    "publish_at": [{"type": "css", "express": "#page-tools > span > span.titer", 'func': "text"},
                                   {"type": "regex", "express": "[\d]{4}.[\d]{2}.[\d]{2}.", "func": 'search',
                                    "param": "0"}],  # 代表发布时间。//*[@id="page-tools"]/span/span[1]
                    "tags": [{"type": "css", "express": ".art_keywords a", "func": "text"},
                             ],  # 文章原始Tag
                    "imgs":[{"type": "css", "express": "#artibody img", "func": "html"},
                            {"type": "xpath", "express": "//@src", "func": ""}],
                    # "comment_num":[{"type": "xpath", "express": "//*[@id='commentCount1']", "func": "text"}]
                    # like_num:[]
                    # dislike_num:[]
                    # filters:[]
                    # comments:{
                    #
                    # }
                }
            ]
        }
        self.__crawler_and_parser(url, rule, header)

        def test_tech_sina_column_article(self):
            url = "http://tech.sina.com.cn/i/2017-04-10/doc-ifyecezv2933520.shtml"
            # url= "http://tech.sina.com.cn/it/2017-04-10/doc-ifyeceza1914635.shtml"
            header = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                "Cache - Control": "max - age = 0",
                'Connection': 'keep-alive',
                'Host': 'tech.sina.com.cn',
                'Referer': 'http://tech.sina.com.cn/',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
                'Upgrade - Insecure - Requests': '1'
            }
            rule = {
                "domain": "tech.sina.com.cn",
                "type": "article",  # 其有两个值，article或comment
                "parse_rules": [
                    {
                        "rule_uuid": "xxxx",  # 这条匹配规则的ID，
                        "url_match": [r"^http[s]?://tech.sina.com.cn/zl/.+?/\d{4}-\d{2}-\d{2}/.*?\d{1,10}.shtml$", ],
                        "title": [{"type": "xpath", "express": '//h1', 'func': "text"}, ],
                        # 代表标题的获取方式，将依次执行后面的表达式，regex代表后面的表达式是一个正则表达式，xpath代表后面是一个路径获取。
                        "author": [{"type": "xpath", "express": "//*[@id='author_ename']/a", "func": "text"}, ],  # 代表作者
                        "origin_meida_name": [
                            {"type": "css", "express": "#media_name > a.ent1.fred",
                             "func": "text"}, ],
                        # # 转载自,原始媒体名。
                        "origin_url": [{"type": "css", "express": "#media_name > a.ent1.fred",
                                        "func": "html"},
                                       {"type": "xpath", "express": "//@href", "func": ""}
                                       ],  # 原始链接。
                        "content": [{"type": "xpath", "express": "//*[@id='artibody']", "func": "html"}, ],  # [必填]内容
                        "publish_at": [{"type": "css", "express": "#page-tools > span > span.titer", 'func': "text"},
                                       {"type": "regex", "express": "[\d]{4}.[\d]{2}.[\d]{2}.", "func": 'search',
                                        "param": "0"}],  # 代表发布时间。//*[@id="page-tools"]/span/span[1]
                        "tags": [{"type": "css", "express": ".art_keywords a", "func": "text"},
                                 ],  # 文章原始Tag
                        "imgs": [{"type": "css", "express": "#artibody img", "func": "html"},
                                 {"type": "xpath", "express": "//@src", "func": ""}],
                        # "comment_num":[{"type": "xpath", "express": "//*[@id='commentCount1']", "func": "text"}]
                        # like_num:[]
                        # dislike_num:[]
                        # filters:[]
                        # comments:{
                        #
                        # }
                    }
                ]
            }
            self.__crawler_and_parser(url, rule, header)