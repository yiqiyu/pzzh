# -*- coding: utf-8 -*-
import scrapy
from scrapy.http.request import Request
import requests
import json
import math
import traceback
import time
import random


class KolstoreSpider(scrapy.Spider):
    name = 'kolstore'
    allowed_domains = ['kolstore.com']
    start_urls = ['http://www.kolstore.com/interface/company/weixin.php']

    def start_requests(self):

        headers = {
              "Host":"www.kolstore.com",
              "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
              "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
              "Accept-Encoding":"gzip, deflate",
              "Referer": "http://www.kolstore.com/company/choose_opinionLeaders.php?olt=weixin",
              "Cookie": "acw_tc=AQAAADc4xj/dGgwAV/AwtwXOyaTp+TJx; PHPSESSID=6223i7bm4akdkkhll2saf92lq0; UserId=13456; UserName=wusheng; Mobile=13392967793; Type=1; code=d29b5e6b6e0cd2504cfd",
              "Connection" : "keep-alive",
              "X-Requested-With": "XMLHttpRequest",
              "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"
            }
            # yield Request(link,headers=self.headers,callback=self.parse2)
        for url in self.start_urls:
            param = {
                "page":"1",
                "userType":"0",
                "priceType":"SingnalPicPrice",
                "class":"42",
                "accountType":"2"
            }
            yield scrapy.FormRequest(url, formdata=param,headers=headers,callback=self.parse_wx_list)


    def parse_wx_list(self,response):
        body = response.body
        self.log(response)
        pass

    def parse(self, response):
        pass



class KSCrawlerBase(object):

    def __init__(self,class_id,header,class_desc,beg_page=1):
        self._class_id = class_id
        self._page = beg_page
        self._header = header
        self._url = "http://www.kolstore.com/interface/company/weixin.php"
        self._class_desc = class_desc


    def _get_query_param(self,page):
        return {}


    def crawler(self):
        url = self._url
        page = self._page
        headers = self._header
        cls_id = self._class_id
        desc = self._class_desc

        _max_page = 9999

        max_repeat = 10     #最大重复次数

        ret = False

        repeat = 0  #重复次数

        while(_max_page >= page):
            s = requests.Session()

            try:

                print({"class":cls_id, "page":page, "name":desc, "type":"msg"},flush=True)

                param = self._get_query_param(page)

                resp = s.post(url,headers=headers,data=param)
                status_code = resp.status_code
                content = resp.text

                if status_code == 200:
                    resp_obj = json.loads(content)
                    body = resp_obj["msg"]

                    total_pags = int(body["total"])/20
                    _max_page =  math.ceil(total_pags)

                    for row in body["rows"]:
                        row["class_name"] = desc
                        row_msg = json.dumps(row,ensure_ascii=False)
                        print(row_msg)

                    repeat = 0
                    page += 1
                else:
                    repeat += 1

                    print({"msg":"sleep..","type":"msg"},flush=True)
                    time.sleep(random.randint(1,200)/100)

                    if repeat > max_repeat:
                        break
            except Exception as e:

                repeat += 1
                traceback.print_exc(e)

                print({"msg":"sleep..","type":"msg"},flush=True)
                time.sleep(random.randint(1,200)/100)

                if repeat > max_repeat:
                    break
            finally:
                s.close()

                pass

        if _max_page > page:
            ret = False
        else:
            ret = True

        return ret

class KSCrawlerWeixin(KSCrawlerBase):

    def __init__(self,class_id,header,class_desc,beg_page=1):
        super(KSCrawlerWeixin,self).__init__(class_id,header,class_desc,beg_page)
        self._url = "http://www.kolstore.com/interface/company/weixin.php"

        self._header[""] = "http://www.kolstore.com/company/choose_opinionLeaders.php?olt=weibo"

    def _get_query_param(self,page):

        param = {
                    "page":"%d"%page,
                    "userType":"0",
                    "priceType":"SingnalPicPrice",
                    "class":"%d"%self._class_id,
                    "accountType":"2"
                }
        return param

class KSCrawlerWeibo(KSCrawlerBase):

    def __init__(self,class_id,header,class_desc,beg_page=1):
        super(KSCrawlerWeibo,self).__init__(class_id,header,class_desc,beg_page)
        self._url = "http://www.kolstore.com/interface/company/weibo.php"
        self._header["Referer"] = "http://www.kolstore.com/company/choose_opinionLeaders.php?olt=weibo"

    def _get_query_param(self,page):

        param = {
                "page":"%d"%page,
                "priceType":"PostHardPrice",
                "class":"%d"%self._class_id,
                "accountType":"1"
                }
        return param

class KolStoreCrawler(object):
    '''
    原生的抓取。
    '''
    def __init__(self):
        self.headers = {
          "Host":"www.kolstore.com",
          "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
          "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
          "Accept-Encoding":"gzip, deflate",
          "Cookie": "acw_tc=AQAAADc4xj/dGgwAV/AwtwXOyaTp+TJx; PHPSESSID=6223i7bm4akdkkhll2saf92lq0; UserId=13456; UserName=wusheng; Mobile=13392967793; Type=1; code=d29b5e6b6e0cd2504cfd",
          "Connection" : "keep-alive",
          "X-Requested-With": "XMLHttpRequest",
          "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8"
        }

    def wb_list(self):


        data = [
            #[22,"财经"],[24, "电商"],
            #[26,"心情",32], [27,"运动"],[28,"母婴"],
            # [29, "房产"],[31,"文化"],[32,"星座"],
             #[33,"萌宠",16],[34, "地域",182],
            #[2, '时尚',140],[1, "娱乐",93],
            #[3,"影视音乐",48],
            # [4,"生活百科",173],
            # [13, "科技互联"],[14, "动漫"],[21,"旅行图片"],
            # [20,"美食"],[18,"新闻"],
            # [16,"创意",6],[15,"KOL"],[54,'小鲜肉'],[164,'网红模特']
        ]

        for dt in data:
            dt_id, dt_desc = dt[0],dt[1]
            dt_beg = 1
            if len(dt) == 3:
                dt_beg = dt[2]
            type_crawler = KSCrawlerWeibo(dt_id, self.headers,dt_desc,dt_beg)
            if type_crawler.crawler():
                continue
            else:
                break

    def wx_list(self):

        data = [
            #[42,"财经"],[43, "电商"],[44,"心情",20], [45,"运动"],[47,"母婴"],
             # [48, "房产",27],[49,"文化"],[50,"星座"],[51,"萌宠"],[52, "地域",251],
            #[165, "微商",176],[8, '时尚',247],[7, "娱乐",111],
            #[9,"影视音乐",64],[10,"生活百科",183],
            #[35, "科技互联",135],[36, "动漫"],[41,"旅行图片"],
            # [40,"美食",44],[39,"新闻"],[38,"创意"],[37,"KOL"]
        ]

        for dt in data:
            dt_id, dt_desc = dt[0],dt[1]
            dt_beg = 1
            # if len(dt) == 3:
                # dt_beg = dt[2]
            type_crawler = KSCrawlerWeixin(dt_id, self.headers,dt_desc,dt_beg)
            if type_crawler.crawler():
                continue
            else:
                break


if __name__ == '__main__':

    crawler = KolStoreCrawler()
    crawler.wb_list()


