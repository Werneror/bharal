#!/usr/bin/python3
# coding: utf-8
# author: Werner
# email: me@werner.wiki
# date: 2020.03.05

import os


CERT_FILE = os.path.join('ssl', 'cert.pem')
KEY_FILE = os.path.join('ssl', 'key.pem')
FAVICON_FILE = os.path.join('resources', 'favicon.ico')
INDEX_FILE = os.path.join('templates', 'index.html')
LOGIN_FILE = os.path.join('templates', 'login.html')
LOG_FILE = 'bharal.log'    # Modify this

LOGIN_PATH = '/login'
FAVICON_PATH = '/favicon.ico'
SERVER_NAME = 'bharal/0.1'
SESSION_COOKIE_NAME = 'bharal_session'

SCHEME = 'https'
DOMAIN = '127.0.0.1'    # Modify this
BIND_IP = '0.0.0.0'
PORT = 4430   # Modify this
SERVER = '{}://{}:{}/'.format(SCHEME, DOMAIN, PORT)    # Modify this if use Ningx as a reverse proxy

# Modify and add users
USERS = {
    'admin': 'admin',
    'werner': 'p@s5w0rd',
}
