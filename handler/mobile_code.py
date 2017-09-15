import tornado
import  json

from .base import  BaseHandler
from common.alidayu_tornado import get_req
from worker import account as Account
from common.util import generate_verify_code

class MobileCodeHanlder(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, _tel):
        """
        获取手机验证码
        采用tornado httpclient  异步发送短信

        """
        if _tel:
            self.request.arguments.update({"tel": [_tel]})

        tel = self.get_argument("tel")
        if Account._check_mobile(tel):
            _code = generate_verify_code()

            """set _code to redis"""
            Account.set_code(tel, _code)

            msg = {"operate": "找回密码", "code": _code}

            req = get_req(tel, msg)
            resp = yield req.get_response()  # send  msg

            resp = resp.decode() if isinstance(resp, bytes) else resp
            resp = json.loads(resp)

            if "error_response" in resp.keys():
                """ alidayu  error"""
                _reason = resp["error_response"]['sub_msg']
                self.render_json_response(code=501, msg=_reason)
            else:
                self.render_json_response(code=200, msg="OK")
