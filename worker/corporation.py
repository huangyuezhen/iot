from sqlalchemy import text


from db.iot import IOT
from .account import  add_account
from common.util import sha256

INT_PARAMS = ["status", "blist", "employee_range", "offset", "page_size"]
STR_PARAMS = ["scope", "cid", "name", "address", "liable","id"]

def add_corporation( sesseion, **kwargs):
    assert kwargs

    IOT.add(sesseion, table=IOT.corporation, **kwargs)
    #return IOT.find(sesseion, table=IOT.corporation, cid=cid,one=True)

def add_corporation_slave(sess,**kwargs):
    #f_cid =kwargs.get("f_cid")
    IOT.add(sess,table =IOT.corporation_slave,**kwargs)
    #return IOT.find(sess, table=IOT.corporation_slave, f_cid=f_cid,one=True)

def get_corporation(sess,one ,**kwargs):#filter by status
    status =kwargs.get("status")
    page =kwargs.get("page")
    page_size =kwargs.get("page_size")
    return IOT.join_find(sess, table =(IOT.corporation,IOT.corporation_slave),one=one,
                               _key1=IOT.corporation.status,_value1= status,page=page,page_size=page_size)

def get_corporation_orm(seseeion,table,one,**kwargs):
    return IOT.find(seseeion,table,one =one,**kwargs)


def textsql_corporation(sep=' AND ',**kwargs):
    """
    textual  sql  bind params for  iot_corpotation and iot_corporation_slave
    """
    query_list =[]
    for key in kwargs.keys():
        if key in ["status","cid","name","address","liable","id"]:
            if key in ["status","cid","id"]:
                query_list.append('a.{}=:{}'.format(key, key))
            else :
                query_list.append('a.{} like :{}'.format(key, key))

        elif key in   ["scope","blist","employee_range"]:
            if key in ["blist","employee_range"]:
                query_list.append('b.{}=:{}'.format(key, key))
            else :
                query_list.append('b.{} like :{}'.format(key, key))
    return sep.join(query_list)


def get_total_count( **kwargs):
    """
    sql select 方法返回 选中记录总数
    :param kwargs: self.request.arguments
    :return: total_count
    """
    """pop page arguments ,if exist"""
    page = kwargs.pop("page", -1)
    page_size = kwargs.pop("page_size", -1)

    count_sql = "select count(a.cid) from iot_corporation as a join iot_corporation_slave as b on  a.cid = b.f_cid"
    return IOT.textualsql_get(count_sql,textsql_corporation,INT_PARAMS,STR_PARAMS,page,page_size,t_count_flag= True,**kwargs)[0][0]



def get_corporation_sql( sep ="  AND  ",**kwargs):
    """
    采用  sqlalchemy bind params to make  sql ,get corporation info
    :param kwargs:
    :return:
    """
    page = kwargs.pop("page", -1)
    page_size = kwargs.pop("page_size", -1)

    a_colum = ",".join(
        ["a.id,a.name", "a.cid", "a.liable ", "a.address", "a.site", "a.tel", "a.mobile","a.email", "a.status+0 as status","a.note"])
    b_colum = ",".join(["b.scope", "b.addr_pro","b.addr_city","b.addr_com","b.ctime", "b.blist+0 as blist", "b.employee_range"])

    """select  statement"""
    _sql = "select  {},{} from iot_corporation as a join iot_corporation_slave as b on  a.cid = b.f_cid".format(
        a_colum, b_colum)

    return IOT.textualsql_get(_sql,textsql_corporation,INT_PARAMS,STR_PARAMS,page,page_size,sep,t_count_flag=False,**kwargs)



def update_coration(sess,filter,up_argus):
     IOT.update(sess,IOT.corporation,filter,up_argus)
     cid =filter["cid"]
     return IOT.find(sess,IOT.corporation,one=True,cid =cid)

def update_coration_slave(sess,filter,up_argus):
    IOT.update(sess, IOT.corporation_slave, filter, up_argus)
    f_cid = filter["f_cid"]
    return IOT.find(sess, IOT.corporation_slave, one=True, f_cid=f_cid)

def check_manger_acnt(session,cid,status):
    """
    当更改 公司注册状态时，
    检测状态的变化值：
    1 ： 在user 新添加初始化用户
    4 ： uers 表status 更改为 4 ，账号被注销
    """
    if status ==1:
        q = IOT.find(session,IOT.corporation,one=True,cid=cid)
        mobile,_key = q.mobile ,q.cid[-6:]
        if IOT.find(session,IOT.account,one=True,f_cid =cid): #user exist ,udpate
            IOT.update(session, IOT.account, {"f_cid": cid}, {"status": 1})
        else : # not exist ,add
            """ sha256 加密用户密码"""
            _key = sha256(_key).hexdigest()
            add_account(session,cid,mobile,_key,0)
    elif status == 4:
        IOT.update(session,IOT.account,{"f_cid":cid},{"status":4})
    else:
        pass

def check_user_cid(arguments):
    """
    企业用户只可以修改自身信息，检测cid 与token_cid 是否一致
    param :arguments : self.requets.arguments
    """
    _user_type = int(arguments["token_type"][0])
    cid = arguments["cid"][0]  if "cid" in arguments.keys() else -1
    token_cid = arguments["token_cid"][0]

    if isinstance(cid,bytes):
        cid = cid.decode()
    if isinstance(token_cid, bytes):
        token_cid = token_cid.decode()

    if ~_user_type & 1 and cid != token_cid:
        return  False
    else :
        return True



def check_manager_uesr(arguments):
    """
    when update coporation status
    check user type ,if manager user or status ==-1  return tue else false
    企业不具备更改状态 属性权限时，返回false
    """
    _user_type = int(arguments["token_type"][0])
    status = arguments.get("status",-1)
    if _user_type &1 or status ==-1 :
        """管理员用户，_user_type &1 为真 """
        return True
    else :
       return  False
       #self.render_json_response(code =401,reason= "Unauthorized")


def corporation_update_args(self):
    """
    检测修改参数 涉及到哪个表，corporation or corporation_slave  or both
    """
    co_argus = {}
    slave_argu = {}

    # option args
    name = self.get_argument("name", -1)
    liable = self.get_argument("liable", -1)
    address = self.get_argument("address", -1)
    tel = self.get_argument("tel", -1)

    site = self.get_argument("site", -1)
    email = self.get_argument("email", -1)
    scope = self.get_argument("scope", -1)
    ctime = self.get_argument("ctime", -1)
    blist = int(self.get_argument("blist", -1))
    employee_range = self.get_argument("employee_range", -1)
    status = int(self.get_argument("status", -1))
    note =  self.get_argument("note", -1)

    # arguments  of corporation table
    if status != -1:
        co_argus.update({"status": status})
    if name != -1:
        co_argus.update({"name": name})
    if address != -1:
        addr_pro = self.get_argument("addr_pro")
        addr_city = self.get_argument("addr_city")
        addr_com = self.get_argument("addr_com")
        co_argus.update({"address": address})
        slave_argu.update({"addr_pro": addr_pro, "addr_city": addr_city, "addr_com": addr_com})
    if liable != -1:
        co_argus.update({"liable": liable})
    if tel != -1:
        co_argus.update({"tel": tel})

    if site != -1:
        co_argus.update({"site": site})
    if email != -1:
        co_argus.update({"email": email})
    if note!=-1 :
        co_argus.update({"note": note})

    # 属于corporation_slave 的参数
    if scope != -1:
        slave_argu.update({"scope": scope})
    if ctime != -1:
        slave_argu.update({"ctime": ctime})
    if blist != -1:
        slave_argu.update({"blist": blist})
    if employee_range != -1:
        slave_argu.update({"employee_range": employee_range})

    return  co_argus,slave_argu













