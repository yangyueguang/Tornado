
import cx_Oracle
import conf
import datetime
from utils.xdict import Dict
from utils.dlog import dlog
# https://www.jianshu.com/p/79b92439fbbd
# 'docker run -d -P -p 1521:1521 -v /Users/supers/Documents/oracle:/home/oracle/data_temp --name oracle_11g  alexeiled/docker-oracle-xe-11g'
# alexeiled/docker-oracle-xe-11g
#   sid: xe
#   service name: xe
#   username: system
#   password: oracle

class Oracle(object):
    def __init__(self):
        retry = 3
        while retry > 0:
            try:
                oc = conf.ORACLE_CONF
                conn_url = "%s:%s/%s" % (oc['host'], oc['port'], oc['service'])
                dlog(conn_url)
                self._conn = cx_Oracle.connect(oc['username'], oc['password'], conn_url, encoding="UTF-8")
                self._conn.autocommit = True
                self.cursor = self._conn.cursor()
                self.cursor.rowfactory = lambda *args: dict(zip([d[0] for d in self.cursor.description], args))
                self.create_table()
                break
            except Exception as e:
                dlog(e, True, exc_info=e)
                retry -= 1

    # 创建表
    def create_table(self):
        sql = "select count(*) from user_tables where table_name = upper('extract_record')"
        exist = self.exist(sql)
        if not exist:
            self.execute_sql_file('create_table.sql')

    def execute_sql_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_list = f.read().split(';')[:-1]
            for x in sql_list:
                self.cursor.execute(x)
                print("执行成功sql: %s" % x)

    # query methods
    def queryAll(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def queryOne(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def queryBy(self, sql, nameParams={}):
        self.cursor.execute(sql, nameParams)
        return self.cursor.fetchall()

    def insertBatch(self, sql, nameParams=[]):
        self.cursor.prepare(sql)
        self.cursor.executemany(None, nameParams)
        self.commit()

    def update(self, sql):
        self.cursor.execute(sql)
        self.commit()

    def exist(self, sql):
        return self.queryOne(sql)[0] > 0

    def drop_table(self, table_name):
        sql = 'drop table %s cascade constraints' % table_name
        self.cursor.execute(sql)

    # 插入抽取记录表
    def insert_record(self, params):
        d = Dict(params)
        exist_sql = "select count(*) from extract_record where doc_id = %s;" % params.get('doc_id')
        if self.exist(exist_sql):
            sql = """
                update extract_record r 
                set r.hisotry_id = %s,
                r.doc_type = %s,
                r.pdf_path = %s,
                r.status = %s,
                r.error_code = %s,
                r.error_msg = %s,
                r.update_time	= %s,
                where r.doc_id = %s;""" % (d.hisotry_id, d.doc_type, d.pdf_path, d.status, d.error_code, d.error_msg, d.update_time, d.doc_id)
            dlog(sql)
            self.update(sql)
        else:
            params['create_time'] = datetime.datetime.now()
            sql = """
            insert into extract_record
            values (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.insertBatch(sql, params)

    # 插入抽取文本字段表
    def insert_item(self, params, doc_id):
        d = Dict(params)
        exist_sql = "select count(*) from extract_item where doc_id = %s;" % doc_id
        if self.exist(exist_sql):
            sql = """
                update extract_item r 
                set r.item_id = %s,
                r.item_name = %s,
                r.word = %s,
                r.confidence = %0.3f
                where r.doc_id = %s;""" % (d.item_id, d.item_name, d.word, d.confidence, doc_id)
            dlog(sql)
            self.update(sql)
        else:
            params['doc_id'] = doc_id
            sql = """
                    insert into extract_item
                    values (%s, %s, %s, %s, %s)
                    """
            self.insertBatch(sql, params)


    # 插入抽取表格字段表
    def insert_table(self, params, doc_id):
        d = Dict(params)
        exist_sql = "select count(*) from extract_table where doc_id = %s;" % doc_id
        if self.exist(exist_sql):
            sql = """
                update extract_table t 
                set t.table_id = %s,
                t.table_name = %s,
                t.table_path = %s
                where t.doc_id = %s;""" % (d.table_id, d.table_name, d.table_path, doc_id)
        else:
            params['doc_id'] = doc_id
            sql = """
                insert into extract_table
                values (%s, %s, %s, %s)
                """
            self.insertBatch(sql, params)

    def commit(self):
        self._conn.commit()

    def __del__(self):
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, '_conn'):
            self._conn.close()


extract = [{
                "terms_id": 20,
                "terms_name": "主标题",
                "word": "景气周期来临，黄鸡龙头佳境已至",
                "confidence": 1
            },{
                "terms_id": 21,
                "terms_name": "副标题",
                "word": "立华股份2019年半年报点评",
                "confidence": 1
            }]
table = [
            {
                "table_name": "表格-财务摘要",
                "table_id": "33",
                "excel_path": "/Users/supers/Desktop/tornado/app/static/7c5449b6-2537-11ea-a447-02420a000246/表格-财务摘要.xls"
            }
        ]
res = {
    "id": "2",
    "docType": "27",
    "history_id": 88,
    "status": "OK",
    "message": "",
    "pdf_path": "/upload/extract/4bd9f42a-338d-11ea-bea8-02420a00103c.pdf",
    "result": {}
}
if __name__ == '__main__':
    oracle = Oracle()
    res_dict = {
        'doc_id': res['id'],
        'hisotry_id': res['history_id'],
        'doc_type':	res['docType'],
        'pdf_path':	res['pdf_path'],
        'status': res['status'],
        'error_code':	200,
        'error_msg': res['message'],
        'update_time':	datetime.datetime.now()
    }
    oracle.insert_record(res_dict)
    # for item in extract:
    #     oracle.insert_item(item, '2')
    # for item in table:
    #     oracle.insert_table(item, '2')