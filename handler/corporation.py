"""
企业信息部分接口
"""

from .base import BaseHandler
from common.util import  now
from worker import corporation
from common.authentication import  validate_requests,check_user_type


class CorporationHandler(BaseHandler):

    @validate_requests
    def get(self,_id):
        """
        根据请求条件返回公司注册信息
        """
        code = int(self.get_argument("token_type"))
        _user_type = check_user_type(code)

        sql = "select name ,address from tabela where id =12"



        if not _user_type in ["corporation", "manager"]:
            self.render_json_response(reason="TokenError,user_type not support", code=400)
            return

        if _id:
            kwargs = {"cid": [_id],"id":[_id]}

            out_put = corporation.get_corporation_sql(sep ="  OR  ",**kwargs)

            _cid = out_put[0][2] if out_put else -1

            self.request.arguments.update({"cid": [_cid]})

            if not corporation.check_user_cid(self.request.arguments):
                """token_cid 与cid 不一致，报错"""
                self.render_json_response(code =401,reason="Unauthorized")
                return

            self.render_json_response(res=out_put, code=200)
            return



        if _user_type == "corporation":
            """
            企业用户
            """
            token_cid = str(self.get_argument("token_cid"))

            kwargs ={"cid":[token_cid]}

            out_put = corporation.get_corporation_sql(**kwargs)
            total_count = corporation.get_total_count(**kwargs)

            self.render_json_response(res=out_put,total_count = total_count, code=200)

        elif _user_type == "manager":
            """
            管理员用户
            """
            _kwargs = self.request.arguments

            out_put = corporation.get_corporation_sql(**_kwargs)
            total_count = corporation.get_total_count(**_kwargs)
            self.render_json_response(res=out_put,total_count = total_count, code=200)




    def post(self,*args):
        """
             企业注册，初始化状态为 0，未审核,添加成功后，返回当前注册值
        """
        self.set_header('Access-Control-Allow-Origin', '*')
        name = self.get_argument("name")
        cid =self.get_argument("cid")
        liable = self.get_argument("liable")
        address = self.get_argument("address")
        tel =self.get_argument("tel")
        mobile = self.get_argument("mobile")
        addr_pro = self.get_argument("addr_pro")
        addr_city = self.get_argument("addr_city")
        addr_com = self.get_argument("addr_com")

        _now =now()
        site =self.get_argument("site")
        email =self.get_argument("email","")
        scope =self.get_argument("scope","")
        ctime =self.get_argument("ctime",_now)
        blist =int (self.get_argument("blist",0))
        employee_range =self.get_argument("employee_range")

        corporation.add_corporation(self.session,name =name,cid =cid ,liable=liable,address=address,tel=tel,mobile = mobile,site =site,email=email,status =0)
        corporation.add_corporation_slave(self.session,scope=scope,f_cid =cid, addr_pro=addr_pro, addr_city=addr_city,
                                                                      addr_com=addr_com, ctime=ctime, blist=blist,
                                                                     employee_range=employee_range)

        """返回注册内容"""
        kwargs ={"cid":cid}
        out_put = corporation.get_corporation_sql(**kwargs)

        self.render_json_response(res=out_put, code=200,msg="OK")



    @validate_requests
    def put(self,_cid):
        """
           1.修改注册公司审核状态、属性等

        """
        if _cid :
            self.request.arguments.update({"cid":_cid})

        if not corporation.check_user_cid(self.request.arguments) or not corporation.check_manager_uesr(
                self.request.arguments):
            """
               检测 
               1. 企业用户只可修改自身信息，cid =token_cid
               2. 企业用户不可更改 状态属性
               不满足上述两个条件，返回 Unauthorized
            """
            self.render_json_response(code=401, reason="Unauthorized")
            return


        cid = self.get_argument("cid")
        status = int(self.get_argument("status",-1))


        """get update arguments"""
        co_argus,slave_argu =corporation.corporation_update_args(self)

        if co_argus:
             corporation.update_coration(self.session, {"cid": cid}, co_argus)
        if slave_argu:
             corporation.update_coration_slave(self.session, {"f_cid": cid}, slave_argu)

        """监测是否需要 操作 iot_user 表,add  or update"""
        corporation.check_manger_acnt(self.session, cid, status)

        """返回更新后的结果"""
        kwargs = {"cid": cid}
        out_put = corporation.get_corporation_sql(**kwargs)

        self.render_json_response(res=out_put, code=200,msg="OK")



