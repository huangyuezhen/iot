"""
阿里大鱼短信发送Api

req=AlibabaAliqinFcSmsNumSendRequest(appkey, secret, url, partner_id)
 
req.extend="123456"
req.sms_type="normal"
req.sms_free_sign_name="注册验证"
req.sms_param=json.dumps(params)
req.rec_num="13000000000"
req.sms_template_code="SMS_5410290"
try:
    resp= req.getResponse()
    print(resp)
except Exception,e:
    print(e)

"""

import requests
import hashlib
from time import time
import json
import logging

from  conf import  settings
logger = logging.getLogger(__name__)


class RestApi(object):
    def __init__(self, key, secret, url="https://eco.taobao.com/router/rest", partner_id=""):
        self.key = key
        self.secret = secret
        self.url = url
        self.partner_id = partner_id

    def sign(self, params):
        #===========================================================================
        # '''签名方法
        # @param parameters: 支持字典和string两种
        # '''
        #===========================================================================
        if isinstance(params, dict):
            params = "".join(["".join([k, v]) for k,v in sorted(params.items())])
            params = "".join([self.secret, params, self.secret])
        sign = hashlib.md5(params.encode("utf-8")).hexdigest().upper()
        return sign

    def get_api_params(self):
        params = {}
        try:
            [params.__setitem__(k, getattr(self, k)) for k in self.get_param_names()]
        except AttributeError:
            raise Exception("Some parameters is needed for this api call")
        [params.__setitem__(k, getattr(self, k)) for k in self.get_option_names() if hasattr(self, k)]
        return params

    def getResponse(self, authorize=None):
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
        # headers = {"Content-Type":"application/x-www-form-urlencoded;charset=utf-8"}

        sys_params.update(params)
        logger.debug(json.dumps(sys_params))
        r = requests.post(self.url, params=sys_params, headers=headers)
        r.raise_for_status()
        return r.json()


class AlibabaAliqinFcSmsNumSendRequest(RestApi):
    def get_api_name(self):
        return "alibaba.aliqin.fc.sms.num.send"

    def get_param_names(self):
        return ['sms_type', 'sms_free_sign_name', 'rec_num', 'sms_template_code']

    def get_option_names(self):
        return ['extend', 'sms_param']


def send_msg(**kwargs):
    """
    向用户发送短信

    kwargs 需含以下两个参数
    msg ：{"operate": "找回密码", "code": _code}
    tel : 用户手机号

    """
    msg = kwargs["msg"]
    tel =  kwargs["tel"]

    appkey = settings["Alidayu"]["appkey"]
    secret = settings["Alidayu"]["secret"]

    req = AlibabaAliqinFcSmsNumSendRequest(appkey, secret)

    req.extend = "123456"
    req.sms_type = "normal"
    req.sms_free_sign_name = settings["Alidayu"]["sign_name"]
    req.sms_template_code =  settings["Alidayu"]["template_code"]
    req.sms_param = json.dumps(msg)
    req.rec_num = tel

    try:
        resp = req.getResponse()
        return resp
    except Exception:
        return  False


