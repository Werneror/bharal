#!/usr/bin/python3
# coding: utf-8
# author: Werner
# email: me@werner.wiki
# date: 2020.03.05

import re
import http.server
from urllib import parse

from publicsuffix2 import PublicSuffixList

from settings import *
from lib.proxy import Proxy
from lib.users import users
from lib.sessions import sessions
from lib.template import template


class BharalHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        self.login_path = LOGIN_PATH
        self.favicon_path = FAVICON_PATH
        self.server_name = SERVER_NAME
        self.session_cookie_name = SESSION_COOKIE_NAME
        self.domain_re = re.compile(r'(?=^.{3,255}$)[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+')
        with open(FAVICON_FILE, 'rb') as f:
            self.favicon_data = f.read()
        super().__init__(request, client_address, server)

    def do_GET(self):
        self.do_request()

    def do_POST(self):
        self.do_request()

    def do_HEAD(self):
        self.do_request()

    def do_request(self):
        """
        do_GET or do_POST

        :return:
        """
        self.pre_process_path()
        if self.is_login():
            if self.is_need_proxy():
                Proxy(self).proxy()
            else:
                self.process_original()
        else:
            self.redirect_to_login()

    def is_login(self):
        """
        检查是否登录
        :return:
        """
        if self.path == self.login_path or self.path == self.favicon_path:
            return True
        session = self.get_request_cookie(self.session_cookie_name)
        if sessions.is_session_exist(session):
            return True
        else:
            return False

    def process_original(self):
        """
        处理原生请求(非代理请求)
        :return:
        """
        if self.path == self.favicon_path:
            self.process_favicon()
        elif self.path == self.login_path:
            self.process_login()
        else:
            self.process_index()

    def process_login(self):
        """
        处理登录
        :return:
        """
        if self.command == 'POST':
            content_length = int(self.headers['Content-Length'])
            raw_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = parse.parse_qs(parse.unquote(raw_data))
            if 'user' in parsed_data and 'password' in parsed_data:
                if users.is_effective_user(parsed_data['user'][0], parsed_data['password'][0]):
                    session = sessions.generate_new_session()
                    self.send_response(http.HTTPStatus.FOUND)
                    self.send_header('Location', '/')
                    self.send_header('Set-Cookie', '{}={}; expires=Sun, 30-Jun-3000 02:06:18 GMT; '
                                                   'path=/; HttpOnly'.format(self.session_cookie_name, session))
                    self.end_headers()
                    return
            body = template.get_login_html(login_failed=True)
        else:
            body = template.get_login_html(login_failed=False)
        self.return_html(body)

    def process_index(self):
        """
        返回首页
        :return:
        """
        body = template.get_index_html()
        self.return_html(body)

    def process_favicon(self):
        """
        处理 favicon 图标
        :return:
        """
        self.send_response(200)
        self.send_header('Content-Type', 'image/x-icon')
        self.end_headers()
        self.wfile.write(self.favicon_data)

    def return_html(self, body):
        """
        返回HTML页面
        :param body:
        :return:
        """
        self.send_response(200)
        self.send_header('Content-Length', len(body))
        self.send_header('Content-Type', 'text/html; charset=UTF-8')
        self.end_headers()
        self.wfile.write(body.encode('utf-8'))

    def is_need_proxy(self):
        """
        检查请求路径判断是否需要进行代理
        :return:
        """
        return self.path[1:].startswith('http://') or self.path[1:].startswith('https://')

    def pre_process_path(self):
        """
        对 path 进行预处理
        :return:
        """
        if self.path.startswith('/?url='):
            self.path = self.path.replace('/?url=', '/', 1)
        if self.is_start_with_domain(self.path[1:]):
            self.path = '/https://' + self.path[1:]
        if not self.is_need_proxy():
            referer = self.get_request_header('Referer')
            if referer is not None and parse.urlparse(referer.replace(SERVER, '')).netloc != '':
                self.path = '/' + referer.replace(SERVER, '') + self.path

    def get_request_cookie(self, cookie_name):
        """
        取请求 cookie
        :param cookie_name:
        :return:
        """
        cookies = str()
        for header in self.headers._headers:
            if header[0] == 'Cookie':
                cookies = header[1].split('; ')
                break
        for cookie in cookies:
            _cookie = cookie.split('=')
            if len(_cookie) == 2 and _cookie[0] == cookie_name:
                return _cookie[1]
        return str()

    def get_request_header(self, header_name):
        """
        取请求头
        :param header_name:
        :return:
        """
        for header in self.headers._headers:
            if header[0] == header_name:
                return header[1]
        return None

    def version_string(self):
        """
        返回服务器软件的版本字符串
        :return:
        """
        return self.server_name

    def redirect_to_login(self):
        """
        重定向到登录页面
        :return:
        """
        self.send_response(http.HTTPStatus.FOUND)
        self.send_header('Location', self.login_path)
        self.end_headers()

    def is_start_with_domain(self, string):
        """
        判断 string 是否是以域名开头
        :param string:
        :return:
        """
        domain = self.domain_re.match(string)
        psl = PublicSuffixList()
        if domain is None or domain.group(1)[1:] not in psl.tlds:
            return False
        else:
            return True
