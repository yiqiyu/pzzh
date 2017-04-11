#coding:utf-8
from __future__ import absolute_import

import tldextract

from pz3_crawler.core.crawler import Crawler

from pz3_crawler.core.crawler_conf import CrawlerConf

class CrawlerMgr(object):
    '''
    用于管理所有下载器。crawler_conf集合。
    此类当某个URL来时，用于判断此URL需要哪个Crawler来进行下载 。
    '''
    ARTICLE_URL='article'
    COMMENT_URL='comment'
    MEDIAS_URL='media'
    SEARCH_URL = "search"

    def __init__(self,mongodb,**kwargs):
        self._db = mongodb
        self._collect = self._db.crawler_conf


    def can_crawler(self,url):
        '''
        判断这个URL是否可以抓取。
        :param url:
        :return:    [true|false]
        '''
        return self.get_crawler_object(url,url_type=self.ARTICLE_URL) != None

    def get_crawler_object(self,url,url_type,**params):
        '''
        获取一个可以抓取URL的爬虫对象。从数据库中获取。
        :param url:
        :return:   [Crawler]
        '''
        parse_result = tldextract.extract(url)
        domain = parse_result.domain + '.' + parse_result.suffix
        cond = {'domain':domain,"url_type":url_type}

        item = self._collect.find_one(cond)

        crawler = None

        if item:
            crawler_conf = CrawlerConf.from_mongo_document(domain,item,url_type)

            crwl_cnf_item = crawler_conf.get_conf_item(url)     #获取这个URL的抓取配置
            if crwl_cnf_item:
                crwl_cnf_dict = crwl_cnf_item.to_mongo_document()

                crawler_param = dict(params)
                crawler_param.update(crwl_cnf_dict)

                crawler_param.update({
                    'domain':domain,
                    'url_type':url_type,  #url类型,可以是 媒体,文章,评论
                    # 'header':crwl_cnf_dict.get('header'),
                    # 'cookie':crwl_cnf_dict.get('cookie'),
                    # 'end_rule':crwl_cnf_dict.get('end_rule'),
                    # 'encode':crwl_cnf_dict.get('encode')
                })
                crawler = Crawler(**crawler_param)                  #创建下载器

        return crawler

    def insert(self,crawler_conf):
        '''
        增加一个抓取配置项。
        :param crawler_obj: [CrawlerConf]
        :return:
        '''
        crawler_doc = crawler_conf.to_mongo_document()
        unqine_desc = crawler_conf.get_unique_desc()

        item = self._collect.find_one(unqine_desc)
        if not item:
            self._collect.insert(crawler_doc)
        else:
            domain = item["domain"]
            url_type = item["url_type"]

            crawler_conf_obj = CrawlerConf.from_mongo_document(domain,item,url_type)

            # 将同一域名下的所有抓取规则进行合并。
            # TODO: 这里没有进行规则去重的合并。
            for cnf_item in crawler_conf.get_all_conf_items():
                crawler_conf_obj.add_conf_item(cnf_item)

            crawler_doc = crawler_conf_obj.to_mongo_document()

            self._collect.find_and_modify(query=unqine_desc, update=crawler_doc, upsert=True)

        return

    def get_search_conf_iter(self):
        '''
        获取所有用于搜索的配置项
        :return:    [list(CrawlerConf)]
        '''

        cond = {"url_type":CrawlerMgr.SEARCH_URL}
        conf_iter = self._collect.find(cond)#.sort({"domain":-1})

        for t_conf in conf_iter:
            domain = t_conf["domain"]
            url_type = t_conf["url_type"]

            crawler_conf_obj = CrawlerConf.from_mongo_document(domain,t_conf,url_type)

            yield crawler_conf_obj

    def get_search_conf_by_name(self,name):
        '''
        获取某个名称的搜索配置项。
        :return     [CrawlerConf]
        '''
        cond = {"url_type":CrawlerMgr.SEARCH_URL,"item.name":name}
        t_conf = self._collect.find_one(cond)#.sort({"domain":-1})

        domain = t_conf["domain"]
        url_type = t_conf["url_type"]

        crawler_conf_obj = CrawlerConf.from_mongo_document(domain,t_conf,url_type)
        return crawler_conf_obj

    #
    # def get_search_crawler_obj(self,name,end_cond=None,header=None,proxy=None,encode='utf8',keyword=""):
    #     conf = self.get_search_conf_by_name(name)
