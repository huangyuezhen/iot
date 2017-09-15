# -*-coding:utf-8 -*-
import pymysql
import requests
import re

def ConnectToMysqlDb():
    conn = pymysql.connect(
        host='172.16.44.2',
        port=3306,
        user='root',
        passwd='cnicggis_!@#',
        db='iot',
        charset='utf8'
    )
    cur = conn.cursor()
    return conn,cur
def iot_corporation(conn,cur):
    bd_sense_num_his = 'create table iot_corporation (' \
                       'id int not null auto_increment,' \
                       'name varchar(100) not null comment "企业名称，最长255字节", ' \
                       'cid varchar(64) not null comment "社会信用代码",' \
                       'liable varchar(64) not null comment "公司法人",' \
                       'address varchar(255) not null comment "收件地址？公司注册地址？",' \
                       'site varchar(128) not null  default ""  comment "官网地址",' \
                       'tel varchar(32) not null comment "联系电话",' \
                       ' email varchar(64) not null default "" comment "电子邮箱地址",' \
                       'status BIT(32) not null  comment "审核状态",'\
                       'note varchar(255) not null default "" comment "备注",' \
                       'primary key (id),' \
                       'unique key uidx_name(name),' \
                       'unique key uidx_cid(cid))engine=InnoDB auto_increment=10000 DEFAULT CHARSET=utf8mb4;'

    cur.execute(bd_sense_num_his)
    conn.commit()

def iot_corporation_slave():
    bd_sense_num_his ='create table   iot_corporation_slave(' \
                      'id int not null auto_increment,' \
                      'scope varchar(255) not null default "" ,' \
                      'addr_pro int not null ,' \
                      'addr_city int not null ,' \
                      'addr_com int not null comment "区编号",' \
                      'ctime datetime not null comment  DEFAULT CURRENT_TIMESTAMP "注册时间",' \
                      ' blist BIT(32) not null default 0 comment "公司是否上市？0：未设置；1：上市；2：未上市",' \
                      'employee_range tinyint not null default 0 comment "0:未设置",' \
                      'f_cid varchar(64) not null comment "社会信用代码",' \
                      'primary key (id),foreign key (f_cid) references iot_corporation(cid) on delete cascade' \
    ')engine=InnoDB DEFAULT CHARSET=utf8mb4;'
    cur.execute(bd_sense_num_his)
    conn.commit()

def iot_id(conn, cur):
    bd_sense_num_his ='create table iot_id (' \
                      'id int not null auto_increment comment "自增id",' \
                      '_id varchar(128) not null comment "物品标识",' \
                      'version varchar(12) not null comment "标识编码版本",' \
                      'ctime TIMESTAMP not null DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP comment "时间戳",' \
                      'addr varchar(24) not null comment "地址编码",' \
                      'category varchar(32) not null comment "物品类别",' \
                      'vender varchar(64) not null comment "厂家、供应商",' \
                      'serial_no varchar(128) not null comment "商品编号",' \
                      'status BIT(32) not null  comment "商品状态",' \
                      'f_cid varchar(64) not null comment "社会信用代码",' \
                      'foreign key (f_cid) references iot_corporation(cid) on delete cascade,' \
                      'primary key (id),' \
                      'unique key uidx_id(_id)' \
                      ')engine=InnoDB DEFAULT CHARSET=utf8mb4;'

    cur.execute(bd_sense_num_his)
    conn.commit()
def iot_query(conn, cur):
    bd_sense_num_his ='create table iot_query (' \
                      'id int not null auto_increment comment "自增id",' \
                      '_id varchar(128) not null comment "物品标识",' \
                      'ip varchar(64) not null comment "用户IP地址",' \
                      ' model varchar(64) not null comment "查询设备机型",' \
                      'address point not null comment "地理坐标",' \
                      'qtime TIMESTAMP not null default current_timestamp comment "查询时间戳",' \
                      'primary key (id)' \
                      ')engine=InnoDB DEFAULT CHARSET=utf8mb4;'
    cur.execute(bd_sense_num_his)
    conn.commit()
def create_corparetion():
    sql ='create table iot_employee_scale (' \
         'id int not null auto_increment,' \
         'range varchar(128) not null comment "员工规模",' \
         'primary key (id)' \
         ')engine=InnoDB DEFAULT CHARSET=utf8mb4;'
    cur.execute(sql)
    conn.commit()
def iot_id_apply(conn,cur):
    bd_sense_num_his ='create table iot_id_apply (' \
                      'id int not null auto_increment comment "自增id",' \
                      'addr varchar(24) not null comment "地址编码",' \
                      'category varchar(32) not null comment "物品编码",' \
                      'f_cid varchar(64) not null comment "社会信用代码",' \
                      'id_num int not null comment "申请标识数量",' \
                      'version VARCHAR (4) not null default "01",' \
                      'mtime TIMESTAMP not null default current_timestamp comment "申请时间戳" ,' \
                      'ctime TIMESTAMP not null default current_timestamp comment "生产日期时间戳",status BIT (32) not null default 0 comment "申请状态",'\
                      'foreign key (f_cid) references iot_corporation(cid) on delete cascade,' \
                      'primary key (id)' \
                      ')engine=InnoDB  auto_increment=10000 DEFAULT  CHARSET=utf8mb4;'
    cur.execute(bd_sense_num_his)

def iot_user(conn, cur):
    bd_sense_num_his = 'create table iot_user (' \
                       'id int not null auto_increment comment "自增id",' \
                       'account varchar(24) not null comment "账号",' \
                       '_key varchar(32) not null comment "密码",' \
                       'f_cid varchar(64) not null comment "社会信用代码",' \
                       'person varchar(24) DEFAULT null comment "联系人",' \
                       'tel VARCHAR (24) DEFAULT null  comment "联系电话",' \
                       'status bit(32) DEFAULT 1 COMMENT "账号状态", '\
                       'mtime TIMESTAMP not null default current_timestamp comment "申请时间戳" ,' \
                       'foreign key (f_cid) references iot_corporation(cid) on delete cascade,' \
                       'primary key (id),' \
                       'unique key uidx_fcid(f_cid),' \
                       'unique key uidx_account(account)' \
                       ')engine=InnoDB  auto_increment=10000 DEFAULT  CHARSET=utf8mb4;'
    cur.execute(bd_sense_num_his)
    conn.commit()
def iot_id_serial_no(conn,cur):
    bd_sense_num_his = 'create table iot_id_serial_no (' \
                       'id int not null auto_increment comment "自增id",' \
                       'category varchar(32) not null comment "物品编码",' \
                       'f_cid varchar(64) not null comment "社会信用代码",' \
                       'id_bnum int not null comment "标识起始值",' \
                       'id_enum int not null comment "标识结束值",' \
                       'version VARCHAR (4) not null default "01",' \
                       'mtime TIMESTAMP not null default current_timestamp comment "申请时间戳" ,' \
                       'foreign key (f_cid) references iot_corporation(cid) on delete cascade,' \
                       'primary key (id)' \
                       ')engine=InnoDB  auto_increment=10000 DEFAULT  CHARSET=utf8mb4;'
    cur.execute(bd_sense_num_his)
    conn.commit()

def insert_into_corparetion_slave():
    sql ='insert into iot_employee_scale(id, range) values(0, "未设置"),(1, "50人 以下"), (2, "50-100 人"), (3, "100-500 人"), (4, "500-2000 人"), (5, "2000 人以上");'
    cur.execute(sql)
    conn.commit()
if __name__ == '__main__':
    conn, cur =ConnectToMysqlDb()
    #iot_corporation(conn, cur)
    #iot_corporation_slave()
    #iot_id(conn, cur)
    #iot_query(conn, cur)
   # create_corparetion()
    '''sql = 'create table iot_id_apply (id int not null auto_increment comment "自增id",f_cid varchar(64) not null comment "社会信用代码",' \
                       'foreign key (f_cid) references iot_corporation(cid) on delete cascade,' \
                       'ctime TIMESTAMP not null DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP comment "时间戳",' \
                       'addr varchar(24) not null comment "地址编码",' \
                       'category varchar(32) not null comment "物品类别",' \
                       'status BIT(32) not null  comment "审核状态",'\
                       'id_num int not null ' \
                       'primary key (id)' \
                      ')engine=InnoDB DEFAULT CHARSET=utf8mb4;'''''
    #cur.execute("CREATE TABLE users (id INT, name VARCHAR(18))")
    #cur.execute(sql)
    #conn.commit()
    #iot_id_apply(conn, cur)
    #iot_id_serial_no(conn, cur)
    #insert_into_corparetion_slave()
    iot_user(conn,cur)