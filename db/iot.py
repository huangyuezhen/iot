

from sqlalchemy.ext.automap import automap_base
from sqlalchemy import text


from sqlalchemy import bindparam
from sqlalchemy import Integer, String
import redis

from db.mariadb import ENGINE,session_scope
from .redis import  Redis
from common.util import  _to_int


Base = automap_base()
Base.prepare(ENGINE, reflect=True)



class IOT(object):
    def __init__(self,Base,POOL):
        self.corporation = Base.classes.iot_corporation
        self.corporation_slave = Base.classes.iot_corporation_slave
        self._id = Base.classes.iot_id
        self._id_apply = Base.classes.iot_id_apply
        self.id_serial = Base.classes.iot_id_serial_no
        self.account = Base.classes.iot_user

        self.StrictRedisOb =  redis.StrictRedis(connection_pool= POOL)

    def add(self,sesseion,table, **kwargs):
        assert kwargs
        with session_scope(sesseion) as  session:
            newob = table(**kwargs)
            session.add(newob)
    def add_all(self,sesseion, obs =[]):
        assert obs
        with session_scope(sesseion) as  session:
            session.add_all(obs)
    def update(self,sesseion,table,filters,up_argus,flag =True):
        assert up_argus,filters
        with session_scope(sesseion) as session :
            if flag:
                row = session.query(table).filter_by(**filters).update(up_argus,synchronize_session=False)
            else :
                row = session.query(table).filter(filters).update(up_argus,synchronize_session=False)

            return row

    def  find(self,sesseion,table,one=False,*args,**kwargs):
        assert kwargs
        page ,page_size =args if args else (1,15)
        page =int(page)
        page_size =int(page_size)
        with session_scope(sesseion) as session:
            q =session.query(table).filter_by(**kwargs)
            if one :
                return q.first()
            elif page >0 and page_size>0 :
                offset = (page - 1) * page_size
                q = q.offset(offset).limit(page_size)
                return  q

    def join_find(self,sesseion,table=(),one=True,**kwargs):
        """
        has been deserted
        """
        assert  kwargs
        page, page_size = int(kwargs.get("page",1)) ,int(kwargs.get("page_size",15))
        _ob =kwargs.get("_key1")
        _value =kwargs.get("_value1")

        with session_scope(sesseion) as session:
            table1,table2 =table
            if _value == -1:
                q =session.query(table1,table2).join(table2)
            else :
                q = session.query(table1, table2).join(table2).filter(_ob == _value)

            if one:
                return q.first()
            elif page > 0 and page_size > 0:
                total_count = q.count()
                offset = (page - 1) * page_size
                q = q.offset(offset).limit(page_size).all()
                return q,total_count

    def sql_find(self,_sql,**kwargs):

         page, page_size = int(kwargs.get("page", 1)), int(kwargs.get("page_size", 15))
         if page > 0 and page_size > 0:
             offset = (page - 1) * page_size
             _sql =" limit".join([_sql," {},{}".format(offset,page_size)])

         res = ENGINE.execute(_sql)
         output = res.fetchall()
         res.close()
         return output

    def sql_find_bind_param(self,_sql):

         res = ENGINE.execute(_sql)
         output = res.fetchall()
         res.close()
         return output


    def page_bind_params(self,page, page_size, _sql, **kwargs):
        """
        sqlalchemy   bind params  to prevent sql injection
        bind page params
        if  page  or page_size is None ,set default(1,15)
        to prevent too much out_out to return

        """
        if isinstance(page,list):
            page =_to_int(page[0])
        if isinstance(page_size,list) :
            page_size = _to_int(page_size[0])

        if page < 0 or page_size < 0:
            page =1
            page_size =15

        offset = (page - 1) * page_size
        _limit_sql = " limit :offset,:page_size "
        _sql = " ".join([_sql, _limit_sql])
        kwargs.update({"offset": [offset], "page_size": [page_size]})

        return _sql, kwargs

    def sql_bindparams(self,int_params_list,str_params_list,**kwargs):
        """
        to  prevent sql injection ,use sql bindparams
        :param kwargs:  self.request.arguments
        :return: a list of  bindparams
        """
        b_p = []

        for key, _value in kwargs.items():

            if isinstance(_value,list):
                _value = _value[0].decode() if isinstance(_value[0], bytes) else _value[0]
            elif isinstance(_value,bytes):
                _value = _value.decode()

            if key in  int_params_list:
                o = bindparam(key, value=_value, type_=Integer)
            elif key in  str_params_list:
                o = bindparam(key, value=_value, type_=String)
            else:
                continue
            b_p.append(o)
        return b_p


    def textualsql_get(self,_sql,textsql_where,int_params_list,str_params_list,page,page_size,
                       sep="  AND ",t_count_flag =True,**kwargs):
        """
        textualsql selct to prevent sql injection
        """
        """pop page arguments ,if exist"""
        kwargs.pop("page", -1)
        kwargs.pop("page_size", -1)


        """ get  where condition statement"""
        where_condition = textsql_where(sep=sep, **kwargs)


        """select statement join filters"""
        if where_condition:
            _sql = "  WHERE ".join([_sql, where_condition])

        if not t_count_flag :
            """ not get total count """
            _sql, kwargs =self.page_bind_params(page, page_size, _sql, **kwargs)

        """where condition  bind params"""
        count_b_q = self.sql_bindparams(int_params_list, str_params_list, **kwargs)

        stmt = text(_sql, bindparams=count_b_q)

        return self.sql_find_bind_param(stmt)

IOT = IOT(Base,Redis.connection_pool())




