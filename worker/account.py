

from db.iot import IOT
from common.error import IoTError
from common.util import  check_mobile,msg_send,sha256
from conf import settings

from  common.alidayu import  send_msg

MSG_URL = settings["MSG_URL"] #短信发送器 url


def add_account(session,cid,tel,_key,type ):
    IOT.add(session,IOT.account,account =tel,f_cid = cid,_key =_key,status =0 ,type =type)

def check_account(session,account,_key):
     """
     验证账号 密码
     """
     q =  IOT.find(session,IOT.account,account=account,_key =_key,one=True)
     cid ,_type =(None,None)
     if q :
        cid ,_type = q.f_cid,q.type

     return cid,_type


def check_new_old_key(old_key,new_key):
    """check new and old key
    """
    return True if old_key ==new_key  else False

def check_account_newkey_args(self):
    """
     检测  user 修改的参数
    """
    #kwargus = self.request.argumnets
    #account ,old_key = kwargus["account"][0],kwargus["_key"][0]
    account =  self.get_argument("account")
    old_key = self.get_argument("_key")
    new_key =  self.get_argument("new_key", None)

    """ sha256 转换用户输入密码"""
    if old_key: old_key = sha256(old_key).hexdigest()
    if new_key: new_key = sha256(new_key).hexdigest()



    return account,old_key,new_key

def bindmobile_args(self):
    """
     检测  user 修改的参数
    """
    #kwargus = self.request.argumnets
    #account ,old_key = kwargus["account"][0],kwargus["_key"][0]
    account =  self.get_argument("account")
    old_key = self.get_argument("_key")
    person =  self.get_argument('person', None)
    tel = self.get_argument("tel", None)
    _code =  self.get_argument("_code", None)


    """ sha256 转换用户输入密码"""
    if old_key: old_key = sha256(old_key).hexdigest()

    upkwargs = {}

    if tel and _check_mobile(tel):
        upkwargs.update({"tel": tel, "account": tel})
    if person:
        upkwargs.update({"person": person})

    return account,tel,old_key,_code,upkwargs




def  _check_mobile(tel):
    """
    """
    if tel and check_mobile(tel):
        return  True
    else :
        raise IoTError(400, reason="Invalid mobile number")

def  set_code(tel,_code,ex=120):
    """
    set virify code  to redis
    default expired in 120 seconds
    """
    IOT.StrictRedisOb.set(tel,_code,ex=ex)

def validate_code(tel,_code):
    """
    验证码是否有效
    """
    if  IOT.StrictRedisOb.get(tel):
        code =  IOT.StrictRedisOb.get(tel).decode()
        return True if code == _code else False
    return False



def check_payload(payload):
    """
    短信 载荷是否 有效
    """
    if  check_mobile(payload["mobile"]) and "msg" in payload.keys():
        return True
    return False


def _msg_send_o(payload,url = MSG_URL ):
    """
    南沙版  发送短信
    """
    if check_payload(payload):
        return msg_send(url,payload)

def _msg_send(payload ):
    """
    alidayu  message send
    """
    if check_payload(payload):
        tel = payload["mobile"]
        msg =  payload["msg"]
        return send_msg(tel=tel, msg=msg)


def update_key(sess,filter,upkwargs):
    """
    重置密码
    """
    return IOT.update(sess,IOT.account,filter,upkwargs)


