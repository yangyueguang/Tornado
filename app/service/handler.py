#! /usr/bin/env python
# coding: utf-8

import time, os, stat
import traceback
import conf
import urllib
import json
import asyncio
from utils.manager import extract, translate_response
from tornado import gen, iostream
from .base import BaseHandler
from service.xnet import XRequest
from functools import wraps
from utils.dlog import logger


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
    def post(self):
        try:
            time.sleep(10)
            self.send_status_message(1, u'sync request finished, during 10s sleep.')
            return
        except Exception as e:
            logger.error(traceback.format_exc())


class AsyncTestHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        try:
            yield gen.sleep(10)
            # asyncio.events
            self.send_status_message(1, u'Async request finished, during 10s sleep.')
            return
        except Exception as e:
            logger.error(traceback.format_exc())

class UserLoginHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        try:
            user_service = XRequest()
            params = urllib.parse.urlencode(self.body())
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

field_config = {}
try:
    with open('static/field_config.json', 'r') as f:
        field_config = json.loads(f.read())
except:
    logger.info('field_config read error')


# pdf 抽取
class Extract(BaseHandler):
    @gen.coroutine
    def post(self):
        request_file = self.request.files.get('file', None)
        error_message = ''
        if not request_file:
            error_message = 'file is required!'
        elif not self.body.docType:
            error_message = 'docType is required!'
        elif not self.body.id:
            error_message = 'id is required!'
        if error_message:
            self.send_status_message(301, error_message)
            return
        name = request_file[0]['filename']
        file_body = request_file[0]['body']
        if not name.endswith('.pdf'):
            self.send_status_message(302, '仅支持pdf类型文件!')
            return
        elif not file_body:
            self.send_status_message(303, '文件为空、文件读取失败!')
            return
        file_path = os.path.join(conf.STATIC_PATH, name.split('.')[0])
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        file_name = os.path.join(file_path, name)
        with open(file_name, 'wb') as f:
            f.write(file_body)
        res = extract(file_name, int(self.body.docType))
        if not res:
            self.send_status_message(304, '抽取服务调用失败!')
            return
        json_result = res.get('result', {})
        if not json_result:
            self.send_status_message(305, '文档转化失败!')
            return
        result = translate_response(res, file_path, field_config, self.body.id)
        # os.remove(file_name)
        self.send_json(result)
