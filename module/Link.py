#!/usr/bin/env python
# coding=utf-8

from module import Comment, Account
from module.DB import db
from module.define import *
import time
import datetime
from module.util import convert

class Link(object):
    db = db

    def __init__(self, lid=0, db=db):
        # self.lid = bytes.decode(lid)
        if isinstance(lid, bytes):
            self.lid = bytes.decode(lid)
        else:
            self.lid = lid

        # self.lid = lid
        self.db = db
        print(type(db))
        self.link_key = LINK.format(lid=self.lid)

    @classmethod
    def create(self, link):
        pass

    @classmethod
    def save(self):
        pass


    def _sort_by_time(self):
        lst = self.db.r.zrevrange(LINK_SORT_BYTIME, 0, -1)
        tmp = []
        for key in lst:
            tmp.append(bytes.decode(key))
        lst = tmp

        return lst

    def _visit(self):
        result = int(self.db.r.zscore(LINK_SORT_BYVISIT.format(lid=self.lid), self.lid))

        return result

    @classmethod
    def all(cls):
        lst = cls._sort_by_time(cls)
        links = []

        for lid in lst:
            links.append(Link(lid))

        return links

    @classmethod
    def delete(cls, lid):

        try:
            link = Link(lid)

            cls.db.r.delete(LINK.format(lid=lid))
            cls.db.r.srem(LINK_ALL, lid)
            cls.db.r.zrem(LINK_SORT_BYTIME.format(lid=lid), lid)
            cls.db.r.zrem(LINK_SORT_BYVISIT.format(lid=lid), lid)
            cls.db.r.srem(ACCOUNT_LINK.format(uid=link.author_id), lid)
        except:
            return False
        else:
            return True

    # return all comments
    def _comments(self):
        link_comments = LINK_COMMENT.format(lid=self.lid)
        lst = self.db.zrevrange(link_comments, 0, -1)
        result = []

        for cid in lst:
            result.append(Comment(cid))

        return result

    @property
    def comments(self):
        return self._comments()

    def _author(self):
        return Account(self.author_id)

    @classmethod
    def add(cls, info):

        lid= cls.db.r.incr(LINK_COUNT)

        info.setdefault('url', None)
        info.setdefault('created_at', None)
        info.setdefault('title', None)
        info.setdefault('author', None)
        info.setdefault('updated_at', None)
        # info.setdefault('vote_up', 0)
        # info.setdefault('vote_down', 0)
        # points , vote_up and vote_down chage this value
        info.setdefault('points', 0)

        cls.db.r.hmset(LINK.format(lid=lid), info)
        cls.db.r.sadd(LINK_ALL, lid)
        cls.db.r.zadd(LINK_SORT_BYTIME.format(lid=lid), lid, int(time.time()))
        cls.db.r.zadd(LINK_SORT_BYVISIT.format(lid=lid),lid, 0)
        cls.db.r.sadd(ACCOUNT_LINK.format(uid=info['author']), lid)

        return lid

    def _num_comments(self):
        link_comment_num = LINK_COMMENT_COUNT.format(lid=self.lid)

        return self.db.r.scard(link_comment_num)


    def __getattr__(self, field):
        # attribute = ['icon', 'url', 'title', 'created_at', 'updated_at']
        attribute = []

        action = ['comments', 'author']

        if field in attribute:
            return self._get(field)
        elif field == 'num_comments':
            return self._num_comments()
        elif field == 'visit':
            return self._visit()
        elif field == 'comments':
            return self._comments()
        elif field == 'author':
            return self._author()
        elif field == 'author_id':
            return int(self._get('author'))
        else:
            return None

    @property
    def title(self):
        # return self.link_key
        return self.db.hget(self.link_key, 'title')

    @property
    def url(self):
        return self.db.hget(self.link_key, 'url')

    @property
    def created_at(self):
        return self.db.hget(self.link_key, 'created_at')

    @property
    def points(self):
        result = self.db.hget(self.link_key, 'points')

        if result:
            return result
        else:
            return 0

    def vote_up(self, incr=1):
        return self.db.r.hincrby(self.link_key, 'points', incr)

    def vote_down(self, incr=-1):
        return self.db.r.hincrby(self.link_key, 'points', incr)

    def _get(self, field):
        key = LINK.format(lid=self.lid)
        result = self.db.hget(key, field)
        return result

    # Bytes to str
    def _bytes2str(self, byte, doit=True):
        if not isinstance(byte, bytes):
            return byte

        if doit == True:
            return bytes.decode(byte)
        else:
            return byte
