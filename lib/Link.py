#!/usr/bin/env python
# coding=utf-8

from lib.DB import db
from lib.define import *
import time
import datetime
from lib.util import convert

class Link(object):
    def __init__(self, link_id=0):
        self.link_id = link_id
        self.db = db

    def _get(self, field, value):
        pass

    def getAll(self):
        lst = self.db.r.zrevrange(LINK_SORT_BYTIME, 0, -1)
        #print("zscore")
        #print(self.db.r.zscore(LINK_SORT_BYTIME, 6))
        #print(self.db.r.keys('link:'))
        tmp = []
        for key in lst:
            tmp.append(bytes.decode(key))
        lst = tmp

        result = []
        for key in lst:
            print(key)
            tmps = self.db.r.hgetall(LINK.format(link_id=key))
            tmps = convert(tmps)
            tmps['visit'] = int(self.db.r.zscore(LINK_SORT_BYVISIT.format(link_id=key), key))

            tmps['created_at'] = datetime.datetime.fromtimestamp(int(tmps['created_at'])).strftime("%Y-%m-%d %H:%M:%S")

            result.append(tmps)

        return result

    def add(self, info):

        link_id= self.db.r.incr(LINK_COUNT)

        self.db.r.hmset(LINK.format(link_id=link_id), info)
        self.db.r.sadd(LINK_ALL, link_id)
        self.db.r.zadd(LINK_SORT_BYTIME.format(link_id=link_id), link_id, int(time.time()))
        self.db.r.zadd(LINK_SORT_BYVISIT.format(link_id=link_id),link_id, 0)

#        print(link_id)
        return link_id
