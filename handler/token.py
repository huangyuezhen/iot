'''
'''
from .base import BaseHandler
from common import token_formatters

from common.util import now,sha256
from common.authentication import  check_user_type
from worker import account as Account

class TokenHandler(BaseHandler):
    def post(self):
        """
        用户登录,获取token
        """
        account = self.get_argument("account")
        _key = self.get_argument("_key")

        """ sha256 加密密码"""
        _key = sha256(_key).hexdigest()


        cid, _type = Account.check_account(self.session, account, _key)

        ip = self.request.remote_ip

        if not cid:
            self.render_json_response(code=404, msg='please check input account & password')
            return

        _type = int(_type) if isinstance(_type,str) else _type

        """get  user type corporation or manager"""
        user_type = check_user_type (_type)

        expired_at = now(hours=1)

        token_formatters.load_keys()
        token = token_formatters.create_token(token_cid=cid, token_type=_type, remote_ip=ip, expires_at=expired_at)

        # self.set_cookie("token",token)
        self.render_json_response(token=token, code=200,user_code=_type,user = user_type,cid=cid, msg="OK")