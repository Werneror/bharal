#!/usr/bin/python3
# coding: utf-8
# author: Werner
# email: me@werner.wiki
# date: 2020.03.05

import ssl
import logging
import http.server

import urllib3
from socketserver import ThreadingMixIn

from settings import *
from lib.handler import BharalHTTPRequestHandler


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ThreadingHttpServer(ThreadingMixIn, http.server.HTTPServer):
    pass


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        filename=LOG_FILE,
        filemode='a',
        format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    )

    with ThreadingHttpServer((BIND_IP, PORT), BharalHTTPRequestHandler) as httpd:
        if SCHEME == 'https':
            httpd.socket = ssl.wrap_socket(httpd.socket, certfile=CERT_FILE, keyfile=KEY_FILE, server_side=True)
        print('Serving HTTP on {bind_ip} port {port} ({scheme}://{domain}:{port}/) ...'.format(
            bind_ip=BIND_IP, port=PORT, scheme=SCHEME, domain=DOMAIN
        ))
        httpd.serve_forever()
