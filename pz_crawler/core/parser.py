# -*- coding: utf-8 -*-

__author__ = 'commissar'
import pymongo
import tldextract
from bs4 import BeautifulSoup

import re
from pz_crawler.core import extractor
import hashlib
import lxml.html.soupparser
import lxml.html.html5parser
# from lxml.html import tostring, html5parser,soupparser

from lxml import etree
from lxml import objectify
import importlib
import traceback
from tldextract.tldextract import LOG
import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

import logging
#logging.basicConfig(level=logging.WARN)
logging.basicConfig(level=logging.CRITICAL)


'''
当前包依赖mongoDB中的指定库中的rules集合。
rules集合的结构如下：
      rule = {
            "domain":"1905.com",
            "type":"article",               #其有两个值，article或comment
            "parse_rules":[
                {
                    "rule_uuid":"xxxx",                             #这条匹配规则的ID，
                    "url_match":["^http[s]?://www.1905.com/news/[\d]{8}/[\d]*.",],        #[必填]url的适配正则表达式。其是或的关系，只有要有一个成功就代表当前页面可以抓取。
                    "title":[{"type":"xpath","express":'//h1','func':"text"},],     #代表标题的获取方式，将依次执行后面的表达式，regex代表后面的表达式是一个正则表达式，xpath代表后面是一个路径获取。
                    "author":[{"type":"css","express":"div.pic-base>span.autor-name","func":"text"},
                              {"type":"regex","express":"：(.*?)$", "func":'search',"param":"1",}],    #代表作者
                    "origin_meida_name":[{"type":"css","express":".pic-source > .copyfrom","func":"text"},],                       #转载自,原始媒体名。
                    "origin_url":[{"type":"css","express":".pic-source > .copyfrom","func":"html" },
                                    {"type":"xpath","express":"//@href","func":""}],                            #原始链接。
                    "content":[ {"type":"css","express":"div.pic-content > p", "func":"html"}, ],                            #[必填]内容
                    "publish_at":[{"type":"css","express":".pic-base > span:first-child",'func':"text"},
                                  {"type":"regex", "express":"[\d]{4}.[\d]{2}.[\d]{2}", "func":'search', "param":"0"}],    #代表发布时间。
                    "tags":[{"type":"css", "express":"div.rel-label > a","func":"text"  }],                                    #文章原始Tag
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
            "parse_py":[
                {
                "rule_uuid":"xxxx",                             #这条匹配规则的ID，
                "url_match":["^http[s]?://www.weibo.com/u/[\d]+",],        #[必填]url的适配正则表达式。其是或的关系，只有要有一个成功就代表当前页面可以抓取。
                "modulepath":"pz_crawler.pzcode.parse_py.weibo", #python类的命名空间
                "class":"weibo",
                "functon":"main"
                }
            ]
        }

'''





class ExtractorGroup(object):
    '''
    代表一组提取数据的动作组。
    '''

    def __init__(self, actions):

        self.extractors = self._build_extractor(actions)        #提取表达式列表。

    def _build_extractor(self,actions):
        '''
        将规则建立成解析对象。
        :param actions:
        :return:
        '''
        act_list = []
        for act in actions:
            class_name = act["type"].capitalize() + "ValueExtractor"

            action_obj = getattr(extractor,class_name)(**act)
            action_obj.build()

            act_list.append(action_obj)

        return act_list

    def debug_value(self, content, xml_doc):
        '''
        此接口用于调试规则。将会把每条规则的匹配结果都返回。
        :param content:
        :param xml_doc:
        :return:    [list(string)]
        '''

        result = []

        val = content
        for act in self.extractors:
            if isinstance(val,(list,set)):
                new_list = []
                for t_val in val:
                    new_val = act.value(content,xml_doc,t_val)
                    new_list.append(new_val)
                val = new_list
            else:
                val = act.value(content,xml_doc,val)

            result.append(val)

        return result

    def get_value(self,content, xml_doc):
        '''
        从文章中获取内容。
        :param content:     [str]内容。
        :param xml_doc:     [etree]全文档的dom树
        :return:    [string]返回最终规则所匹配的结果。
        '''
        val = content
        for act in self.extractors:

            if isinstance(val,(list,set)):
                new_list = []
                for t_val in val:
                    new_val = act.value(content,xml_doc,t_val)
                    new_list.append(new_val)
                val = new_list
            else:
                val = act.value(content,xml_doc,val)

        return val

class ExtractorObjectGroup(ExtractorGroup):

    def __init__(self, actions):

        self._inner_actions = {}        #内部对象的动作集

        outer_acts = actions.get("express",[])
        super(ExtractorObjectGroup,self).__init__(outer_acts)

        property_dict = actions.get("property",{})
        for filed_name, filed_actions in property_dict.items():
            self._inner_actions [filed_name] = ExtractorGroup(filed_actions)


    def get_value(self,content, xml_doc):

        tmp_result = super(ExtractorObjectGroup,self).get_value(content, xml_doc)
        result = {}


        if isinstance(tmp_result,(list,set)):
            result = []

            for tmp_item in tmp_result:

                if isinstance(tmp_item,unicode):
                    tmp_item = tmp_item.encode("utf-8")

                tmp_xml = etree.HTML(tmp_item.lower().decode('utf-8'))

                tmp_obj = {}

                for filed_name, filed_act_grp_obj in self._inner_actions.items():

                    t_value = filed_act_grp_obj.get_value(tmp_item, tmp_xml)    #这个是动作组的获取，对于每个组只会调用 一次。
                    tmp_obj[filed_name] = t_value

                result.append(tmp_obj)
        else:

            if isinstance(tmp_result,unicode):
                tmp_result = tmp_result.encode("utf-8")

            tmp_xml =None
            try:
                try:
                    tmp_xml = etree.HTML(tmp_result.lower().decode('utf-8'))
                except:
                    tmp_xml = etree.HTML(tmp_result.lower())

                for filed_name, filed_act_grp_obj in self._inner_actions.items():

                    field_value = filed_act_grp_obj.get_value(tmp_result, tmp_xml)    #这个是动作组的获取，对于每个组只会调用 一次。
                    result[filed_name] = field_value
            except Exception as e:
                logging.error(traceback.format_exc())


        # for filed_name, filed_act_grp_obj in self._inner_actions.items():
        #
        #     if isinstance(tmp_result,(list,set)):
        #
        #         field_value = []
        #         for tmp_item in tmp_result:
        #
        #             if isinstance(tmp_item,unicode):
        #                 tmp_item = tmp_item.encode("utf-8")
        #
        #             tmp_xml = etree.HTML(tmp_item.lower().decode('utf-8'))
        #
        #             t_value = filed_act_grp_obj.get_value(tmp_item, tmp_xml)    #这个是动作组的获取，对于每个组只会调用 一次。
        #             field_value.append(t_value)
        #         result[filed_name] = field_value
        #     else:
        #
        #         if isinstance(tmp_result,unicode):
        #             tmp_result = tmp_result.encode("utf-8")
        #
        #         tmp_xml = etree.HTML(tmp_result.lower().decode('utf-8'))
        #
        #         field_value = filed_act_grp_obj.get_value(tmp_result, tmp_xml)    #这个是动作组的获取，对于每个组只会调用 一次。
        #         result[filed_name] = field_value

        return result


class HtmlParserBase(object):

    TYPE_ARTICLE = "article"
    TYPE_COMMENT = "comment"
    TYPE_MEDIA = "media"
    TYPE_SEARCH = "search"      #代表搜索结果可跟踪列表

    PARSE_RULES= "parse_rules"
    PARSE_PY = "parser_py"
    def __init__(self,rule):
        '''
        :param rule:    [MongoDB.Collectino.Item]为上面的纪录。结构如下
                        {
                           domain:xxxx,
                            parse_rules:[
                            {},{}
                            ]
                        }
        :return:
        '''
        self.rule = rule


    def to_mongo_document(self):
        '''
        返回可写入mongo的文档对象。
        :return:
        '''
        return self.rule

    def get_parser_rules(self,url):
        '''
        得到某个URL的相应配图规则。
        :param url:
        :return:   （str,dict） [parse_rules中的Item],结构见
         {
            rule_uuid:xxxx;                             #这条匹配规则的ID，
            url_match:[url_regex_1,url_regex_2],        #[必填]url的适配正则表达式。其是或的关系，只有要有一个成功就代表当前页面可以抓取。
            title:[{regex:'xxxx'},{xpath:'xxxxx'}],     #代表标题的获取方式，将依次执行后面的表达式，regex代表后面的表达式是一个正则表达式，xpath代表后面是一个路径获取。
            author:[{regex:'xxxx'},{xpath:'xxxxx'}],    #代表作者
            content:[]                                  #[必填]内容
            publish_at:[同上]，                          #代表发布时间。
            tags:[],                                    #文章原始Tag
            imgs:[],
            comment_num:[]
            like_num:[]
            dislike_num:[]
            filters:[]
            comments:{

            }
        }

        '''
        try:
            for t_rule in self.rule["parse_rules"]:
                for _url_match in t_rule["url_match"]:
                    if re.match(_url_match,url,re.IGNORECASE):
                        return "parse_rules",t_rule
        except:
            logging.warn(traceback.format_exc().replace('\n',' '))

        return "parser_py",self.get_parser_py(url)


    def get_parser_py(self, url):
        '''
        得到某个URL的相应配图规则。
        :param url:
        :return:    parse_py,结构见
         {
            rule_uuid:xxxx;                             #这条匹配规则的ID，
            url_match:[url_regex_1,url_regex_2],        #[必填]url的适配正则表达式。其是或的关系，只有要有一个成功就代表当前页面可以抓取。
            "pypath":"" #python的路径
        }
        '''
        try:
            for t_rule in self.rule["parse_py"]:
                for _url_match in t_rule["url_match"]:
                    if re.match(_url_match,url,re.IGNORECASE):
                        return t_rule
        except:
            logging.warn('parse_py error for url %s' % url)
        return None

    def add_rules(self,rules,parse_type):
        '''
        增加解析与匹配规则。
        :param rules:   [list()]列表中为新增规则。
        :return:    [True|Flase]
        '''

        #比较新加的规则中是否有已经支持的。
        for t_rule in self.rule[parse_type]:
            for new_ru in rules:
                #两个规则是否有交集，有交集则不做处理。返回错误。
                if list(set(t_rule["url_match"]).intersection(set(new_ru["url_match"]))):
                    return False

        #确认没有重叠的再将对象加到规则中。
        for new_ru in rules:
            m = hashlib.md5()
            m.update(",".join(new_ru["url_match"]))
            new_ru["rule_uuid"] = m.hexdigest()
            self.rule[parse_type].append(new_ru)

        return True


    def parser(self, url, content):
        fun_str, config = self.get_parser_rules(url)
        return getattr(self, fun_str)(url,content,config)

    def parser_py(self, url, content,config):
        modulepath = config['modulepath'] #python类的命名空间
        logging.info(modulepath)
        cha = importlib.import_module(modulepath)
        class_ = getattr(cha, config['class'])()
        data = getattr(class_, config['main'])(url,content,config)
        return data


    def decode_html(html_string):
        from bs4 import UnicodeDammit             # BeautifulSoup 4

        converted = UnicodeDammit(html_string)
        if not converted.unicode_markup:
            raise UnicodeDecodeError(
                "Failed to detect encoding, tried [%s]",
                ', '.join(converted.tried_encodings))
        # print converted.original_encoding
        return converted.unicode_markup

    def parse_rules(self, url, content, config):
        '''
        对内容进行解析。
        :return:    [parse_rules中的Item],结构见
        {
            title:“”,     #代表标题的获取方式，
            author:“”,    #代表作者
            content:“”,   #[必填]内容
            publish_at:“”,                          #代表发布时间。
            tags:"",                                    #文章原始Tag
            imgs:"",
            comment_num:""
            like_num:""
            dislike_num:""
            filters:""
            comments:{

            }
        }
        '''
        html_src = content.lower()
        document = None

        # 将条件注释判断浏览器<!--[if !IE]><!--[if IE]><!--[if lt IE 6]><!--[if gte IE 6]> 这种注释删除，
        # 因为    lxml的_convert_tree(） 不支持这种注释。

        reg_list = [r"<!--[\s]*\[[\s]*if[^\]]{1,12}]>",
                    r"<!--[\s]*\[[\s]*if[^\]]+]>",
                    r'<!--[\s\S]*?>',
                    r"<![\s]*\[endif\][\s]*-->",
                    r'<![\s]*--[\s]*>',
                    r"[^!]([-]{2,})[^>]"]

        for reg_pl in reg_list:
            html_src,_ = re.subn(reg_pl, "", html_src,0,re.IGNORECASE|re.MULTILINE)


        if isinstance(content,str):
            # document = etree.HTML(content.lower())

            document =  lxml.html.soupparser.fromstring(html_src.lower(),features='html5lib')#'html.parser')
            # document = lxml.html.html5parser.fromstring(html_src)
            # document = lxml.html.fromstring(html_src)
        else:
            # document = etree.HTML(content.lower().decode('utf-8'))

            document =  lxml.html.soupparser.fromstring(html_src.lower().decode('utf-8'),features='html5lib')
            # document = lxml.html.html5parser.fromstring(html_src.decode('utf-8'))
            # document = lxml.html.fromstring(html_src.decode('utf-8'))



        result = {}
        for field_name, field_express in config.items():

            if field_name in ["rule_uuid","url_match"]:
                continue

            t_extractor = None

            if type(field_express) is dict:
                t_extractor = ExtractorObjectGroup(field_express)
            else:

                t_extractor = ExtractorGroup(field_express)
            t_val = t_extractor.get_value(content,document)

            result[field_name] = t_val

        return result

class UrlParserJudge(object):
    '''
    URL解析判断器，通过URL来判断此页面是否可被解析。
    '''
    def __init__(self, mongodb):
        '''

        :param mongo_connect_str:   [str]mongo连接字符串，如"mongodb://localhost:27017/"
        :param mongo_db:            [str]数据库名。
        :param mongo_user:          [str]用户名
        :param mongo_passwd         [str]密码
        :return:
        '''

        self.db = mongodb

    def test_parser(self, url, any_type):
        '''
        测试此URL是否可以被解析。
        :param url: [str]
        :return:    [HtmlParserBase对象|False]
        '''
        parse_result = tldextract.extract(url)

        #tldextract.extract('http://forums.news.cnn.com/')
        #ExtractResult(subdomain='forums.news', domain='cnn', suffix='com')

        full_domain = parse_result.domain + '.' + parse_result.suffix

        rule = self.db.rules.find_one({"domain":full_domain.lower(),"type":any_type})

        if rule:
            parser = HtmlParserBase(rule)
            result = parser.get_parser_rules(url)
            if result:
                return parser

        return False

class ParserRuleDb(object):
    def __init__(self,mongo_connect_str,mongo_db,mongo_user=None,mongo_passwd=None):
        '''

        :param mongo_connect_str:   [str]mongo连接字符串，如"mongodb://localhost:27017/"
        :param mongo_db:            [str]数据库名。
        :param mongo_user:          [str]用户名
        :param mongo_passwd         [str]密码
        :return:
        '''

        self.mongo_client = pymongo.MongoClient(mongo_connect_str)
        self.db = self.mongo_client[mongo_db]

        if mongo_user and mongo_passwd:
            self.db.authenticate(mongo_user,mongo_passwd)

    def add_parser_rule(self,rule, parse_type,rtype):
        '''
        增加对某一域名的抓取规则。
        :param  domain      [str]域名，全小写。
        :param  rules       [list()]规则列表，规则对象：
        :return:    返回当前[mongodb.ObjectId]
        '''
        domain = rule['domain']
        rules = rule[parse_type]
        rule = {
            "domain":domain,
            "type":rtype,
            parse_type:[]
        }

        parser = HtmlParserBase(rule)
        parser.add_rules(rules,parse_type)
        doc = parser.to_mongo_document()

        rule_doc = self.db.rules.find_one({"domain":domain.lower(),"type":rtype})
        if not rule_doc:
            result = self.db.rules.insert(doc)
        else:

            parser.add_rules(rule_doc.get(parse_type,[]),parse_type)
            doc = parser.to_mongo_document()

            result = self.db.rules.update({"domain":doc["domain"],"type":rtype}, doc)

        return result

