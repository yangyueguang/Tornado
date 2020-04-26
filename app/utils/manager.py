#!/usr/bin/env python
# coding=utf-8
# author: Super
# email: 2829969299@qq.com
import requests
import time
from utils.xdict import Dict
import conf
import os
from utils.oracle_db import Oracle
import random
from utils.dlog import dlog
import json
import xlwt
from openpyxl import Workbook

LAST_LOGIN_TIME = None
HEADERS = {'Authorization': None}


def auto_login(func):
    def wrapper(*args, **kwargs):
        global LAST_LOGIN_TIME
        if not LAST_LOGIN_TIME or (time.time() - LAST_LOGIN_TIME) >= conf.RELOGIN_INTERVAL:
            try:
                dlog(conf.LOGIN_HOST)
                res = requests.post(conf.LOGIN_HOST + '/api/login', conf.USER_INFO)
                if res.status_code >= 400:
                    dlog('登录失败，请联系达观项目负责人')
                    exit()
                token = res.json().get('access_token')
                HEADERS['Authorization'] = 'Bearer ' + token
                dlog('got token: %s' % token)
            except:
                dlog('login error')
            LAST_LOGIN_TIME = time.time()
        return func(*args, **kwargs)
    return wrapper


@auto_login
def extract(input_file, doc_type_id):
    """调用idps单文件抽取接口"""
    url = conf.LOGIN_HOST + '/api/extracting/instant'
    file_data = open(input_file, 'rb')
    res = None
    try:
        res = requests.post(url, data={'docType': doc_type_id}, headers=HEADERS, files={'file': file_data})
        dlog(json.dumps(res.json(), ensure_ascii=False, indent=4))
    except:
        dlog('/api/extracting/instant was error!', True)
    file_data.close()
    return res.json() if res else {}


def translate_response(res):
    result = {
        "id": res,
    }
    try:
        write_to_oracle(result, 0)
    except:
        result['message'] = '写入数据库失败'
    return result


# 写入oracle数据库
def write_to_oracle(res, id):
    # oracle = Oracle()
    # oracle.insert_record(res)
    # oracle.insert_item(res['result']['extract'], id)
    # oracle.insert_table(res['result']['tables'], id)
    # dlog(json.dumps(res, ensure_ascii=False, indent=4))
    pass


def xls_save(data, file_name, sheet_name):
    workbook = xlwt.Workbook(encoding='utf-8')
    sheet = workbook.add_sheet(sheet_name)
    for row, item in enumerate(data):
        for col, value in enumerate(item):
            sheet.write(row, col, value)
    workbook.save(file_name)

