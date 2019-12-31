#!/usr/bin/env python
# coding=utf-8
# author:liuyoumin@datagrand.com
# datetime:2019/4/23 下午17:05
from __future__ import unicode_literals
import requests
import time
# from utils.Dlog import logger
import json
import os
import conf
from utils.xdict import Dict
from utils.excel import *

LAST_LOGIN_TIME = None
HEADERS = {'Authorization': None}


def auto_login(func):
    def wrapper(*args, **kwargs):
        global LAST_LOGIN_TIME
        if not LAST_LOGIN_TIME or (time.time() - LAST_LOGIN_TIME) >= conf.RELOGIN_INTERVAL:
            try:
                res = requests.post(conf.LOGIN_HOST + '/api/login', conf.USER_INFO)
                if res.status_code >= 400:
                    print('登录失败，请联系达观项目负责人')
                    exit()
                token = res.json().get('access_token')
                HEADERS['Authorization'] = 'Bearer ' + token
                print('got token: %s' % token)
            except:
                print('login error')
            LAST_LOGIN_TIME = time.time()
        return func(*args, **kwargs)
    return wrapper


@auto_login
def extract(input_file, doc_type_id):
    """调用idps单文件抽取接口"""
    url = conf.LOGIN_HOST + '/api/extracting/instant'
    file = {'file': open(input_file, 'rb')}
    return requests.post(url, data={'docType': doc_type_id}, headers=HEADERS, files=file).json()

def translate_response(res):
    """
    从输入转化为输出
    :return:
    """
    pdf_path = res['result']['pdf_path']
    tables_tags = [32, 33, 34, 37]
    extracts = []
    tables = []
    workbook = xlsxwriter.Workbook(pdf_path + '.xlsx')
    for i in res['result']['tag_list']:
        item = Dict(i)
        if item.tag_id in tables_tags:
            table_item = json.loads(item.ppr, encoding='utf-8')
            data = table_item['text_matrix']
            excel_path = '%s/%s.xlsx' % (os.path.dirname(pdf_path), table_item['table_name'])
            table_item['excel_path'] = excel_path
            write_excel(excel_path, data)
            tables.append(table_item)
            xlsx_add_sheet(table_item['table_name'], data, [], workbook)
        else:
            extract_item = {
                "terms_id": item.terms_id,
                "word": item.word
            }
            extracts.append(extract_item)
    workbook.save()
    workbook.close()
    result = {
        "history_id": res['history_id'],
        "status": res['result']['status'],
        "has_table": true,
        "pdf_path": pdf_path,
        "result": {
            "extract": extracts,
            "tables": tables
        }
    }
    return result


def write_excel(name, data):
    pass


if __name__ == "__main__":
    res = extract('/Users/supers/Desktop/a.pdf', 27)
    print(json.dumps(res, ensure_ascii=False, indent=4))
