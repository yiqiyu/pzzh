# -*- coding: utf-8 -*-
__author__ = 'commissar'

import re
import urllib

class CrawlerConfItem(object):
    '''
    下载器的某一个的配置。用这个对象可以初始化一个Crawler对象。
    '''
    def __init__(self,url_template,header=None,cookie=None,end_rule=None,url_type=None,**kwargs):
        '''

        :param _url_template:   [list(string)]可以抓取的URL
        :param header:          [dict]头部。
        :param cookie:          [string]cookie
        :param end_rule:        [list(string)]
        :return:
        '''

        self.header  = header
        self.cookie = cookie
        self.end_rule = end_rule
        self.url_template = url_template        #可以是一个正则表达式
        self.url_type = url_type

        for nm,nv in kwargs.items():
            self.__setattr__(nm, nv)

    @staticmethod
    def from_mongo_document(document):
        '''
        从mongodb的文档中创建对象。
        :return:
        '''
        return CrawlerConfItem(**document)

    def to_mongo_document(self):

        ret = {}
        for nm,nv in self.__dict__.items():
            ret[nm] = nv

        return ret

    def get_encode(self):
        '''
        获取抓取目标页面的编码。
        :return:   [string]默认是utf-8
        '''
        if hasattr(self,"encode"):
            return self.__getattribute__("encode")
        else:
            return "utf-8"

    def get_keyword_type(self):
        '''
        获取所有关键字类型的。
        :return:
        '''
        url_build_rule = self.__getattribute__("url_build_rule")

        if url_build_rule:
            template_param = url_build_rule.get("param",{})
            if template_param:
                return template_param.get("key_type",None)

        return None

    def get_header(self):
        return self.header

    def build_search_url(self,**kwargs):
        '''
        根据关键字来构造URL，此函数只在url_type为search时有效。
        :param kwargs:      [dict]key为url_build_rule中的param中的key.,当前已知值为{keyword:xxxx}
        :return:    [str]
        '''

        url_result = None
        if not (self.url_type == "search"):
            return url_result

        url_build_rule = self.__getattribute__("url_build_rule")

        if url_build_rule:
            url_template = url_build_rule.get("template",None)

            #模板每个参数的要求。
            template_param = url_build_rule.get("param",{})

            #找到URL的基板，然后将之与所给参数进行替换。
            url_result = url_template
            if url_result:
                for k_name,k_val in kwargs.items():

                    param_conf = template_param.get(k_name,{})
                    param_encode = param_conf.get("encode",None)    #参数是否进行编码。
                    param_quote = param_conf.get("quote",False)     #参数是否需要进行转义

                    url_k_val = k_val
                    #在组装URL时将部分参数转成gdk编码。
                    if param_encode:
                        if isinstance(k_val,unicode):#not isinstance(k_val, unicode):
                            url_k_val = url_k_val.encode(param_encode)
                        else:
                            url_k_val = url_k_val.decode('utf-8').encode(param_encode)

                    if param_quote:
                        url_k_val = urllib.quote(url_k_val)

                    t_place = "{%s}"%k_name
                    url_result = url_result.replace(t_place,url_k_val)

            # search_option = SearchOptions({"keyword":k_val})




        return url_result


    def is_match(self,url):
        '''
        :return  [bool]判断当前配置条目是否可以抓取此URL
        '''

        _url_templates = self.url_template
        b_match = False
        for u_tmp in _url_templates:
            if re.search(u_tmp,url,re.IGNORECASE):
                b_match = True
                break
        return b_match


class CrawlerConf(object):
    '''
    下载器的全部配置。
    {
        domain:"",
        item:[
            {
                type:'xxx'      #默认article、comment、list
                url_template:[str,str,],
                header:{
                },
                cookie:rrrr;
                end_rule:[xx,xx],   #抓取成功的页面特征
                encode:utf8|gbk     #页面的编码。
            }
            ....
        ]
    }
    '''
    def __init__(self,domain,_url_type):
        '''
        :param domain:
        :param _url_type:   [string]article,search,media
        :return:
        '''
        self._domain = domain
        self._url_type = _url_type
        self._items = []            #配置列表。
        self._defaut_item = None    #默认配置规则。
        pass

    @staticmethod
    def from_mongo_document(domain,doc,_url_type):
        '''
        从mongodb的文档中创建对象。
        :return:
        '''
        crw_cnf  = CrawlerConf(domain,_url_type)

        for item in doc.get("item",[]):
            conf_item = CrawlerConfItem.from_mongo_document(item)

            crw_cnf.add_conf_item(conf_item)

        return crw_cnf

    def to_mongo_document(self):
        '''
        生成mongo的文档对象。
        :return:    [dict]
        '''
        ret =  {
            'domain':self._domain,
            'item':[it.to_mongo_document() for it in self._items],
            'url_type':self._url_type
        }

        return ret

    def get_unique_desc(self):
        return {'domain':self._domain,'url_type':self._url_type}

    def get_all_conf_items(self):
        '''
        得到所有的抓取配置项。
        :return:    [list(CrawlerConfItem)]
        '''
        return self._items

    def get_conf_item(self,url):
        '''
        获取与此URL想适配的匹配规则。当域名域名匹配成功，但规则都没有匹配到时，会返回一个默认规则。如域名都没有配置成功，则会返回空。
        :return [CrawlerConfItem|None]
        '''

        correct_item = None
        parse_result = tldextract.extract(url)

        domain = parse_result.domain + '.' + parse_result.suffix


        if domain.lower() == self._domain:
            correct_item = self._defaut_item

            for _t_item in self._items:
                if _t_item.is_match(url):
                    correct_item = _t_item
                    break

        return correct_item

    def add_conf_dict(self,**kwargs):
        '''
        向当前对象中的增加配置项。需要保证字段完整性。
        '''
        new_item = CrawlerConfItem(**kwargs)
        self._items.append(new_item)

        self._defaut_item = self._items[0]


    def add_conf_item(self,item):
        '''
        向当前对象中的增加配置项。
        :param  item    [CrawlerConfItem]
        '''
        self._items.append(item)


    def get_build_search_urls(self, **kwargs):
        '''
        获取此配置的搜索URL。
        :return [list(string)]  URL列表。
        '''
        urls = []
        for item in self._items:
            t_srh_url = item.build_search_url(**kwargs)

            if t_srh_url:
                urls.append(t_srh_url)

        return urls
