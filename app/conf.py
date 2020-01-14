#! /usr/bin/env python
# coding: utf-8

import os

def full_url(host, port):
    real_host = os.getenv(host, 'idps2-gtja.datagrand.cn')
    real_port = os.getenv(port, '80')
    return 'http://{}:{}'.format(real_host, real_port)


TORNADO_LISTEN_PORT = os.getenv('LISTEN_PORT', 8000)
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
STATIC_PATH = os.path.join(CURRENT_PATH, 'static')
LOG_PATH = os.path.join(STATIC_PATH, 'root.log')
LOGIN_HOST = full_url('EXTRACT_HOST', 'EXTRACT_PORT')
RELOGIN_INTERVAL = 300
# user info
USER_INFO = {
    'username': 'admin',
    'password': 'mgZjRYeQVi',
}
# redis conf
REDIS_CONF = {
    'host': "127.0.0.1",
    'port': 6379,
    'password': "",
    'db': 1
}

ORACLE_CONF = {
    'host': '100.100.21.163',
    'port': '1521',
    'username': 'system',
    'password': 'oracle',
    'service': 'xe',
}

settings = {
    'debug': True,  #  debug: True 为调试模式， 会自动重载修改过的文件， 上线时需要设置为False, 减小压力
    'cookie_secret': '95EE8F440B65246FE167615CCB8904B5', # 每一个项目都需要修改一下， 防止加密串重复
}
