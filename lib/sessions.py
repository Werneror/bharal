#!/usr/bin/python3
# coding: utf-8
# author: Werner
# email: me@werner.wiki
# date: 2020.03.05

import time
import random
import string
from threading import Timer


class Sessions(object):

    def __init__(self, length=64, age=604800, recycle_interval=3600):
        """
        :param length: session字符串长度
        :param age: session过期时间，默认为 7 天，单位：秒
        :param recycle_interval，默认为 1 小时，单位：秒
        """
        self.charset = string.ascii_letters + string.digits
        self.length = length
        self.age = age
        self.recycle_interval = recycle_interval
        self.sessions = list()
        self.recycle_session()

    def generate_new_session(self):
        """
        生成新session
        :return:
        """
        new_session = ''.join(random.choice(self.charset) for _ in range(self.length))
        self.sessions.append([new_session, time.time()])
        return new_session

    def is_session_exist(self, session):
        """
        判断一个session是否存在，若存在则更新session最后访问时间
        :param session:
        :return:
        """
        for _session in self.sessions:
            if _session[0] == session:
                _session[1] = time.time()
                return True
        return False

    def recycle_session(self):
        """
        回收过期的session
        :return:
        """
        now = time.time()
        deleting_sessions = list()
        for _session in self.sessions:
            if now - _session[1] > self.age:
                deleting_sessions.append(_session)
        for _session in deleting_sessions:
            self.sessions.remove(_session)
        Timer(self.recycle_interval, self.recycle_session).start()


sessions = Sessions()
