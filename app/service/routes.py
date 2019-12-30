#! /usr/bin/env python
# coding: utf-8


routes = [
        (r"/demo/sync", "handlers.demo.SyncTestHandler"),  # Tornado 同步测试
        (r"/demo/async", "handlers.demo.AsyncTestHandler"),  # Tornado 异步测试
        (r"/demo/userlogin", "handlers.demo.UserLoginHandler"),   # 用户登录
        (r"/demo/uservisit", "handlers.demo.UserVisitHandler"),   # 登录测试
        (r"/demo/asyncdownload", "handlers.demo.AsyncDownloadHandler"),  # 大文件异步下载
]
