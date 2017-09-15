#!/usr/bin/python3

from __future__ import absolute_import, division, print_function, with_statement

import json
import hashlib
from time import time
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from tornado import httpclient, gen


from  conf import  settings

class BaseSendRequest(object):

    SERVER_NAME = 'base'

    def __init__(self, key, secret, url):
        self.key = key
        self.secret = secret
        self.url = url

    def get_api_params(self):
        params = {}
        try:
            [params.__setitem__(k, getattr(self, k))
             for k in self.get_param_names()]
        except AttributeError:
            raise Exception("Some parameters is needed for this api call")
        [params.__setitem__(k, getattr(self, k))
         for k in self.get_option_names() if hasattr(self, k)]
        return params


class AliDaYuSendRequest(BaseSendRequest):
    """
      **Example:** 
          ```
            @gen.coroutine
            def main():
                key = ""
                secret = ""
                req = AliDaYuSendRequest(key, secret)
                req.extend = "123456"
                req.sms_type = "normal"
                req.sms_free_sign_name = "来信"
                req.sms_param = json.dumps({"code": "123456", "time": "10"})
                req.rec_num = "13751744759"
                req.sms_template_code = "SMS_69170500"
                try:
                    resp = yield req.get_response()
                    # resp is instance of class `tornado.httpclient.Response`
                    print(resp.body)
                except Exception:
                    import traceback
                    traceback.print_exc()
        
            io_loop = ioloop.IOLoop.current()
            io_loop.run_sync(main)
          
          ```
    """

    SERVER_NAME = 'alidayu'

    def __init__(self, key, secret, url="https://eco.taobao.com/router/rest", partner_id=""):
        self.key = key
        self.secret = secret
        self.url = url
        self.partner_id = partner_id
        self.client = httpclient.AsyncHTTPClient()
        self.sms_type = "normal"

    def sign(self, params):
        """签名方法
        :param params: 支持字典和string两种
        :return: 签名
        """
        if isinstance(params, dict):
            params = "".join(["".join([k, v]) for k,v in sorted(params.items())])
            params = "".join([self.secret, params, self.secret])
        sign = hashlib.md5(params.encode("utf-8")).hexdigest().upper()
        return sign

    @gen.coroutine
    def get_response(self, authorize=None):
        sys_params = {
            "method": self.get_api_name(),
            "app_key": self.key,
            "timestamp": str(int(time() * 1000)),
            "format": "json",
            "v": "2.0",
            "partner_id": self.partner_id,
            "sign_method": "md5",
        }
        if authorize is not None:
            sys_params['session'] = authorize
        params = self.get_api_params()
        sign_params = sys_params.copy()
        sign_params.update(params)
        sys_params['sign'] = self.sign(sign_params)
        headers = {
            'Content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            "Cache-Control": "no-cache",
            "Connection": "Keep-Alive",
        }
        sys_params.update(params)
        r = yield self.client.fetch(self.url, method="POST",
                                    body=urlencode(sys_params), headers=headers)
        raise gen.Return(r.body)

    @staticmethod
    def get_api_name():
        return "alibaba.aliqin.fc.sms.num.send"

    @staticmethod
    def get_param_names():
        return ['sms_type', 'sms_free_sign_name', 'rec_num', 'sms_template_code']

    @staticmethod
    def get_option_names():
        return ['extend', 'sms_param']


def get_req(tel,msg):

    """
    :return  AliDaYuSendRequest  to Handle send msg

    """

    appkey = settings["Alidayu"]["appkey"]
    secret = settings["Alidayu"]["secret"]

    sign_name =settings["Alidayu"]["sign_name"]
    template_code = settings["Alidayu"]["template_code"]

    req = AliDaYuSendRequest(appkey, secret)
    req.extend = "123456"
    req.sms_type = "normal"
    req.sms_free_sign_name = sign_name
    req.sms_param = json.dumps(msg)
    req.rec_num = tel
    req.sms_template_code = template_code

    return  req









