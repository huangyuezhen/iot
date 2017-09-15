"""
  标识管理部分
"""


import bson


from common import  util
from worker import corporation,iot_id as iot_id_w
from db.iot import  IOT
from .base import  BaseHandler
from common.authentication import  validate_requests,check_user_type,validate_manager_user




json_encoder = util.json_encoder
json_decoder = util.json_decoder

class IotIDHandler(BaseHandler):
    @validate_requests
    def get(self, _id, **kwargs):

        code = int(self.get_argument("token_type"))
        _user_type = check_user_type(code)
        kwargs = self.request.arguments


        if not _user_type in ["corporation", "manager"]:
            self.render_json_response(reason="TokenError,user_type not support", code=400)
            return

        if _user_type == "corporation":
            token_cid = str(self.get_argument("token_cid"))
            kwargs.update({"f_cid": [token_cid]})

        if _id :
            kwargs.update({"id":_id})
            out_put = iot_id_w.get_iot_id(sep="  AND ",**kwargs)

            self.render_json_response(res=out_put, msg = "OK",code=200)
            return

        out_put = iot_id_w.get_iot_id(sep="  AND ", **kwargs)

        count_sql = "select count(id)  from iot_id"
        total_count = iot_id_w.get_id_total_count(count_sql,**kwargs)

        self.render_json_response(res=out_put, total_count=total_count, code=200)


    @validate_requests
    def put(self,id):
        """
        corporation user: update  时间、地点
        manager user : update status
        _id 不更新
        """
        code = int(self.get_argument("token_type"))
        _user_type = check_user_type(code)

        if id :
            self.request.arguments.update({"id": [id]})

        if _user_type == "corporation":

            self.request.arguments.pop("cid", -1)  # 用户设置的cid 无效
            token_cid = str(self.get_argument("token_cid"))
            self.request.arguments.update({"cid": [token_cid]})

            if not iot_id_w.check_update_auth(self.request.arguments):
                """企业用户 不可修改status 属性  ,不满足时"""
                self.render_json_response(code=401, reason="Unauthorized")
                return


        """get filter  and update  arguments"""
        filters_ar, up_kwargs ,_id= iot_id_w.check_iot_id_update_args(self)

        if not up_kwargs:
            self.render_json_response(code=400,reason="new attributes not set")

        if _id:
            """filter by  _id list, other filters  invalid"""
            _row = IOT.update(self.session, IOT._id, IOT._id._id.in_(_id), up_kwargs, flag=False)
            self.render_json_response(code=200, msg="OK", effested_row=_row)

        elif  filters_ar:
            _row = IOT.update(self.session, IOT._id, filters_ar, up_kwargs)
            self.render_json_response(code=200, msg="OK", effested_row=_row)

        else:
            self.render_json_response(code=404, reason="has not chosen any object to update")


class IotIDApplyHandler(BaseHandler):
    """
      标识申请，与及返回申请信息供审核
    """

    @validate_requests
    def get(self,_id):

        code = int(self.get_argument("token_type"))
        _user_type =check_user_type(code)
        if _id :
            self.request.arguments.update({"id": [_id]})

        if not _user_type in[ "corporation","manager"]:
            return self.render_json_response(code=400, reason="currently not support user type")

        if _user_type ==  "corporation":
            """corporation user can only get its own info"""
            token_cid = str(self.get_argument("token_cid"))
            self.request.arguments.update({"f_cid": [token_cid]})

        kwargs = self.request.arguments
        res = iot_id_w.get_apply_info(**kwargs)

        total_count = iot_id_w.get_total_count(**kwargs)

        self.render_json_response(code=200, total_count=total_count,res=res)


    @validate_requests
    def post(self,*args):
        """
        提交 标识ID申请
        在 iot_id_apply 表添加申请记录
        """

        if not corporation.check_user_cid(self.request.arguments):
            """ 
            one can only  apply  iot_id use its own cid ,
            except manager user
            """
            self.render_json_response(code=401, reason="Unauthorized")
            return


        code = int(self.get_argument("token_type"))
        _user_type = check_user_type(code)
        if _user_type ==  "corporation":
            token_cid = self.get_argument("token_cid")
            self.request.arguments.update({"cid":[token_cid]})

        cid =self.get_argument("cid")
        category =self.get_argument("category")
        geocode =self.get_argument("geocode")
        id_num = int(self.get_argument("id_num"))
        ctime = self.get_argument("ctime",-1)

        version  = self.get_argument("version","01")
        apply_id = str(bson.ObjectId())

        if id_num > 1000000:
            self.render_json_response(code=400, reason="id_num can not over than 100w for once")
            return
        elif ctime!=-1:
            iot_id_w.add_iot_id_apply(self.session,f_cid =cid,category=category,id_num =id_num ,ctime =ctime,
                                    addr=geocode,version=version,apply_id =apply_id,status=0)
        else :
            iot_id_w.add_iot_id_apply(self.session, f_cid=cid, category=category, id_num=id_num, addr=geocode,
                                     version=version,apply_id =apply_id,status=0)

        self.render_json_response(code=200,msg="OK")



    @validate_manager_user
    def put(self, _apply_id, **kwargs):
        """
        只有管理员有权限
        审核申请，通过后，
        调用接口生成 _id
        """
        if _apply_id:
            self.request.arguments.update({"apply_id":[_apply_id]})

        apply_id = self.get_arguments("apply_id")  # list
        status = int(self.get_argument("status"))

        if iot_id_w.check_id_apply(self.session, apply_id, status):
            """当审核通过时（status ==1），包含 已被审核通过 的申请，报错"""
            self.render_json_response(code=400, reason="some applies has generated iot_id before")
            return


        if status == 2:
            """审核不通过"""
            IOT.update(self.session, IOT._id_apply, IOT._id_apply.apply_id.in_(apply_id), {"status": status},
                       flag=False)
            self.render_json_response(code=200, msg ="OK")
            return


        if status == 1:
            """审核通过"""
            qq = self.session.query(IOT._id_apply).filter(IOT._id_apply.apply_id.in_(apply_id))
            q_all = qq.all()

            """调用iot_id 生成接口,return f_apply_id(failed id ),s_apply_id(success id )"""
            f_apply_id ,s_apply_id= iot_id_w.generate_id_loop(self.session, q_all)

            IOT.update(self.session, IOT._id_apply, IOT._id_apply.apply_id.in_(s_apply_id), {"status": status},
                       flag=False)

            if f_apply_id :
                reason = " Error occurred when running,the running apply_id is {},".format(f_apply_id[0])
                self.render_json_response(code=400, reason=reason, error_apply_id=f_apply_id,succeess_apply_id = s_apply_id)
                return
            self.render_json_response(code=200, msg ="OK")
            return


        self.render_json_response(code=400, reason="Attribute erros,status attribute  currently not support ")

































