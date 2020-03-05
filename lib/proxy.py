#!/usr/bin/python3
# coding: utf-8
# author: Werner
# email: me@werner.wiki
# date: 2020.03.05

import re
from urllib import parse
from http import HTTPStatus

import requests

from settings import *


class Proxy(object):

    def __init__(self, handler):
        self.handler = handler
        self.url = self.handler.path[1:]
        parse_result = parse.urlparse(self.url)
        self.scheme = parse_result.scheme
        self.netloc = parse_result.netloc
        self.site = self.scheme + '://' + self.netloc
        self.path = parse_result.path

    def proxy(self):
        """
        处理、转发请求，获取响应并在处理后转发，
        :return:
        """
        self.process_request()
        content_length = int(self.handler.headers.get('Content-Length', 0))
        data = self.handler.rfile.read(content_length)
        try:
            r = requests.request(method=self.handler.command, url=self.url, headers=self.handler.headers,
                                 data=data, verify=False, allow_redirects=False)
        except BaseException as error:
            self.process_error(error)
        else:
            self.process_response(r)

    def process_request(self):
        """
        处理请求
        :return:
        """
        self.modify_request_header('Referer', lambda x: x.replace(SERVER, ''))
        self.modify_request_header('Origin', self.site)
        self.modify_request_header('Host', self.netloc)
        self.modify_request_header('Accept-Encoding', 'identity')

    def process_response(self, r):
        """
        处理响应
        :param r: requests.models.Response
        :return:
        """
        self.handler.send_response(r.status_code)
        content = self.revision_link(r.content, r.encoding)
        if 'location' in r.headers._store:    # 跟随30x跳转
            self.handler.send_header('Location', self.revision_location(r.headers._store['location'][1]))
        if 'content-type' in r.headers._store:
            self.handler.send_header('Content-Type', r.headers._store['content-type'][1])
        if 'set-cookie' in r.headers._store:
            self.revision_set_cookie(r.headers._store['set-cookie'][1])
        self.handler.send_header('Content-Length', len(content))
        self.handler.send_header('Access-Control-Allow-Origin', '*')
        self.handler.end_headers()
        self.handler.wfile.write(content)

    def process_error(self, error):
        """
        处理错误
        :param error:
        :return:
        """
        self.handler.send_error(HTTPStatus.BAD_REQUEST, str(error))

    def modify_request_header(self, header, value):
        """
        修改请求头
        :param header: str
        :param value: str or function
        :return:
        """
        target_header = None
        for _header in self.handler.headers._headers:
            if _header[0] == header:
                target_header = _header
                break
        if target_header is not None:
            self.handler.headers._headers.remove(target_header)
            if callable(value):
                new_header_value = value(target_header[1])
            else:
                new_header_value = value
            self.handler.headers._headers.append((header, new_header_value))

    def revision_location(self, location):
        """
        修正跳转链接
        :param location:
        :return:
        """
        if location.startswith('http://') or location.startswith('https://'):
            new_location = SERVER + location
        elif location.startswith('//'):
            new_location = SERVER + self.scheme + ':' + location
        elif location.startswith('/'):
            new_location = SERVER + self.site + location
        else:
            new_location = SERVER + self.site + self.path + '/' + location
        return new_location

    def revision_link(self, body, coding):
        """
        修正响应内容中的链接
        :return:
        """
        if coding is None:    # 当coding为空时认为是二进制数据
            return body
        rules = [
            ("'{}http://", SERVER),
            ('"{}http://', SERVER),
            ("'{}https://", SERVER),
            ('"{}https://', SERVER),
            ('"{}//', SERVER + self.scheme + ':'),
            ("'{}//", SERVER + self.scheme + ':'),
            ('"{}/', SERVER + self.site),
            ("'{}/", SERVER + self.site),
        ]
        for rule in rules:
            body = body.replace(rule[0].replace('{}', '').encode('utf-8'), rule[0].format(rule[1]).encode('utf-8'))
        return body

    def revision_set_cookie(self, cookies):
        """
        修正Set-Cookie响应头
        :param cookies: 用`, `连接了所有cookie后的字符串，麻烦的地方在于expires中也有`, `
        :return:
        """
        cookie_list = list()
        half_cookie = None
        for _cookie in cookies.split(', '):
            if half_cookie is not None:
                cookie_list.append(', '.join([half_cookie, _cookie]))
                half_cookie = None
            elif 'Expires' in _cookie or 'expires' in _cookie:
                half_cookie = _cookie
            else:
                cookie_list.append(_cookie)
        for _cookie in cookie_list:
            self.handler.send_header('Set-Cookie', self.revision_response_cookie(_cookie))

    def revision_response_cookie(self, cookie):
        """
        修正 Set-Cookie 中的 domain、path 和 secure 等
        :param cookie:
        :return:
        """
        cookie = re.sub(r'domain\=[^,;]+', 'domain=.{}'.format(DOMAIN), cookie, flags=re.IGNORECASE)
        cookie = re.sub(r'path\=\/', 'path={}/'.format('/' + self.site), cookie, flags=re.IGNORECASE)
        if SCHEME == 'http':
            cookie = re.sub(r'secure;?', '', cookie, flags=re.IGNORECASE)
        return cookie
