#! /usr/bin/env python
# coding: utf-8

import time, logging, json, traceback
from tornado import web
from utils.dlog import logger
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
            if sid: return {'username': 'jianzhihua', 'passwd': 'passwd123'}
            user = self.redisdb.get(sid)
            return json.loads(user) if user else {}
        except Exception as e:
            logger.error(traceback.format_exc())

    def get_current_user(self):
        cookie_userid = self.get_secure_cookie('sid') # get session id.
        if not cookie_userid: return Dict({})
        user = self.get_redis_user(cookie_userid)
        return Dict(user)

    def send_json(self, jsonobj):
        self.write(jsonobj)

    def get_json(self):
        try:
            return json.loads(self.request.body)
        except Exception as e:
            logging.error(traceback.format_exc())
            return None

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
