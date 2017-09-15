import json
import tornado


from .base import  BaseHandler
from worker import account as Account

from db.iot import IOT
from common.util import sha256,generate_verify_code
from common.authentication import  validate_requests
from common.alidayu_tornado import get_req
from worker import account as Account




class AccountHandler(BaseHandler):
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


    def post(self,*kwargs):
        """
        短信验证码找回密码，设置新的密码
        """
        tel =self.get_argument("tel")
        _code = self.get_argument("_code")
        new_psw = self.get_argument("new_psw")

        if not  Account.validate_code(tel,_code):
            self.render_json_response(code = 400 ,msg = "Invalid _code")
            return

        """ sha256 加密密码"""
        new_psw = sha256(new_psw).hexdigest()

        Account.update_key(self.session,{"account":tel},{"_key":new_psw})
        self.render_json_response(code=200,msg="OK")


    @validate_requests
    def put(self,_acccount):
        """
        修改密码，补
        """
        if _acccount:
            self.request.arguments.update({"account": [_acccount]})

        """检测参数，获得 目标参数"""
        account, old_key, new_key = Account.check_account_newkey_args( self)

        if Account.check_new_old_key(old_key, new_key):
            self.render_json_response(code=400, msg="new_key is the same as old_key")
            return
        elif not new_key:
            self.render_json_response(code=400, msg="nothing to update")
            return

        elif not  Account.check_account(self.session, account, old_key)[0]:
            """原来的账号密码是否正确"""
            self.render_json_response(code=401, msg="Unauthorized")
        else:
            IOT.update(self.session, IOT.account, {"account": account, "_key": old_key},{"_key": new_key})
            self.render_json_response(code=200, msg="OK")



class AccountSupp(BaseHandler):
    @validate_requests
    def put(self, _acccount):
        """
        绑定、修改 联系人、联系手机。
        """
        if _acccount:
            self.request.arguments.update({"account": [_acccount]})

        """检测参数，获得 目标参数"""
        account, tel, old_key, _code, upkwargs = Account.bindmobile_args(self)

        if not  Account.validate_code(tel,_code):
            self.render_json_response(code = 400 ,msg = "Invalid _code")
            return

        if not upkwargs:
            self.render_json_response(code=400, msg="nothing to update")
            return

        elif not Account.check_account(self.session, account, old_key)[0]:
            """原来的账号密码是否正确"""
            self.render_json_response(code=401, msg="Unauthorized")
        else:
            IOT.update(self.session, IOT.account, {"account": account, "_key": old_key}, upkwargs)
            self.render_json_response(code=200, msg="OK")






class Account_manager(BaseHandler):
    def post(self):
        """
        平台管理员用户创建，后台人员使用，部署后关掉此接口
        """
        _key = self.get_argument("_key")

        _type =2

        tel = self.get_argument("tel")
        cid = self.get_argument("cid","")
        AccountHandler.add_account(self.session, cid, tel, _key, _type)
        self.render_json_response(code=200,msg="OK")

