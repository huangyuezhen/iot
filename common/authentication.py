
from . import token_formatters
from .error import  TokenError

def validate_requests(func):
    """
     验证用户回传的token,监测是否有权限，
     同时把token里的cid /token_type 信息写进self.request.arguments
     装饰器函数
    """
    def _deco(*args, **kwargs):
        _self =args[0]
        token = _self.get_argument("token")
        #token = _self.request.arguments.pop("token")[0]
        try :
            payload =  token_formatters.validate_token(token,_self.request)
            if payload:

                cid ,_type = payload["token_cid"],payload["token_type"]
                _self.request.arguments.setdefault("token_cid", []).extend([cid,])
                _self.request.arguments.setdefault("token_type", []).extend([str(_type), ])
            else :
                raise  TokenError

            ret = func(*args, **kwargs)

        except TokenError:
            _self.render_json_response(code=401, reason="Unauthorized")
        else :
            return ret

    return _deco



def check_user_type(code):
    """
    用户类型检测

    """
    _user_type = code

    if not isinstance(code, int):
        raise TypeError

    if ~_user_type &1 :
        return  "corporation"
    elif _user_type  &1 :
        return  "manager"
    else :
        return  None


def validate_manager_user(func):
    """
     验证是否 管理员用户，
     同时把token里的cid /token_type 信息写进self.request.arguments
     装饰器函数
    """
    def _deco(*args, **kwargs):
        _self =args[0]
        token = _self.get_argument("token")
        #token = _self.request.arguments.pop("token")[0]
        try :
            payload =  token_formatters.validate_token(token,_self.request)
            if int(payload["token_type"])   & 1:
                cid ,_type = payload["token_cid"],payload["token_type"]
                _self.request.arguments.setdefault("token_cid", []).extend([cid,])
                _self.request.arguments.setdefault("token_type", []).extend([str(_type), ])
            else :
                raise TokenError
            ret = func(*args, **kwargs)

        except TokenError:
            _self.render_json_response(code=401, reason="Unauthorized")
        else :
            return ret

    return _deco
