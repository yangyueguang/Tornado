#!/usr/bin/env python
# coding=utf-8
# author:liuyoumin@datagrand.com
# datetime:2019/4/23 下午17:05
from __future__ import unicode_literals
import requests
import time
from utils.xdict import Dict
import conf
import os
from utils.dlog import logger
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
                logger.info(conf.LOGIN_HOST)
                res = requests.post(conf.LOGIN_HOST + '/api/login', conf.USER_INFO)
                if res.status_code >= 400:
                    logger.info('登录失败，请联系达观项目负责人')
                    exit()
                token = res.json().get('access_token')
                HEADERS['Authorization'] = 'Bearer ' + token
                logger.info('got token: %s' % token)
            except:
                logger.info('login error')
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
    except:
        logger.error('/api/extracting/instant was error!')
    file_data.close()
    os.remove(input_file)
    return res.json() if res else {}


def translate_response(res):
    json_result = res.get('result', {})
    if not json_result:
        return {}
    tables = []
    extracts = []
    tables_tags = [32, 33, 34, 37]
    ignore_tags = [3, 4, 5, 6, 7]
    pdf_file_path = json_result['pdf_path']
    pdf_path, pdf_name = os.path.split(pdf_file_path)
    pdf_file_path = os.path.join(conf.EXCEL_PATH, pdf_name)
    workbook = Workbook()
    for i in json_result['tag_list']:
        item = Dict(i)
        if item.tag_id in tables_tags:
            table_item = json.loads(item.ppr, encoding='utf-8')
            data = table_item['text_matrix']
            excel_path = '%s%s.xls' % (pdf_file_path, table_item['table_name'])
            table_item['excel_path'] = excel_path
            xls_save(data, excel_path, table_item['table_name'])
            tables.append(table_item)
            sheet = workbook.create_sheet(table_item['table_name'])
            for row, item in enumerate(data):
                for col, value in enumerate(item):
                    sheet.cell(row, col).value = value
        elif item.tag_id not in ignore_tags:
            real_word = item.ppr if item.ppr else item.word
            extract_item = {
                "terms_id": item.terms_id,
                "word": real_word
            }
            extracts.append(extract_item)
    if len(workbook.sheetnames) > 1:
        workbook.save(pdf_file_path + '.xlsx')
    result = {
        "history_id": res['history_id'],
        "status": json_result['status'],
        "has_table": True,
        "pdf_path": json_result['pdf_path'],
        "result": {
            "extract": extracts,
            "tables": tables
        }
    }
    return result


def xls_save(data, file_name, sheet_name):
    workbook = xlwt.Workbook(encoding='utf-8')
    sheet = workbook.add_sheet(sheet_name)
    for row, item in enumerate(data):
        for col, value in enumerate(item):
            sheet.write(row, col, value)
    workbook.save(file_name)

