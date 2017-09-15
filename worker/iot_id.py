import datetime



from common import  util
from common.converter import to_36
from db.iot import  IOT
from worker import  corporation

json_encoder = util.json_encoder
json_decoder = util.json_decoder

INT_PARAMS =["status","offset", "page_size","id"]
STR_PARAMS = ["f_cid","apply_id","addr","category","_id","version","ctime","vender","serial_no"]


def add_iot_id_apply(sess, **kwargs):
    IOT.add(sess,IOT._id_apply, **kwargs)


def textsql_apply(fileds=["status","f_cid","apply_id","addr","category","id"],sep=' AND ',**kwargs):
    """
    textual  sql  bind params for  iot_apply and iot_corporation
    """
    query_list =[]
    for key in kwargs.keys():
        if key in fileds:
            query_list.append('a.{}=:{}'.format(key, key))

    return sep.join(query_list)

def textsql_iot_id (sep=' AND ',**kwargs):
    """
        textual  sql  bind params for  iot_apply and iot_corporation
        """
    query_list = []
    for key in kwargs.keys():
        if key in ["id","_id","version","ctime","addr","category","vender","serial_no","status","f_cid"]:
            query_list.append('{}=:{}'.format(key, key))

    return sep.join(query_list)

def get_total_count(count_sql ="select count(a.apply_id)  from iot_id_apply as a  join iot_corporation as b on  a.f_cid = b.cid ",sep= "  AND ",textsql=textsql_apply,**kwargs):
    """
    return total count of iot_id_apply infomation
        :param kwargs: self.request.arguments
        :return: total count
    """
    """pop page arguments ,if exist"""
    page = kwargs.pop("page", -1)
    page_size = kwargs.pop("page_size", -1)

    count_sql = count_sql
    return IOT.textualsql_get(count_sql, textsql, INT_PARAMS, STR_PARAMS,
                              page, page_size,sep=sep,t_count_flag=True, **kwargs)[0][0]

def get_id_total_count(_sql,sep="  AND ",**kwargs):
    count_sql = _sql
    textsql= textsql_iot_id
    return  get_total_count(count_sql= count_sql,textsql=textsql,sep= sep,**kwargs)

def  get_apply_info(**kwargs):
    """
    :param kwargs:  self.request.arguments
    :return: info if iot_id_apply
    """
    page = kwargs.pop("page", -1)
    page_size = kwargs.pop("page_size", -1)

    a_colum = ",".join(["a.id,a.addr","a.category","a.id_num","a.ctime","a.mtime","a.status+0 as apply_status","a.apply_id"])
    b_colum = ",".join(["b.name", "b.cid", "b.liable", "b.address", "b.site", "b.tel", "b.email", "b.status+0 as cor_status"])

    """"select statement"""
    _sql = "select  {},{} from iot_id_apply as a  join iot_corporation as b on  a.f_cid = b.cid ".format(
        a_colum, b_colum)

    return IOT.textualsql_get(_sql,textsql_apply,INT_PARAMS,STR_PARAMS,page,page_size,t_count_flag= False,**kwargs)

def get_iot_id(sep = " OR ",**kwargs):
    """
    :param kwargs: self.request.arguments
    :return:
    """
    page = kwargs.pop("page", -1)
    page_size = kwargs.pop("page_size", -1)
    colum = ",".join(["id","_id","version","ctime","addr as geocode","category","vender","serial_no","status+0 as status","f_cid as cid"])

    _sql = "select  {} from iot_id ".format(colum)


    return IOT.textualsql_get(_sql,textsql_iot_id, INT_PARAMS, STR_PARAMS, page, page_size ,
                              sep=sep,t_count_flag=False,**kwargs)



def check_id_apply(session,apply_id,status):
    """
    检测 iot_id_apply 表 该项申请是否 已被审核通过,
    避免同一申请两次生成 标识 _id
    """
    if status ==1:
        q = session.query(IOT._id_apply).filter(IOT._id_apply.apply_id.in_(apply_id),IOT._id_apply.status==1)
        if q.count()>0:
            return True
    return  False

def get_id_serial_enum(session,version,category,cid,table = IOT.id_serial):
    """
    从 iot_id_serial_no 表  获取最新的序列号，不存在时返回0
    """
    id_enum = session.query(table.id_enum).filter(table.version==version,table.category==category,table.f_cid==cid).first()
    if id_enum:
        return  id_enum[0]
    else :
        return  0

def _date(dtstr,fmt='%Y%m%d'):
    if isinstance(dtstr,datetime.datetime):
        d = datetime.datetime.strftime(dtstr.date(),fmt)
    else :
        d =datetime.date.strftime(datetime.datetime.strptime(dtstr,"%Y-%m-%d %H:%M:%S").date(),fmt)
    return  d


def iot_id_objects(version,corporation_id,geocode,ctime,id_enum,id_num,cid,category,table=IOT._id):
    """
    构造iot_id  对象
    """
    # short_id
    if version[0] in '0123456789':  # short_id
        brand = '{:0>4s}'.format(to_36(corporation_id))  # 序列号，转换位36进制
        _geocode = "0020" + geocode  # 区域编码 加4位国家码
        iot_id_obs = []

        for i in range(0, id_num):
            id_enum = id_enum + 1
            serial_no = '{:0>6s}'.format(to_36(id_enum))  # 转换为 6位字符串，不足补0
            _id = ''.join([version, ctime, _geocode, category, 'Z', brand, serial_no])
            iot_id_ob = table(_id=_id, version=version, ctime=ctime, addr=geocode, category=category, vender=brand,
                              serial_no=serial_no, f_cid=cid,status=0)
            iot_id_obs.append(iot_id_ob)
        return iot_id_obs ,id_enum
    else:
        return  None,id_enum



def  generate_iot_id(session,cid,id_num,geocode,ctime,category,version):
    """
    往表 iot_id  添加新记录，并更新或添加iot_serial 记录
    """

    if id_num > 1000000:
        return False
    else:

        # 获取 申请企业 ID
        corporation_id = corporation.get_corporation_orm(session, IOT.corporation.id,one =True, cid=cid,)[0]

        #  获取  当前企业当前 categoty 序列号
        id_enum_o = get_id_serial_enum(session, version, category, cid)

        #  调用 iot_id_objects()  函数生成 iot_id_objects
        iot_id_obs, id_enum = iot_id_objects(version, corporation_id, geocode, ctime, id_enum_o, id_num, cid,
                                                      category)


        if iot_id_obs:

            """ 往数据库添加 iot_id_objects"""
            IOT.add_all(session, iot_id_obs)

            if id_enum_o == 0:
                """ 序列号未有该项记录，添加"""
                IOT.add(session, IOT.id_serial, f_cid=cid, category=category, id_enum=id_enum,
                        version=version)
            else:
                """序列号已存在该项记录，更新"""
                IOT.update(session, IOT.id_serial, {"f_cid": cid, "category": category, "version": version},
                           {"id_enum": id_enum})

        return True


def generate_id_loop(session,objects):
    """
    批量
    往表 iot_id  添加新记录，并更新或添加iot_serial 记录
    objects : iot_id_apply query.all()
    """

    f_apply_id = []   # add  failed

    s_apply_id =[]   # add succeed

    for q in objects:
        """
        按申请次数，分批次生成_id
        """

        # 获取iot_id 生成参数
        geocode, category, ctime, id_num, version, cid = q.addr, q.category, q.ctime, q.id_num, q.version, q.f_cid

        apply_id_one = q.apply_id
        ctime = _date(ctime)

        # 调用 生成_id 接口
        ge_flag = generate_iot_id(session, cid, id_num, geocode, ctime, category, version)

        if not ge_flag:
            """
            出现 iot_id 没生成成功
            """
            f_apply_id.append(apply_id_one)
            break
        else :
            s_apply_id.append(apply_id_one)

    return  f_apply_id,s_apply_id


def check_update_auth(arguments):
    """
    检测用户是否有修改权限：
    1.企业用户只可修改自身标识ID 的时间、地点属性，参数cid 与token_cid 冲突时返回 Flase
    2. 企业用户 不可修改status 属性
    :param arguments: self.request.arguments
    :return: bool
    """
    if not corporation.check_user_cid(arguments):
        """企业用户cid 与token_cid 不一致，无操作权限"""
        return False
    else :
        _user_type = int(arguments["token_type"][0])
        new_status = int(arguments["new_status"][0]) if "new_status" in arguments.keys() else -1

        if ~_user_type & 1 and new_status!= -1:
            """企业用户cid 与token_cid 一致，但无更改status 操作权限"""
            return False
        else:
            return True



def check_iot_id_update_args(self):
    """
    检测更新参数
    :param self:
    :return:
    """

    up_kwargs = {}
    filters_ar = {}

    cid = self.get_argument("cid",-1)

    new_ctime = self.get_argument("new_ctime", None)
    new_addr = self.get_argument("new_geocode", None)
    new_status = int(self.get_argument("new_status", -1))

    category = self.get_argument("category", -1)
    addr = self.get_argument("old_geocode", -1)
    version = self.get_argument("version", -1)
    status = self.get_argument("old_status", -1)
    _id = self.get_arguments("_id")
    id = self.get_argument("id",-1)

    if new_ctime:
        up_kwargs.update({"ctime": new_ctime})
    if new_addr:
        up_kwargs.update({"addr": new_addr})
    if new_status != -1:
        up_kwargs.update({"status": new_status})

    if cid != -1:
        filters_ar.update({"f_cid": cid})
    if category != -1:
        filters_ar.update({"category": category})
    if addr != -1:
        filters_ar.update({"addr": addr})
    if version != -1:
        filters_ar.update({"version": version})
    if status != -1:
        filters_ar.update({"status": status})
    if id !=-1 :
        filters_ar.update({"id":id})

    return filters_ar,up_kwargs,_id





