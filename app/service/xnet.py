#! /usr/bin/env python
# coding: utf-8

from tornado import gen, httpclient


class XRequest(object):
    @gen.coroutine
    def http_request(self, url, **args):
        try:
            client = httpclient.AsyncHTTPClient()
            response = yield client.fetch(url, **args)
        except Exception as e:
            raise gen.Return({})
        else:
            raise gen.Return(response.body)

    @gen.coroutine
    def http_get(self, url, **args):
        body = yield self.http_request(url=url, method='GET', **args)
        raise gen.Return(body)

    @gen.coroutine
    def http_post(self, url, params, **args):
        body = yield self.http_request(url=url, method='POST', body=params, **args)
        raise gen.Return(body)

    def http_put(self):
        raise NotImplemented

    @gen.coroutine
    def user_validate(self, params):
        headers = {
            'Accept': 'text / html, application / xhtml + xml, application / xml',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh - CN, zh',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }
        response_body = yield self.http_get('http://www.baidu.com?' + params, headers=headers)
        raise gen.Return(response_body)
