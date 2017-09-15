# IoT系统数据库设计标

| version | author       | date       | describe                                 |
| ------- | ------------ | ---------- | ---------------------------------------- |
| 0.1.0   | hayate       | 2017-06-22 |                                          |
| 0.1.1   | huangyuezhen | 2017-7-31  | add : iot_id_apply /iot_user /iot_id_serial_no |



## iot （database: iot）

### iot_corporation

`企业表`

```sql
CREATE TABLE `iot_corporation` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `name` varchar(100) NOT NULL COMMENT '企业名称，最长255字节',
  `cid` varchar(64) NOT NULL COMMENT '社会信用代码',
  `liable` varchar(64) NOT NULL COMMENT '公司法人',
  `address` varchar(255) NOT NULL COMMENT '公司注册地址',
  `site` varchar(128) NOT NULL DEFAULT '' COMMENT '官网地址',
  `tel` varchar(32) NOT NULL COMMENT '固定电话号码',
  `mobile` varchar(20) NOT NULL COMMENT '联系人手机号码',
  `email` varchar(64) NOT NULL DEFAULT '' COMMENT '电子邮箱地址',
  `status` bit(32) DEFAULT b'0' COMMENT '审核状态',
  `note` varchar(255) NOT NULL DEFAULT '' COMMENT '备注',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uidx_name` (`name`),
  UNIQUE KEY `uidx_cid` (`cid`),
  UNIQUE KEY `uidx_mobile` (`mobile`)
) ENGINE=InnoDB AUTO_INCREMENT=10000 DEFAULT CHARSET=utf8mb4;
```

### iot_corporation_slave

`企业附表`

```sql
CREATE TABLE `iot_corporation_slave` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `scope` varchar(255) NOT NULL DEFAULT '' COMMENT '经营范围',
  `addr_pro` varchar(10) NOT NULL COMMENT '身份编码',
  `addr_city` varchar(10) NOT NULL COMMENT '城市编码',
  `addr_com` varchar(10) NOT NULL COMMENT '区编号',
  `ctime` datetime NOT NULL COMMENT '注册时间',
  `blist` bit(32) NOT NULL DEFAULT b'0' COMMENT '公司是否上市？0：未设置；1：上市；2：未上市',
  `employee_range` tinyint(4) NOT NULL DEFAULT '0' COMMENT '0:未设置',
  `f_cid` varchar(64) NOT NULL COMMENT '社会信用代码',
  PRIMARY KEY (`id`),
  KEY `f_cid` (`f_cid`),
  CONSTRAINT `iot_corporation_slave_ibfk_1` FOREIGN KEY (`f_cid`) REFERENCES `iot_corporation` (`cid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10000 DEFAULT CHARSET=utf8mb4;
```

> - 与iot_corporation 表一同存储企业注册基本信息，创建、更改属性时，与iot_corporation 表保持一致
>
>   ​

### iot_user

`企业账号表`

```sql
CREATE TABLE `iot_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `account` varchar(24) NOT NULL COMMENT '账号',
  `_key` varchar(256) NOT NULL COMMENT '密码',
  `f_cid` varchar(64) NOT NULL COMMENT '社会信用代码',
  `person` varchar(24) DEFAULT NULL COMMENT '联系人',
  `tel` varchar(24) DEFAULT NULL COMMENT '联系电话',
  `status` bit(32) DEFAULT b'1' COMMENT '账号状态',
  `mtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '申请时间戳',
  `type` bit(32) NOT NULL DEFAULT b'0'  COMMENT '默认为企业用户',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uidx_fcid` (`f_cid`),
  UNIQUE KEY `uidx_account` (`account`),
  CONSTRAINT `iot_user_ibfk_1` FOREIGN KEY (`f_cid`) REFERENCES `iot_corporation` (`cid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10000 DEFAULT CHARSET=utf8mb4;
```

> - 公司注册成功后，在 iot_user  默认创建相应的账号，初始密码、初始账号分别为社会信用代码后六位、公司联系人手机电话
> - 用户进行初始密码修改时，需补全 账号联系人名称信息 
> - ‘tel’ 联系电话 等同于account, 暂时空置

### iot_id

`标识表`

```sql
CREATE TABLE `iot_id` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `_id` varchar(128) NOT NULL COMMENT '物品标识',
  `version` varchar(12) NOT NULL COMMENT '标识编码版本',
  `ctime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '时间戳',
  `addr` varchar(24) NOT NULL COMMENT '地址编码',
  `category` varchar(32) NOT NULL COMMENT '物品类别',
  `vender` varchar(64) NOT NULL COMMENT '厂家、供应商',
  `serial_no` varchar(128) NOT NULL COMMENT '商品编号(按版本、厂商、类别)',
  `status` bit(32) NOT NULL DEFAULT b'0' COMMENT '商品状态',
  `f_cid` varchar(64) NOT NULL COMMENT '社会信用代码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uidx_id` (`_id`),
  KEY `f_cid` (`f_cid`),
  CONSTRAINT `iot_id_ibfk_1` FOREIGN KEY (`f_cid`) REFERENCES `iot_corporation` (`cid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10000 DEFAULT CHARSET=utf8mb4;
```

> - status ： 状态的意义 ，详见附表 `数字字段对照含义`
>
> - _id : 标识id, 当修改 本表的其他属性时，不再更新此字段,需要获取时动态生成
>
> - f_cid : 关联 iot_corporation表 cid字段
>
> - vendor : iot_corporation 表 自增ID 36进制表示 , 厂家代码,； 社会信用代码过长，故采用`iot_corporation`表的自增ID进行转换
>
> - serial_no :  商品编号
>
>   根据厂家、物品类别 进行编码，默认起始编码值为1 ，此后按步长为 1 进行递增
>
>   36 进制
>
>   从`iot_id_serial_no`表获得
>
>   ​

### iot_id_serial_no

`物品编码序列号`

```sql
CREATE TABLE `iot_id_serial_no` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `category` varchar(32) NOT NULL COMMENT '物品编码',
  `f_cid` varchar(64) NOT NULL COMMENT '社会信用代码',
  `id_bnum` int(11) NOT NULL DEFAULT '1' COMMENT '标识起始值',
  `id_enum` int(11) NOT NULL COMMENT '标识起始值',
  `version` varchar(4) NOT NULL DEFAULT '01',
  `mtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '申请时间戳',
  PRIMARY KEY (`id`),
  UNIQUE KEY `version` (`version`,`f_cid`,`category`),
  KEY `f_cid` (`f_cid`),
  CONSTRAINT `iot_id_serial_no_ibfk_1` FOREIGN KEY (`f_cid`) REFERENCES `iot_corporation` (`cid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10000 DEFAULT CHARSET=utf8mb4;
```

> f_cid /version /category   建立唯一索引，id_enum 记录该版本厂商、本物品类别下当前最大的商品序列号，默认从1 按步长1 开始递增

> 

### iot_id_apply

`标识申请表`   

```sql
CREATE TABLE `iot_id_apply` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `addr` varchar(24) NOT NULL COMMENT '地址编码',
  `category` varchar(32) NOT NULL COMMENT '物品编码',
  `f_cid` varchar(64) NOT NULL COMMENT '社会信用代码',
  `id_num` int(11) NOT NULL COMMENT '申请标识数量',
  `version` varchar(4) NOT NULL DEFAULT '01',
  `mtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '申请时间戳',
  `ctime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '生产日期时间戳',
  `apply_id` varchar(30) DEFAULT NULL COMMENT '申请ID,唯一ID',
  `status` bit(32) NOT NULL DEFAULT b'0' COMMENT '申请状态',
  PRIMARY KEY (`id`),
  UNIQUE KEY `apply_id` (`apply_id`),
  KEY `f_cid` (`f_cid`),
  CONSTRAINT `iot_id_apply_ibfk_1` FOREIGN KEY (`f_cid`) REFERENCES `iot_corporation` (`cid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10021 DEFAULT CHARSET=utf8mb4;
```

> - 记录申请信息，status:0(未审核)，1(审核通过) ， 2(审核不通过)，详见附表`数字字段对照含义`
> - apply_id : bson 生成的ID,避免从数据库返回新增的 记录的自增ID，与及作为 申请的唯一标识(自增id过于简单)

### iot_query

`查询明细表`暂时未用到，可以先不创建

```sql
create table iot_query if not exists (
  id int not null auto_increment comment "自增id",
  _id varchar(128) not null comment "物品标识",
  ip varchar(64) not null comment "用户IP地址",
  os  varchar(20) not null comment "查询设备操作系统",
  brand  varchar(64) not null comment "查询设备品牌",
  model varchar(64) not null comment "查询设备型号",
  address point not null comment "地理坐标,GCJ_02",
  qtime datetime not null default current_timestamp comment "查询时间戳",
  primary key (id)
)engine=InnoDB DEFAULT CHARSET=utf8mb4;
```

> 备注：
>
> - address : 存储坐标，经纬度。高德： GCJ-02

### json 替代

iot_division_code

`行政区域代码表-仅国内，国家统计局2015-09-30发布，详情请查看`[行政区划代码](http://www.stats.gov.cn/tjsj/tjbz/xzqhdm/201608/t20160809_1386477.html)

直接转成[geocode.json](http://git.dev.cnicg.cn/xujia/iot/blob/master/conf.d/geocode.json)字段，作为静态资源返回给前端使用, 根据用户选择的 省-市-区/县 返回对应的  地理编码

```json
# provinces : 省
{provinces:{}, citys:{}, regions:{}}
```

iot_goods_code

`产品目录表，参考广州市《政府采购品目表》`

直接转成[category.json](http://git.dev.cnicg.cn/xujia/iot/blob/master/conf.d/category.json)字段，作为静态资源返回给前端使用 , 根据用户选择的 类别名称，返回类别代码。

```
# name  to code 
c5["货物"]["通用设备"]["电气设备"]['生活用电器'].keys()   #获取第五层的选项
```

### 

## 附表

#### 数据表字段数字对照

> - employee_range  ( 企业员工规模 ) :
>
> ​      (0, "未设置"), (1, "50人 以下"), (2, "50-100 人"), (3, "100-500 人"), (4, "500-2000 人"), (5, "2000 人以上")
>
> - iot_corporation.status  (  注册公司状态) ：  0 :未审核； 1: 已审核 通过； 2： 已审核未通过 ; 4:企业账号被注销
> - iot_id.status ( 标识状态)：   0: 未使用 ；1： 在使用                                
> - iot_id_apply.status ( 标识申请状态 ) ：0： 未审核 ；1：审核通过； 2：审核不通过
> - iot_corporation_slave.blist (是否上市)：0：未上市；1：已上市
> - iot_user.status(账号状态)：0: 未修改初始密码  1:在使用  ,已修改初始密码     4：被注销
> - iot_user.type(账号类型)  ： 
>
> ​       32位的bit  类型存储， 
>
> ​      0位 表示 用户身份，超级管理员 0 位为1，通过用户名判断
>
> ​       0: 企业用户 ，如  000000  000000  000000  000000  000000  00,  ~0 ^1
>
> ​       1 : 管理员用户 ，如 000000  000000  000000  000000  000000  01,1&1


