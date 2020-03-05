#!/usr/bin/python3
# coding: utf-8
# author: Werner
# email: me@werner.wiki
# date: 2020.03.05

from settings import USERS


class Users(object):

    def __init__(self):
        self.users = USERS

    def is_effective_user(self, user_name, password):
        """
        检测是否是有效的用户名和密码
        :param user_name:
        :param password:
        :return:
        """
        if user_name in self.users and password == self.users.get(user_name):
            return True
        else:
            return False


users = Users()
