import pymongo
from pz3_crawler.test.test_base import TestClass
from pz3_crawler.core.crawler_conf import CrawlerConf, CrawlerConfItem
from pz3_crawler.core.search_crawler import SearchCrawler
from pz3_crawler.core.parser import HtmlParserBase, UrlParserJudge, ParserRuleDb
from pz3_crawler.core.crawler_mgr import CrawlerMgr

import tldextract
from pz3_crawler.conf.setting import log


class TestSina(TestClass):
    def setUp(self):
        self.crawler_rule_db_name = "crawler_rules"
        self.mongo_connect = "mongodb://localhost:27017/"
        self.mongo_client = pymongo.MongoClient(self.mongo_connect)
        self.db = self.mongo_client[self.crawler_rule_db_name]
        self.crawler_mgr = CrawlerMgr(self.db)

    def sina_list_crawler(self, key):
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

    def _insert(self):
        confs = [
            {
            "domain": "sina.com.cn",
            "item": [
                {
                    "cookie": "",
                    "encode": "utf-8",
                    "type": "Crawler",
                    "end_rule": [],
                    "header": {
                        'Accept': '*/*',
                        'Accept-Encoding': 'gzip, deflate, sdch',
                        'Accept-Language': 'zh-CN,zh;q=0.8',
                        'Connection': 'keep-alive',
                        'Host': 'api.search.sina.com.cn',
                        'Referer': 'http://www.sina.com.cn',
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36'
                    },
                    "name": "sina_search",
                    "url_build_rule": {
                        "param": {
                            "key_type": "_snk_",
                            "keyword": {
                                "encode": "gbk",
                                "quote": "true"
                            }
                        },
                        "template": "http://api.search.sina.com.cn/?c=news&q={keyword}&sort=rel&highlight=1&num=10&ie=utf-8&callback=&_=1491985965509"
                    },
                    "url_template": [
                        "^http[s]?://api.search.sina.com.cn/\?"
                    ],
                    "url_type": "search"
                }
            ],
            "url_type": "search"
            },
            {
                "domain": "ent.sina.com.cn",
                "item": [
                    {
                        "cookie": "",
                        "encode": "utf-8",
                        "end_rule": ["id='artibody'"],
                        "type": "Crawler",
                        "header": {
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Encoding': 'gzip, deflate, sdch',
                            'Accept-Language': 'zh-CN,zh;q=0.8',
                            "Cache - Control": "max - age = 0",
                            'Connection': 'keep-alive',
                            'Host': 'ent.sina.com.cn',
                            'Referer': 'http://www.sina.com.cn/mid/search.shtml?q=%E5%BC%A0%E5%AD%A6%E5%8F%8B%E8%A2%AB%E5%96%8A%E5%88%98%E5%BE%B7%E5%8D%8E',
                            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
                            'Upgrade - Insecure - Requests': '1'
                        },
                        "url_template": [r"^http[s]?://ent.sina.com.cn/zl/.+?/\d{4}-\d{2}-\d{2}/.*?\d{1,10}.shtml$", ],
                        "url_type": "aritcle"
                    }
                ],
                "url_type": "aritcle"
            },
            {
                "domain": "ent.sina.com.cn",
                "item": [
                    {
                        "cookie": "",
                        "encode": "utf-8",
                        "end_rule": ["id='artibody'"],
                        "type": "Crawler",
                        "header": {
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Encoding': 'gzip, deflate, sdch',
                            'Accept-Language': 'zh-CN,zh;q=0.8',
                            "Cache - Control": "max - age = 0",
                            'Connection': 'keep-alive',
                            'Host': 'ent.sina.com.cn',
                            'Referer': 'http://ent.sina.com.cn/',
                            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
                            'Upgrade - Insecure - Requests': '1'
                        },
                        "url_template": [r"^http[s]?://ent.sina.com.cn/.+?/\d{4}-\d{2}-\d{2}/.*?\d{1,10}.shtml$", ],
                        "url_type": "article"
                    }
                ],
                "url_type": "aritcle"
            },
            {
                "domain": "news.sina.com.cn",
                "item": [
                    {
                        "cookie": "",
                        "encode": "utf-8",
                        "end_rule": ["id='artibody'"],
                        "type": "Crawler",
                        "header": {
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Encoding': 'gzip, deflate, sdch',
                            'Accept-Language': 'zh-CN,zh;q=0.8',
                            "Cache - Control": "max - age = 0",
                            'Connection': 'keep-alive',
                            'Host': 'news.sina.com.cn',
                            'Referer': 'http://gov.sina.com.cn/',
                            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
                            'Upgrade - Insecure - Requests': '1'
                        },
                        "url_template": [r"^http[s]?://news.sina.com.cn/.+?/\d{4}-\d{2}-\d{2}/.*?\d{1,10}.shtml$", ],
                        "url_type": "article"
                    }
                ],
                "url_type": "aritcle"
            },
            {
                "domain": "tech.sina.com.cn",
                "item": [
                    {
                        "cookie": "",
                        "encode": "utf-8",
                        "end_rule": ["id='artibody'"],
                        "type": "Crawler",
                        "header": {
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Encoding': 'gzip, deflate, sdch',
                            'Accept-Language': 'zh-CN,zh;q=0.8',
                            "Cache - Control": "max - age = 0",
                            'Connection': 'keep-alive',
                            'Host': 'tech.sina.com.cn',
                            'Referer': 'http://tech.sina.com.cn/',
                            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
                            'Upgrade - Insecure - Requests': '1'
                        },
                        "url_template": [r"^http[s]?://tech.sina.com.cn/.+?/\d{4}-\d{2}-\d{2}/.*?\d{1,10}.shtml$", ],
                        "url_type": "article"
                    }
                ],
                "url_type": "aritcle"
            },
            {
                "domain": "tech.sina.com.cn",
                "item": [
                    {
                        "cookie": "",
                        "encode": "utf-8",
                        "end_rule": ["id='artibody'"],
                        "type": "Crawler",
                        "header": {
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Encoding': 'gzip, deflate, sdch',
                            'Accept-Language': 'zh-CN,zh;q=0.8',
                            "Cache - Control": "max - age = 0",
                            'Connection': 'keep-alive',
                            'Host': 'tech.sina.com.cn',
                            'Referer': 'http://tech.sina.com.cn/',
                            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
                            'Upgrade - Insecure - Requests': '1'
                        },
                        "url_template": [r"^http[s]?://tech.sina.com.cn/zl/.+?/\d{4}-\d{2}-\d{2}/.*?\d{1,10}.htm", ],
                        "url_type": "article"
                    }
                ],
                "url_type": "aritcle"
            },
            {
                "domain": "finance.sina.com.cn",
                "item": [
                    {
                        "cookie": "",
                        "encode": "utf-8",
                        "end_rule": ["id='artibody'"],
                        "type": "Crawler",
                        "header": {
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Encoding': 'gzip, deflate, sdch',
                            'Accept-Language': 'zh-CN,zh;q=0.8',
                            "Cache - Control": "max - age = 0",
                            'Connection': 'keep-alive',
                            'Host': 'finance.sina.com.cn',
                            'Referer': 'http://finance.sina.com.cn/',
                            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
                            'Upgrade - Insecure - Requests': '1'
                        },
                        "url_template": [r"^http[s]?://finance.sina.com.cn/(?!z|(?:stock/usstock)).+?/\d{4}-\d{2}-\d{2}/.*?\d{1,10}.shtml$", ],
                        "url_type": "article"
                    }
                ],
                "url_type": "aritcle"
            },
            {
                "domain": "finance.sina.com.cn",
                "item": [
                    {
                        "cookie": "",
                        "encode": "utf-8",
                        "end_rule": ["id='artibody'"],
                        "type": "Crawler",
                        "header": {
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Encoding': 'gzip, deflate, sdch',
                            'Accept-Language': 'zh-CN,zh;q=0.8',
                            "Cache - Control": "max - age = 0",
                            'Connection': 'keep-alive',
                            'Host': 'finance.sina.com.cn',
                            'Referer': 'http://finance.sina.com.cn/',
                            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
                            'Upgrade - Insecure - Requests': '1'
                        },
                        "url_template": [r"^http[s]?://finance.sina.com.cn/stock/usstock/.+?/\d{4}-\d{2}-\d{2}/.*?\d{1,10}.shtml$", ],
                        "url_type": "article"
                    }
                ],
                "url_type": "aritcle"
            },
        ]
        for conf in confs:
            self._insert_crawler_conf(conf["domain"], conf["item"][0], conf["url_type"])

        rules = [
            {
                "domain": "sina.com.cn",
                "type": "search",
                "parse_py": [
                    {
                        "rule_uuid": "xxxx",  # 这条匹配规则的ID，
                        "url_match": [r"^http[s]?://api.search.sina.com.cn/\?", ],
                        "modulepath": "pz3_crawler.parse_py.sina_search",  # python类的命名空间
                        "class": "sina_search",
                        "function": "main"
                    }
                ],
            },
            {
            "domain": "ent.sina.com.cn",
            "type": "article",  # 其有两个值，article或comment
            "parse_rules":
                [
                    {
                    "rule_uuid": "xxxx",  # 这条匹配规则的ID，
                    "url_match": [r"^http[s]?://ent.sina.com.cn/zl/.+?/\d{4}-\d{2}-\d{2}/.*?\d{1,10}.shtml$", ],
                    "title": [{"type": "xpath", "express": '//h1', 'func': "text"}, ],
                    # 代表标题的获取方式，将依次执行后面的表达式，regex代表后面的表达式是一个正则表达式，xpath代表后面是一个路径获取。
                    "author": [{"type": "xpath", "express": "//*[@id='author_ename']/a", "func": "text"}, ],  # 代表作者
                    "origin_meida_name": [
                        {"type": "xpath", "express": "//*[@id='pub_date']/following-sibling::a[1]",
                         "func": "text"}, ],
                    # # 转载自,原始媒体名。
                    "origin_url": [{"type": "xpath", "express": "//*[@id='pub_date']/following-sibling::a[1]",
                                    "func": "html"},
                                   {"type": "xpath", "express": "//@href", "func": ""}
                                   ],  # 原始链接。 # 原始链接。
                    "content": [{"type": "xpath", "express": "//*[@id='artibody']", "func": "html"}, ],  # [必填]内容
                    "publish_at": [{"type": "xpath", "express": "//*[@id='pub_date']", 'func': "text"},
                                   {"type": "regex", "express": "[\d]{4}.[\d]{2}.[\d]{2}.", "func": 'search',
                                    "param": "0"}],  # 代表发布时间。//*[@id="page-tools"]/span/span[1]
                    "tags": [{"type": "css", "express": ".art_keywords a", "func": "text"},
                             ],  # 文章原始Tag
                    "imgs": [{"type": "css", "express": "#artibody img", "func": "html"},
                             {"type": "xpath", "express": "//@src", "func": ""}],

                    }
                ]
            },
            {
            "domain": "ent.sina.com.cn",
            "type": "article",  # 其有两个值，article或comment
            "parse_rules": [
                    {
                    "rule_uuid": "xxxx",  # 这条匹配规则的ID，
                    "url_match": [r"^http[s]?://ent.sina.com.cn/.+?/\d{4}-\d{2}-\d{2}/.*?\d{1,10}.shtml$", ],
                    "title": [{"type": "xpath", "express": '//h1', 'func': "text"}, ],
                    # 代表标题的获取方式，将依次执行后面的表达式，regex代表后面的表达式是一个正则表达式，xpath代表后面是一个路径获取。
                    "author": [{"type": "xpath", "express": "//*[@id='author_ename']/a", "func": "text"}, ],  # 代表作者
                    "origin_meida_name": [
                        {"type": "bs4", "express": {"class": "time-source"}, "func": "find_one", "param": "text"},
                        {"type": "regex", "express": "\s+(\S+)\s+(\S+)\s+(\S+)", "func": "search", "param": 3},
                        # {"type": "regex", "express": "\s", "func": "sub", "param": "" }
                    ],
                    # 转载自,原始媒体名。
                    "origin_url": [
                        {"type": "css", "express": "#page-tools > span > span.titer + span > a:first-child",
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
                    }
                ]
            },
            {
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
            },
            {
                "domain": "tech.sina.com.cn",
                "type": "article",  # 其有两个值，article或comment
                "parse_rules": [
                    {
                        "rule_uuid": "xxxx",  # 这条匹配规则的ID，
                        "url_match": [r"^http[s]?://tech.sina.com.cn/.+?/\d{4}-\d{2}-\d{2}/.*?\d{1,10}.shtml$", ],
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
            },
            {
                "domain": "tech.sina.com.cn",
                "type": "article",  # 其有两个值，article或comment
                "parse_rules": [
                    {
                        "rule_uuid": "xxxx",  # 这条匹配规则的ID，
                        "url_match": [r"^http[s]?://tech.sina.com.cn/zl/.+?/\d{4}-\d{2}-\d{2}/.*?\d{1,10}.htm", ],
                        "title": [{"type": "xpath", "express": '//h1', 'func': "text"}, ],
                        # 代表标题的获取方式，将依次执行后面的表达式，regex代表后面的表达式是一个正则表达式，xpath代表后面是一个路径获取。
                        "author": [{"type": "xpath", "express": "//*[@id='author_ename']/a", "func": "text"}, ],  # 代表作者
                        "origin_meida_name": [
                            {"type": "css", "express": "#media_name > a:nth-child(1)",
                             "func": "text"}, ],
                        # # 转载自,原始媒体名。
                        "origin_url": [{"type": "css", "express": "#media_name > a:nth-child(1)",
                                        "func": "html"},
                                       {"type": "xpath", "express": "//@href", "func": ""}
                                       ],  # 原始链接。
                        "content": [{"type": "xpath", "express": "//*[@id='artibody']", "func": "html"}, ],  # [必填]内容
                        "publish_at": [{"type": "css", "express": "#pub_date", 'func': "text"},
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
            },
            {
            "domain": "finance.sina.com.cn",
            "type": "article",  # 其有两个值，article或comment
            "parse_rules": [
                {
                    "rule_uuid": "xxxx",  # 这条匹配规则的ID，
                    "url_match": [
                        r"^http[s]?://finance.sina.com.cn/(?!z|(?:stock/usstock)).+?/\d{4}-\d{2}-\d{2}/.*?\d{1,10}.shtml$", ],
                    "title": [{"type": "xpath", "express": '//h1', 'func': "text"}, ],
                    # 代表标题的获取方式，将依次执行后面的表达式，regex代表后面的表达式是一个正则表达式，xpath代表后面是一个路径获取。
                    "author": [{"type": "css", "express": "p.article-editor", "func": "text"},
                               {"type": "regex", "express": "(.*?)：(.*?) ", "func": 'search',
                                "param": "2"}
                               ],  # 代表作者
                    # "origin_meida_name": [
                    #     {"type": "css", "express": "span.time-source > span > a",
                    #      "func": "text"}, ],
                    "origin_meida_name": [
                        {"type": "bs4", "express": {"class": "time-source"}, "param": "text", "func": "find_one"},
                        {"type": "regex", "express": "\n \n(.*?)\n", "func": 'search',
                         "param": "1"}
                    ],
                    # # 转载自,原始媒体名。
                    "origin_url": [{"type": "css", "express": "span.time-source > span > a",
                                    "func": "html"},
                                   {"type": "xpath", "express": "//@href", "func": ""}
                                   ],  # 原始链接。
                    "content": [{"type": "xpath", "express": "//*[@id='artibody']", "func": "html"}, ],  # [必填]内容
                    "publish_at": [{"type": "css", "express": "span.time-source", 'func': "text"},
                                   {"type": "regex", "express": "[\d]{4}.[\d]{2}.[\d]{2}.", "func": 'search',
                                    "param": "0"}],  # 代表发布时间。//*[@id="page-tools"]/span/span[1]
                    "tags": [{"type": "css", "express": ".article-keywords a", "func": "text"},
                             ],  # 文章原始Tag
                    "imgs": [{"type": "css", "express": "#artibody img", "func": "html"},
                             {"type": "xpath", "express": "//@src", "func": ""}],
                    }
                ]
            },
            {
            "domain": "finance.sina.com.cn",
            "type": "article",  # 其有两个值，article或comment
            "parse_rules": [
                {
                    "rule_uuid": "xxxx",  # 这条匹配规则的ID，
                    "url_match": [
                        r"^http[s]?://finance.sina.com.cn/stock/usstock/.+?/\d{4}-\d{2}-\d{2}/.*?\d{1,10}.shtml$", ],
                    "title": [{"type": "xpath", "express": '//h1', 'func': "text"}, ],
                    # 代表标题的获取方式，将依次执行后面的表达式，regex代表后面的表达式是一个正则表达式，xpath代表后面是一个路径获取。
                    "author": [{"type": "css", "express": "p.article-editor", "func": "text"},
                               {"type": "regex", "express": "(.*?)：(.*?) ", "func": 'search',
                                "param": "2"}
                               ],  # 代表作者
                    "origin_meida_name": [{"type": "css", "express": "#media_name", "func": "text"},
                                          {"type": "regex", "express": "\s", "func": 'sub',
                                           "param": ""}
                                          ],
                    # # 转载自,原始媒体名。
                    "origin_url": [{"type": "css", "express": "#media_name > a", "func": "html"},
                                   {"type": "xpath", "express": "//@href", "func": ""}
                                   ],  # 原始链接。
                    "content": [{"type": "xpath", "express": "//*[@id='artibody']", "func": "html"}, ],  # [必填]内容
                    "publish_at": [{"type": "css", "express": "#pub_date", 'func': "text"},
                                   {"type": "regex", "express": "[\d]{4}.[\d]{2}.[\d]{2}.", "func": 'search',
                                    "param": "0"}],  # 代表发布时间。//*[@id="page-tools"]/span/span[1]
                    "tags": [{"type": "css", "express": ".art_keywords a", "func": "text"},
                             ],  # 文章原始Tag
                    "imgs": [{"type": "css", "express": "#artibody img", "func": "html"},
                             {"type": "xpath", "express": "//@src", "func": ""}],

                    }
                ]
            }
        ]

        for rule in rules:
            self._insert_parse_conf(rule["domain"], rule, rule["type"])



    def test_crawl_list_and_page(self):
        # header = {
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        #     'Accept-Encoding': 'gzip, deflate, sdch',
        #     'Accept-Language': 'zh-CN,zh;q=0.8',
        #     "Cache - Control": "max - age = 0",
        #     'Connection': 'keep-alive',
        #     'Host': 'finance.sina.com.cn',
        #     'Referer': 'http://www.sina.com.cn/',
        #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36',
        #     'Upgrade - Insecure - Requests': '1'
        # }
        self._insert()
        # result_list = []
        # for item in self.sina_list_crawler("小米"):
        #     url = item["url"]
        #     # self._insert_crawler_conf("sina", "article")
        #     crawler = self.crawler_mgr.get_crawler_object(item["url"], "article")
        #     # tld = tldextract.extract(url)
        #     # header["host"] = ".".join(part for part in tld if part)
        #     code, content = crawler.get()
        #
        #     if code == 200:
        #         judge = UrlParserJudge(self.db)
        #         parser = judge.test_parser(url, "article")
        #         result = parser.parser(url, content)
        #         result_list.append(result)
        #
        # with open