#! /usr/bin/env python
# coding: utf-8

import time, os, stat
import traceback
import urllib
from tornado import gen, iostream
from .base import BaseHandler
from service.xnet import XRequest
from functools import wraps
from utils.Dlog import logger


def is_login(func):
    @wraps(func)
    def with_logging(self, **kwargs):
        logger.info("--------logger %s" % self.current_user)
        if not self.current_user:
            logger.info('current user is null, remote ip: %s' % self.request.remote_ip)
            self.send_status_message(1, u'Not login!')
            return
        return func(self, **kwargs)
    return with_logging


class SyncTestHandler(BaseHandler):
    def get(self):
        try:
            time.sleep(10)
            self.send_status_message(1, u'sync request finished, during 10s sleep.')
            return
        except Exception as e:
            logger.error(traceback.format_exc())


class AsyncTestHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        try:
            yield gen.sleep(10)
            self.send_status_message(1, u'Async request finished, during 10s sleep.')
            return
        except Exception as e:
            logger.error(traceback.format_exc())


class UserLoginHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        try:
            user_service = XRequest()
            params = urllib.parse.urlencode(self.get_json())
            if not params:
                self.send_status_message(1, u'get params error!')
                return
            val_msg = None
            if not params.get(u'username') or not params.get(u'passwd'):
                self.send_status_message(2, u'username, password can not be null.' )
                return
            response_body = yield user_service.user_validate(params)
            logger.info("content len: %s" % len(response_body))
            cookieid = "cookieid123"
            self.set_secure_cookie('sid', cookieid)
            self.send_status_message(1, "search content len: %s, user cookieid: %s" % (len(response_body), cookieid))
        except Exception as e:
            logger.error(traceback.format_exc())


class UserVisitHandler(BaseHandler):
    @is_login
    @gen.coroutine
    def get(self):
        try:
            self.send_status_message(0, u'login success!')
        except Exception as e:
            logger.error(traceback.format_exc())


class AsyncDownloadHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        file_path = '/data/apply.tar.gz'
        download_name = "a.data"
        content_length = self.get_content_size(file_path)
        self.set_header("Content-Length", content_length)
        self.set_header("Content-Type", "application/octet-stream")
        self.set_header("Content-Disposition", "attachment;filename=" + download_name)  # 设置新的文件名
        content = self.get_file_content(file_path)
        if isinstance(content, bytes):
            content = [content]
        for chunk in content:
            try:
                self.write(chunk)
                yield self.flush()
            except iostream.StreamClosedError:
                break
        return

    # 使用python自带的对于yield的应用对文件进行切片，for循环每运用一次就调用一次
    def get_file_content(self, file_path):
        remaining = None
        chunk_size = 64 * 1024  # 每片的大小是64K
        with open(file_path, "rb") as file:
            while True:
                if remaining is not None and remaining < chunk_size:
                    chunk_size = remaining
                chunk = file.read(chunk_size)
                if chunk:
                    if remaining is not None:
                        remaining -= len(chunk)
                    yield chunk
                else:
                    if remaining is not None:
                        assert remaining == 0
                    return

    # 读取文件长度
    def get_content_size(self, file_path):
        stat_result = os.stat(file_path)
        content_size = stat_result[stat.ST_SIZE]
        return content_size