#! /usr/bin/env python
# coding: utf-8

import os


TORNADO_LISTEN_PORT = 8081
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(CURRENT_PATH, '../scripts')

# redis conf
REDIS_CONF = {
    'host': "127.0.0.1",
    'port': 6379,
    'password': "",
    'db': 1
}

settings = {
    'debug': True,  #  debug: True 为调试模式， 会自动重载修改过的文件， 上线时需要设置为False, 减小压力
    'cookie_secret': '95EE8F440B65246FE167615CCB8904B5', # 每一个项目都需要修改一下， 防止加密串重复
}