# -*- coding: utf-8 -*-
__author__ = 'commissar'

import re
import lxml
from lxml import etree
from lxml.etree import _Element

from html.parser import HTMLParser
from bs4 import BeautifulSoup
# from pz3_crawler.core.parser import HTMLParser

import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')


class UnsupportFuncException(Exception):
    pass


class BaseValueExtractor(object):
    '''
    '''
    FUNC_TEXT = "text"
    FUNC_HTML = 'html'

    FUNC = {FUNC_TEXT:"",FUNC_HTML:""}

    def __init__(self, type, express, func="text", **kwargs):
        self.expression = express
        self.type = type
        self.func = func

    def build(self):
        pass


class RegexValueExtractor(BaseValueExtractor):
    '''
    使用正则表达式提取内容。
    '''
    FUNC_SEARCH = "search"
    FUNC_SUB = "sub"

    FUNCS = [FUNC_SEARCH, FUNC_SUB]


    def __init__(self,type, express, func='search',param=-1,**kwargs):

        super(RegexValueExtractor,self).__init__( type, express, func, **kwargs )
        self.param = param
        # self.expression = expression
        self.builded_exp = re.compile(express,re.IGNORECASE)

        if not self.func in RegexValueExtractor.FUNCS:
            raise UnsupportFuncException()

    def _search(self,last_val):
        match_result = self.builded_exp.search(last_val)

        ret = ""
        if match_result:
            grp_num = int(self.param)
            if grp_num > -1:
                ret = match_result.group(grp_num)
            else:
                ret = match_result.group()

        return ret

    def _sub(self,last_val):
        match_result =  self.builded_exp.sub(self.param, last_val)
        return match_result

    def value(self,content,dom_tree,last_val):

        new_val = getattr(self, "_"+self.func)(last_val)
        return new_val

class XpathValueExtractor(BaseValueExtractor):
    '''
    使用XPath提取内容。
    '''

    def __init__(self,type, express, func ,**kwargs):
        super(XpathValueExtractor,self).__init__( type, express, func, **kwargs )

        if not (func in CssValueExtractor.FUNC.keys() or func == ""):
            raise UnsupportFuncException()

        self.param = kwargs.get("param","utf8")

    def _query_tree(self,dom_tree):
        '''
        获取经过表达式匹配后dom元素。
        :param dom_tree:
        :return:    [list(Element)]
        '''
        return dom_tree.xpath(self.expression)

    def value(self,content,dom_tree,last_val):

        cur_tree = dom_tree
        if isinstance(last_val, (_Element,)):
            cur_tree = last_val
        elif isinstance(last_val,str) and len(content) > len(last_val):
            # cur_tree = etree.fromstring(last_val)
            cur_tree = lxml.html.soupparser.fromstring(last_val,features='html5lib')

        elem = self._query_tree(cur_tree)

        ret = ""

        if len(elem) == 1:
            if not self.func or self.func == "":
                ret = elem[0]
            elif self.func == BaseValueExtractor.FUNC_HTML:
                ret = etree.tounicode(elem[0])

                # ret = etree.tostring(elem[0])

            else:
                ret = getattr(elem[0], self.func)
        elif len(elem) > 1:
            text_ary = []
            if self.func == BaseValueExtractor.FUNC_HTML:
                for t_elem in elem:
                    t_txt = etree.tounicode(t_elem)
                    if t_txt:
                        text_ary.append(t_txt)
            elif not self.func or self.func == "":
                for t_elem in elem:
                    text_ary.append(t_elem)
            else:
                for t_elem in elem:
                    t_txt = getattr(t_elem, self.func)
                    if t_txt:
                        text_ary.append(t_txt)

            ret = text_ary#"\r\n".join(text_ary)
        return ret

class CssValueExtractor(XpathValueExtractor):


    def _query_tree(self,dom_tree):
        return dom_tree.cssselect(self.expression)


class ConstValueExtractor(BaseValueExtractor):
    '''
    常量赋值，直接返回常量
    '''
    def __init__(self,type, express, func=None,**kwargs):
        super(ConstValueExtractor,self).__init__(type,express,func,**kwargs)


    def value(self,content,dom_tree,last_val):

        # new_val = getattr(self, "_"+self.func)(last_val)
        return self.expression

class PostfixValueExtractor(BaseValueExtractor):
    '''
    后缀赋值，将前一个处理的值作为后缀加到一个常量后返回。
    '''
    def __init__(self,type, express, func=None,param=None,**kwargs):
        super(PostfixValueExtractor,self).__init__(type,express,func,**kwargs)
        self.param = param

    def value(self,content,dom_tree,last_val):

        expre = self.expression

        # if isinstance(expre,unicode):
        #     expre = expre.encode("utf-8")
        return expre + last_val

class PrefixValueExtractor(BaseValueExtractor):
    '''
    前缀赋值，将前一个处理的值作为前缀加到一个常量前返回。
    '''
    def __init__(self,type, express, func=None,param=None,**kwargs):
        super(PrefixValueExtractor,self).__init__(type,express,func,**kwargs)
        self.param = param

    def value(self,content,dom_tree,last_val):

        expre = self.expression

        # if isinstance(expre,unicode):
        #     expre = expre.encode("utf-8")
        return  last_val + expre


class OtherValueExtractor(BaseValueExtractor):
    '''
    其他函数功能。
    '''
    def __init__(self,type, express, func=None,param=None,**kwargs):
        super(OtherValueExtractor,self).__init__(type,express,func,**kwargs)

    def value(self,content,dom_tree,last_val):

        #unescape 将上次的结果进行HTML转义，即将&amp; &lt; &gt; 转换成 & < >
        if self.func == "unescape":
            html_parser = HTMLParser()#.HTMLParser()
            return html_parser.unescape(last_val)
        else:
            return last_val

class Bs4ValueExtractor(BaseValueExtractor):
    '''
    其他函数功能。
    '''
    FUNC_FIND_ONE = "find_one"
    FUNC_FIND_ALL = 'find_all'

    FUNC = {FUNC_FIND_ONE:"",FUNC_FIND_ALL:""}

    def __init__(self,type, express, func=None,param=None,**kwargs):
        super(Bs4ValueExtractor,self).__init__(type,express,func,**kwargs)
        if not (self.func in Bs4ValueExtractor.FUNC.keys() or self.func == ""):
            raise UnsupportFuncException()
        self.param = param

    def buid_bs4(self,content):
        soup = BeautifulSoup(content,'lxml')
        return soup

    def get_html(self,soup):
        html =[]
        if isinstance(soup,list):
            for tag in soup :
                html.append(tag.prettify())
        else:
            html.append(soup.prettify())
        return ''.join(html)

    def get_text(self,soup):
        text =[]
        if isinstance(soup,list):
            for tag in soup :
                text.append(tag.get_text())
        else:
            text.append(soup.get_text())
        return ''.join(text)

    def find_one(self,last_val):
        soup = self.buid_bs4(last_val)
        '''name=None, attrs={}'''
        tag = soup.find(**self.expression)
        return getattr(self, 'get_%s' % self.param)(tag)

    def find_all(self,last_val):
        soup = self.buid_bs4(last_val)
        '''name=None, attrs={}'''
        tags = soup.findAll(**self.expression)
        return getattr(self, 'get_%s' % self.param)(tags)

    def value(self,content,dom_tree,last_val):
        result_txt = ''
        if isinstance(last_val,(list,set)):
            html = []
            for dstr in last_val:
               findtxt = getattr(self, self.func)(dstr)
               html.append(findtxt)
            result_txt = html
        else:
            result_txt = getattr(self, self.func)(last_val)
        return result_txt