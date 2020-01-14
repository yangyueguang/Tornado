#! /usr/bin/env python
# coding: utf-8

import time, logging, json, traceback
from tornado import web
from utils.dlog import dlog
from utils.xdict import Dict


class BaseHandler(web.RequestHandler):

    @property
    def redisdb(self):
        return self.application.redisdb

    def prepare(self):
        self.ret = {'status': 0, 'request_id': str(int(time.time() * 1000000)), 'message': 'success!'}
        logging.info(self.ret)

    def get_redis_user(self, sid):
        try:
            # TODO demo test. if the request has sid(session id) return
            if sid: return {'username': 'xxx', 'passwd': '123'}
            user = self.redisdb.get(sid)
            return json.loads(user) if user else {}
        except Exception as e:
            dlog(traceback.format_exc(), True)

    def get_current_user(self):
        cookie_userid = self.get_secure_cookie('sid') # get session id.
        if not cookie_userid: return Dict({})
        user = self.get_redis_user(cookie_userid)
        return Dict(user)

    def send_json(self, jsonobj):
        self.write(jsonobj)

    @property
    def body(self):
        bodys = {}
        self.request.files
        for i in self.request.body_arguments:
            bodys.update({i: self.get_body_argument(i, None)})
        return Dict(bodys)

    def send_status_message_data(self, status, message, data):
        self.ret['status'] = status
        self.ret['message'] = message
        self.ret['data'] = data
        self.send_json(self.ret)

    def send_status_message(self, status, message):
        self.ret['status'] = status
        self.ret['message'] = message
        self.send_json(self.ret)

    def send_data(self, data):
        self.ret['data'] = data
        self.send_json(self.ret)
