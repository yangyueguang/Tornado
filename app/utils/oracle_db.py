
import cx_Oracle
import conf
from utils.dlog import logger
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
                logger.info(conn_url)
                self._conn = cx_Oracle.connect(oc['username'], oc['password'], conn_url, encoding="UTF-8")
                self._conn.autocommit = True
                self.cursor = self._conn.cursor()
                self.cursor.rowfactory = lambda *args: dict(zip([d[0] for d in self.cursor.description], args))
                self.create_table()
                break
            except Exception as e:
                logger.error("connect to oracle error: %s", e, exc_info=e)
                retry -= 1

    # 创建表
    def create_table(self):
        sql = "select count(*) from user_tables where table_name =upper('extract_record');"
        exist = self.cursor.execute(sql)
        if exist <= 0:
            table_sql = open('utils/create_table.sql').read()
            self.cursor.execute(table_sql)

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

    def exist(self, sql):
        return self.cursor.execute(sql) > 0

    # 插入抽取记录表
    def insert_record(self, params, doc_id):
        exist_sql = "select count(*) from extract_record where doc_id = %s;" % doc_id
        if self.exist(exist_sql):
            sql = """
                update extract_record i 
                set t.age = '24', t.idnumber = '3503021994XXXXXXXX'
                where i.doc_id = %s;"""
        else:
            sql = """
            insert into extract_record
            values (%s, %s, %s, %s, %s)
            """
        self.insertBatch(sql, params)

    # 插入抽取文本字段表
    def insert_item(self, params, doc_id):
        exist_sql = "select count(*) from extract_item where doc_id = %s;" % doc_id
        if self.exist(exist_sql):
            sql = """
                        update extract_item i 
                        set t.age = '24', t.idnumber = '3503021994XXXXXXXX'
                        where i.doc_id = %s;"""
        else:
            sql = """
                    insert into extract_item
                    values (%s, %s, %s, %s, %s)
                    """
        self.insertBatch(sql, params)


    # 插入抽取表格字段表
    def insert_table(self, params, doc_id):
        exist_sql = "select count(*) from extract_table where doc_id = %s;" % doc_id
        if self.exist(exist_sql):
            sql = """
                        update extract_table i 
                        set t.age = '24', t.idnumber = '3503021994XXXXXXXX'
                        where i.doc_id = %s;"""
        else:
            sql = """
                    insert into extract_table
                    values (%s, %s, %s, %s, %s)
                    """
        self.insertBatch(sql, params)

    def commit(self):
        self._conn.commit()

    def __del__(self):
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, '_conn'):
            self._conn.close()


