#! /usr/bin/env python
# coding: utf-8


routes = [
        (r"/demo/sync", "service.handler.SyncTestHandler"),  # Tornado 同步测试
        (r"/demo/async", "service.handler.AsyncTestHandler"),  # Tornado 异步测试
        (r"/demo/userlogin", "service.handler.UserLoginHandler"),   # 用户登录
        (r"/demo/uservisit", "service.handler.UserVisitHandler"),   # 登录测试
        (r"/demo/asyncdownload", "service.handler.AsyncDownloadHandler"),  # 大文件异步下载
        (r'/extract', 'service.handler.Extract')  # 正式业务pdf抽取
]
