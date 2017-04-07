# -*- coding: utf-8 -*-
__author__ = 'wangyi'

from pymongo import MongoClient



class mongo(object):
    __pool = {}
    def __init__(self,_host):
        if _host not in mongo.__pool:
            mongo.__pool[_host] = MongoClient(host=_host)
        self.__client = mongo.__pool[_host]

    def getclient(self,_db):
        return self.__client[_db]
if __name__ == "__main__":
    mc = mongo("mongodb://chrome.zy.com:27017").getclient("es")
    print(mc)
    mc1 = mongo("mongodb://chrome.zy.com:27017").getclient("starcloud")
    print(mc1)


