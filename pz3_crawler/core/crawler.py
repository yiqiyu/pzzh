#coding:utf-8
from __future__ import absolute_import
__author__ = 'commissar'


from pz3_crawler.conf.setting import log

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

import requests
import traceback
import re

class Crawler(object):
    '''
    这是下载基类，如不进行派生，那么将使用基础的。
    '''

    SEARCH_URL = ""


    def __init__(self,domain,header,proxy=None,ref_url=None,cookie=None,end_rule=None,url_type=None,encode='utf8',**kwargs):
        '''

        :param domain:  [string]当前处理是哪个域名的下载顺
        :param header:  [dict]需要的头部结果
        :param proxy:   [stirng]代理机器字符串。格式如192.168.1.2：9090
        :param ref_url: [string]引用的URL
        :param cookie:  [dict]请求时需要带的cookie.
        :param end_rule  [list|string]用于判断当前页面是否是已经抓取的最终结果页。
        :param url_type 代表url类型 可以是 media,article,comment
        :param kwargs:
        :return:
        '''
        self._domain = domain
        self._header = header
        self._proxy = proxy
        self._ref_url = ref_url
        self._cookie = cookie
        self._end_rule = end_rule
        self._url_type = url_type
        self._encode = encode.lower()

        self._content = None


    def is_result(self):
        '''
        判断当前抓取结果是否为想要的最终结果。
        :return:    [true|false]
        '''
        b_result = True

        if self._content:
            for rt in self._end_rule:

                re_ret = re.search(rt,self._content,re.IGNORECASE)
                if not re_ret :
                    b_result = False
        else:
            b_result = False

        return b_result


    def get(self,url,header=None,proxy=None,timeout=10):
        '''
        获取URL页面内容。
        :param url:
        :return:    [(int, str)]返回状态码和内容。
        '''

        s = requests.session()

        t_proxy = None

        if not self._proxy:
            if not proxy:
                log.warn("[NO_USE_PROXY]This crawler not use proxy!--[%s]"%(url))
            else:
                t_proxy = proxy
        else:
            t_proxy = self._proxy
        s.proxies = t_proxy

        if self._header:
            s.headers.update(self._header)

        if header:
            s.headers.update(header)

        resp = s.get(url,timeout=timeout)
        status_code = resp.status_code

        msg = "[CRAWLER_RESULT][%s][%s][proxy:%s]"%(url,resp.status_code,t_proxy)
        content = resp.content

        if isinstance(content,bytes):
            content = content.decode(self._encode)
        if resp.status_code == 200:

            # try:
                #用chardet进行内容分析
                # str_code = chardet.detect(data)

                # if not self._encode in ['utf-8','utf8'] :
                #     try:
                #         content = content.decode(self._encode).encode('utf-8')
                #     except:
                #         log.error(traceback.format_exc())
                self._content = content
                log.info(msg)

            # except:
            #     msg = "%s:[%s]"%(msg,traceback.format_exc())
            #     log.error(msg)

        else:
            header_str = str(s.headers)#simplejson.dumps(s.headers, ensure_ascii=False)

            msg = "%s[%s][proxy:%s][header:%s]"%(msg,content,t_proxy,header_str)
            log.warn(msg)

        return status_code,content

