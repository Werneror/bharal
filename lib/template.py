#!/usr/bin/python3
# coding: utf-8
# author: Werner
# email: me@werner.wiki
# date: 2020.03.05

from settings import INDEX_FILE
from settings import LOGIN_FILE


class Template(object):

    def __init__(self):
        with open(INDEX_FILE) as f:
            self.index_html = f.read()
        with open(LOGIN_FILE) as f:
            self.login_html = f.read()

    def get_index_html(self):
        return self.index_html

    def get_login_html(self, login_failed=False):
        if login_failed:
            return self.login_html.format(login_failed=1)
        else:
            return self.login_html.format(login_failed=0)


template = Template()
