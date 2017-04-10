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


    def get(self,url,header=None,proxy=None,timeout=3):
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
            content = content.decode()
        if resp.status_code == 200:

            try:
                #用chardet进行内容分析
                # str_code = chardet.detect(data)

                if not self._encode in ['utf-8','utf8'] :
                    try:
                        content = content.decode(self._encode).encode('utf-8')
                    except:
                        log.error(traceback.format_exc())
                self._content = content
                log.info(msg)

            except:
                msg = "%s:[%s]"%(msg,traceback.format_exc())
                log.error(msg)

        else:
            header_str = str(s.headers)#simplejson.dumps(s.headers, ensure_ascii=False)

            msg = "%s[%s][proxy:%s][header:%s]"%(msg,content,t_proxy,header_str)
            log.warn(msg)

        return status_code,content



class SearchCrawler(object):
    '''
    执行搜索列表的的抓取。参数可通过抓取队列中取得。。
    '''
    def __init__(self,start_url,end_cond,paser_rule,header=None,proxy=None,encode='utf8',keyword=""):
        '''

        :param start_url:   [string]起始URL
        :param end_cond:    [dict]停止条件。
            {
            "end_url":"",        #到某个URL
            "end_time":"",       #到某个时间点。
            "max_count":100,    #最大纪录条数。
            }
        :param header:      [dict]请求头。
        :param proxy:       [str]
        :param encode:      [str]utf-8或gbk
        :param keyword:     [str]关键字。
        :return:
        '''
        self._start_url = start_url
        self._header = header
        self._keyword = keyword
        self._proxy = proxy
        self._encode = encode
        self._parse_rule = paser_rule

        #下面的是停止条件。
        self._end_time = None
        end_time_str = end_cond.get("end_time",None)
        if end_time_str:
            end_time_str =  datetime_regular(end_time_str)
            self._end_time = dtstr2ts(end_time_str)

        self._end_url = end_cond.get("end_url",None)

        self._max_count = end_cond.get("max_count",100)




    def _is_end(self,item,index):
        '''
        判断当前搜索结果项是否是结束项。
        :param item:    [dict]结构为
        {
            "media_name": "chenqiaoheaven",
            "title": "<em>雷军</em>为什么毫无保留的把自己的战略透漏出来?",
            "url": "http://tieba.baidu.com/p/4929394817?pid=102248997286&cid=0#102248997286",
            "create_at": "2017-01-06 16:46",
            "channel": "小米",
            "media_url": "http://tieba.baidu.com/i/sys/jump?un=chenqiaoheaven"
        }
        :param  index   当前是第几条纪录。
        :return:    [true|false\
        '''

        tm_url = item.get("url",None)
        tm_cur_time = item.get("create_at",None)
        try:
            # 遇到那个规定的URL了。
            if not tm_url is None and tm_url == self._end_url:
                return True

            #将时间数据数据进行规则化。
            tm_time_str = tm_cur_time
            tm_time_str =  datetime_regular(tm_cur_time)
            tm_time_obj = dtstr2ts(tm_time_str)

            #如是当前条目时间已经早过end_time,则表示已经结束。
            if self._end_time and self._end_time > tm_time_obj:
                return True


        except:
            log.error(traceback.format_exc())

        if self._max_count < index:
            return True

        return False

    def get_page_urls(self):
        '''
        获取这个抓取项所取得的所有相关链接。
        :return:    [list("“)]每个item的结构如下。
        {
            "media_name": "\u90ae\u79d1\u9662\u8fbe\u6469\u72d2\u72d2",
            "refer_url": "http://tieba.baidu.com/f/search/res?isnew=1&kw=&qw=%C0%D7%BE%FC&un=&rn=10&pn=0&sd=&ed=&sm=1&only_thread=1",
            "title": "<em>\u96f7\u519b</em>\u5bb6\u7684\u7ea2\u7c733\u7cfb\u7edf\u8d8a\u66f4\u65b0\u8d8a\u5783\u573e",
            "url": "http://tieba.baidu.com/p/4931251555?pid=102309462758&cid=0#102309462758",
            "create_at": "2017-01-08 01:38",
            "header": {
                "Connection": "keep-alive",
                "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
                "Accept-Encoding": "gzip, deflate, sdch",
                "Cache-Control": "max-age=0",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36",
                "Host": "tieba.baidu.com",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Upgrade-Insecure-Requests": "1"
            },
            "proxy": null,
            "channel": "\u9ad8\u8fbe",
            "media_url": "http://tieba.baidu.com/i/sys/jump?un=%d3%ca%bf%c6%d4%ba%b4%ef%c4%a6%e1%f4%e1%f4"
        }
        '''

        result_list = []    #列表中的对象为push_url_params(self,url,head,proxy,ref_url,cookie,count):所使用的参数。

        header = self._header

        ref_url = self._start_url #此值随着翻页会变化。

        parse_result = tldextract.extract(self._start_url)
        domain = parse_result.domain + '.' + parse_result.suffix
        domain = domain.lower()

        cur_url = self._start_url

        idx  = 0
        b_exit = False

        while (not b_exit):

            crawl_obj = Crawler(domain=domain, header=header,proxy=self._proxy,ref_url=ref_url,url_type=CrawlerMgr.SEARCH_URL,encode=self._encode)

            status,content = crawl_obj.get(cur_url)

            if status == 200:
                #解析。
                parser = HtmlParserBase(self._parse_rule)
                page_doc = parser.parser(cur_url,content)

                #获取结构后的文章。
                search_items = page_doc.get("search_items",[])

                #判断文章是否已经到结束。
                for srh_ite in search_items:

                    idx += 1
                    if self._is_end(srh_ite, idx ):
                        b_exit = True
                        break

                    srh_ite["refer_url"] = cur_url  #增加URL的引用。
                    srh_ite['proxy']    = self._proxy
                    srh_ite["header"]   = header

                    result_list.append(srh_ite)

                cur_url = page_doc.get("next_url",None)     #下一页URL。

                if not cur_url:
                    b_exit = True
            else:
                b_exit = True

        return result_list