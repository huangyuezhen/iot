## IOT 标识平台 后端接口



#### 数据表 status 字段数字对照

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

### API约定

> 请求参数与及返回结果均默认为application/json,  
>
> 请求参数若无特殊说明，均支持application/x-www-form-urlencoded ,application/json ,两种类型。
>
> API Define
>
> URI : scheme://domain/resources?parameters
>
> scheme : http[s]
>
> resources :  服务定义的资源，可以是物理实体也可以是抽象的 
>
> parameters : 接口参数 
>
> - 参数既可以放在URI也可以放在http的请求body
> - 对于方法（POST|PUT|PATCH），参数强制要求放在Body
> - 请求参数类型默认为application/json，且采用utf-8 编码
>
> Response : {code:200}
>
> page & page_size 参数缺省时，默认值page =1 ,page_size =15,返回值total_count: 查询总数
>
> 用户身份认证，采用token方法，需要鉴权的接口，前端需携带token。（后端通过token 内的token_type 信息用户鉴别管理员 与企业用户）

### 1.corporation 公司信息

公司注册、查看、审核、修改、注销

| verb | path              | request       | response             | note                           |
| ---- | ----------------- | ------------- | -------------------- | ------------------------------ |
| GET  | corporation/      | {}            | [CORPORATIONT,]      | 根据筛选条件获取公司信息，需要鉴权              |
| GET  | corporation/[id]  | {}            | [CORPORATIONT,]      | id: 自增id,需要鉴权                  |
| POST | corporation/      | {CORPORATION} | {code:200, res: res} | 提交公司信息，进行公司注册，不需要鉴权            |
| PUT  | corporation/      | {}            | {code:200, res: res} | 修改、审核、注销公司注册信息，需要鉴权（且用户类型为管理员） |
| PUT  | corporation/[cid] | {}            |                      | cid :企业信用代码，需要鉴权               |

#### 1.1 POST

`公司注册`

请求参数  Content-Type":"application/x-www-form-urlencoded"    or  “application/json”

| 参数名            | 类型     | 说明             |
| -------------- | ------ | -------------- |
| cid            | string | 必选，社会信用代码      |
| name           | string | 必选，公司名称        |
| liable         | string | 必选，公司法人        |
| tel            | string | 必选，公司固定电话      |
| mobile         | string | 必选，联系人手机号码     |
| address        | string | 必选，公司注册地址      |
| addr_pro       | string | 必选， 注册地址 省份编码  |
| addr_city      | string | 必选，注册地址 城市编码   |
| addr_com       | string | 必选，注册地址 区（县）编码 |
| blist          | int    | 必选，公司是否上市      |
| email          | string | 可选，公司邮箱        |
| scope          | string | 必选，经营范围        |
| ctime          | date   | 必选，注册时间        |
| blist          | int    | 必选，公司是否上市      |
| employee_range | int    | 必选，企业员工规模      |
| note           | string | 可选，备注          |

请求示例 ("application/json")

```javascript
{
    "res": [
        {
            "note": "",
            "scope": "视频流量/广告变现",
            "name": "比度克有2677",
            "addr_com": "15",
            "email": "",
            "employee_range": 2,
            "mobile": "666",
            "site": "https://cnicg.cn",
            "liable": "展示嘎哈呢",
            "blist": 6,
            "cid": "017890045AGd9088s7AS56U56",
            "addr_city": "1",
            "id": 10039,
            "tel": "022-3933908",
            "addr_pro": "44",
            "address": "广东省广州市南沙区环市大道南2号",
            "ctime": "2016-01-03 00:00:00",
            "status": 2
        }
    ],
    "code": 200
}
```


#### 1.2 GET

`获取公司信息`

请求参数(用于筛选)

| 参数名            | 类型     | 是否必选 |
| :------------- | :----- | :--- |
| status         | int    | 否    |
| cid            | string | 否    |
| name           | string | 否    |
| address        | string | 否    |
| liable         | string | 否    |
| scope          | string | 否    |
| blist          | int    | 否    |
| empolyee_range | int    | 否    |
| page           | int    | 否    |
| page_size      | int    | 否    |

请求示例

```
get  http://172.16.44.2:8010/corporation?status=1&page=1&page_size=2
or http://172.16.44.2:8010/corporation?employee_range=4
or http://172.16.44.2:8010/corporation?scope="物联网车"
```

返回值： 返回当前请求的公司注册信息

返回值示例：

```json
{
    "code": 200,
    "res": [
        {
            "address": "广东省广州市南沙区环市大道45号",
            "tel": "022-3933908",
            "name": "整的abds_39084",
            "cid": "017890045AGd9088s7ASU56",
            "site": "https://cnicg.cn",
            "status": 0,   //公司注册状态
            "blist": 1,    //公司是否上市， 0：为上市；1：已上市
            "id": 10038,
            "employee_range": 1,
            "ctime": "2016-01-03 00:00:00",
            "email": "",
            "scope": "物联网车",
            "liable": "王震"
        }
    ]
}
```

#### 1.3 PUT

`审核、修改、注销`

API 路径:  iot_id/[cid]  , 除无须传递cid 作为筛选条件外，修改参数同下

URL参数： iot_id/

-  根据 cid  对公司注册信息进行修改
-  cid 一旦注册后不可更改；
-  除cid 外 所有参数均为可选参数
-  审核 时  更新 status 状态 即可， status 字段对照请参见 文首数字对照说明（0 :未审核； 1: 已审核 通过； 2： 已审核未通过 ; 4:企业账号被注销）

请求参数

| 参数名            | 类型     | 是否必选                                 |
| -------------- | ------ | ------------------------------------ |
| cid            | string | 是,筛选条件，选定的修改对象cid                    |
| name           | string | 否                                    |
| liable         | int    | 否                                    |
| tel            | string | 否                                    |
| address        | string | 否                                    |
| addr_pro       | string | 否                                    |
| addr_city      | string | 否                                    |
| addr_com       | string | 否                                    |
| blist          | int    | 否                                    |
| email          | string | 否                                    |
| scope          | string | 否                                    |
| ctime          | date   | 否                                    |
| blist          | int    | 否                                    |
| employee_range | int    | 否                                    |
| status         | int    | 否，审核公司注册信息，1: 审核通过；2：审核不通关；4:企业账号被注销 |
| note           | string | 否，备注信息                               |

请求示例 ("application/json")

```json

  {
      "name":" 码上吃饭",
	  "cid":"0178900-AGHDod90887ASU",
	  "liable":"王震",
	  "address":"广东省广州市番禺区环市大道南2号",
	  "tel": "022-3933908",
	  "addr_pro": "44",
	  "addr_city":"01",
	  "addr_com":"14",
	  "site": "https://cnicg.cn",
	  "email":"",
	  "scope":"物联网、车",
	  "ctime":"2017-01-07",
	  "blist":1,
	  "employee_range": 3,
	  "status":1
  
}
```
返回值：当前修改后的值

返回值示例("application/json")：

```json
{"res": 
 [
   {"site": "https://cnicg.cn", 
    "address": "广东省广州市番禺区环市大道南2号", 
    "liable": "王震", 
    "cid": "0178900-AGHDod90887ASU",
    "note": "",
    "tel": "022-3933908",
    "name": "码上吃饭", 
    "corporation_id": 10009, 
    "scope": "物联网、车",
    "status": 1, 
    "email": "", 
    "blist": 1, 
    "ctime": "2017-01-07", 
    "employee_range": 3}
 ], 
 "code": 200
}
```

###  2.iot_id 标识修改

标识修改

| verb | path        | request | response                                 | note                                     |
| ---- | ----------- | ------: | ---------------------------------------- | ---------------------------------------- |
| GET  | iot_id/[id] |      {} |                                          | id : 自增id，如果是查询单个，尽量采用这个方式查询，自增ID为主键,查询速度快好多，需要鉴权 |
| GET  | iot_id/?    |      {} |                                          | query_str，需要鉴权                           |
| PUT  | iot_id/     |      {} | {code=200, info="success", effested_row=_row | 修改标识时间、地点、标识状态更新,需要鉴权（企业用户只可修改属于自己的标识信息、不可修改状态，管理员具有修改全部标识状态的权限），需要鉴权 |
| PUT  | iot_id/[id] |      {} |                                          | id: 自增ID，需要鉴权                            |

#### GET

API 路径:  iot_id/[自增ID]

url 参数的形式支持以下字段的筛选查询

| 参数        | 类型     |                     |
| --------- | ------ | ------------------- |
| id        | int    | 自增id                |
| addr      | string | 地址编码, 如440405       |
| category  | string | 物品类别编码，如 A02010206  |
| vender    | string | 厂商ID，企业表自增ID 十六进制表示 |
| serial_no | string | ID序列号 ,十六进制表示       |
| status    | int    | 状态，0: 未使用 ；1： 在使用   |
| f_cid     | string | 企业社会信用代码            |

示例：

```
http://172.16.44.2:8010/iot_id/3
http://172.16.44.2:8010/iot_id?cid=0178900-AGHDod90887ASU&serial_no=000007
```

```json
返回值示例

{
    "msg": "OK",
    "res": [
        {
            "serial_no": "000003",
            "version": "01",
            "_id": "01201702110020440401A02010206Z07Q1000003",
            "id": 3,
            "geocode": "440826",
            "vender": "07Q1",
            "category": "A02010206",
            "ctime": "2017-09-30 00:00:00",
            "cid": "0178900-AGHDod90887ASU",
            "status": 0
        }
    ],
    "code": 200
}
```

#### 2.2 PUT

`标识时间地点修改、标识状态更新、回收`

请求参数，支持参数类型：Content-Type":"application/x-www-form-urlencoded" or "application/json"

| 参数名         | 类型     | 含义                                       |
| ----------- | ------ | ---------------------------------------- |
| new_ctime   | string | 可选，商品生产日期                                |
| new_geocode | string | 可选，商品地址编码,  和new_ctime 不可同时为空            |
| new_status  | int    | 可选，标识状态更新，0: 未使用 ；1： 在使用  （管理员才可修改）      |
| cid         | string | 可选，社会信用代码 ：筛选条件。                         |
| category    | string | 可选，物品类别代码，筛选条件。                          |
| old_geocode | string | 可选，物品地址编码，筛选条件                           |
| version     | string | 可选，标识版本号，筛选条件。                           |
| old_status  | int    | 可选，修改前标志状态，筛选条件。                         |
| _id         | 数组     | 可选，标识ID，当此项参数不为空时，其他筛选条件失效，以_id 指定的标识ID为选中对象 |

iot_id/[id] 的请求示例（修改指定的iot_id）

```json
 {
  	"new_geocode":"440826",
  	"new_ctime":"2017-09-30"
  }
```

请求示例（application/json）

```json
{     "token": "gAAAAABZiMguwTxnp5hvrE0qjmmxF0AqdR0cW5JrTKgTgmQUH92qL6VpcEDJAraly2cMoGi0ct9BH07W2OtEu_56JE4lN-V849GsSIjsMtRUs2lSPKI-l5KVES1I0pgr9FfHqK6BtrnsY3LhV6pJIrKXmT6KwU_LB-gsAfE6423QziSKMRal6R7jKJjcnIz7Gl70GMYOmz4ioTMD8YI_ib_gLnpA_HwJRZSgwLZZmWMm3_Fi2F2P1d-avgn3I-gWLe_m-cb4vC1L",
	"category":"A04010207",
	"old_geocode":"440823",
	"cid":"01566890045AGd8s7AS5456890898",
	"new_geocode":"440823",
	 "new_ctime":"2017-07-05"

}
```

返回值 （application/json）

```json
{
    "effested_row": 1,
    "msg": "ok",
    "code": 200
}
```

### 3.id_application 标识申请、审核

标识申请、申请审核、审核通过后标识生成

| verb | path                      | request | response                                 | note                       |
| ---- | ------------------------- | ------: | ---------------------------------------- | -------------------------- |
| GET  | id_application/?          |      {} | {APPLICATION}                            | 获取标识申请信息，需要鉴权              |
| GET  | id_application/[id]       |      {} |                                          | id: 自增ID，需要鉴权              |
| POST | id_application/           |      {} | {code =200 , msg ="success"              | 标识申请，需要鉴权                  |
| PUT  | id_application/           |      {} | {code=200, info="success", effested_row=_row} | 申请审核，审核通过后，标识生成，需要鉴权（管理员）  |
| PUT  | id_application/[apply_id] |         |                                          | apply_id: 申请id，其余参数同上，需要鉴权 |

####  3.1 POST

`标识申请`

请求参数,参数类型    Content-Type":"application/x-www-form-urlencoded" or  “application/json“

| 参数名      | 类型     |                                    |
| -------- | ------ | ---------------------------------- |
| cid      | string | 必选，社会信用代码 （企业用户时，可以不用传递，默认为对应的cid） |
| category | string | 必选，物品类别                            |
| geocode  | string | 必选，物品地理编码                          |
| id_num   | int    | 必选，申请的标识数量 （单次申请不可超过100w）          |
| ctime    | date   | 可选，默认未当前时间戳，短标识 ，只到日期，长标识加上 time）  |
| version  | string | 可选，版本号，默认为01                       |

请求示例( "Content-Type:application/json")

```json
{
"ctime":"20170703",
"category":"A04010207 " , 
"geocode":"440115",
"id_num":100,
"cid":"01566890045AGd8s7AS5456U56"
}
```



#### 3.2 GET

`获取标识申请信息`

请求参数

| 参数名       | 类型     | 说明                                       |      |
| --------- | ------ | ---------------------------------------- | ---- |
| status    | int    | 可选，标识状态(0： 未审核 ；1：审核通过； 2：审核不通过) ，筛选条件   |      |
| page      | int    | 可选 ，页码                                   |      |
| page_size | int    | 可选 ，数量                                   |      |
| apply_id  | string | 可选，标识申请id , 筛选条件                         |      |
| addr      | string | 可选,地址编码，示例： 440117, 筛选条件                 |      |
| category  | string | 可选，物品编码，示例： A04010207, 筛选条件              |      |
| f_cid     | string | 可选，公司社会信用代码，但用户为企业时，默认为该公司 cid, 该项参数无效;筛选条件 |      |

> get  方法返回 需要审核的申请信息，status 是筛选条件，
>
> 0：未审核；1：审核通过；2 ：审核不通过

请求示例

```javascript
get  http://172.16.44.2:8010/id_application?status=0&page=1&page_size=3
or   http://172.16.44.2:8010/id_application?status=0
or  http://172.16.44.2:8010/id_application?page=1&page_size=9&&f_cid=001566890045AGd8s7AS5456U5&addr=440115&category=A04010208
```

返回值示例

```json
{
    "res": [
        {
            "addr": "440115",
            "category": "A02010207",
            "email": "",
            "apply_id": "59790a4de13823dbabe383c1",
            "address": "广东省广州市南沙区环市大道南2号",
            "liable": "王震",
            "cor_status": 1,//企业状态
            "site": "https://cnicg.cn",
            "name": "腾讯abds_3",
            "id_num": 1,
            "apply_status": 1, //申请状态
            "tel": "022-3933908",
            "cid": "017890045AGHDod90887ASU",
            "ctime": "2017-05-03 00:00:00",
            "mtime": "2017-07-26 17:31:57"
        }
    ],
    "code": 200,
    "total_count": 17
}
```

#### 3.3 PUT

`申请审核，审核通过后，标识生成`

请求参数 Content-Type":"application/x-www-form-urlencoded" or "application/json"

| 参数       | 类型   | 说明                |
| -------- | ---- | ----------------- |
| apply_id | 数组   | 3.2 接口返回的apply_id |
| status   | int  |                   |

> put 方法 用于更新审核状态，status:
>
> 1：审核通过；2 ：审核不通过
>
> 当传递的参数status :1  时，后台进行标识生成，时间较长，10w 条ID 大概耗时 50s

请求示例( "Content-Type:application/json")

```json
{
"apply_id": ["597f2fabe13823d7c25f342c","597b5887e13823aeeb63bb2f"],
"status":1
}
```

返回值：

```json
{
    "info": "OK",
    "code": 200
}
```

### 4. account

企业账户密码修改、账户联系人/联系电话添加/修改；

| verb | path          |                            request | response             | note                    |
| ---- | ------------- | ---------------------------------: | -------------------- | ----------------------- |
| GET  | account/      |                         {"tel":''} | {code =200，msg="OK"} | 获取6位手机验证码               |
| GET  | account/[tel] |                                 {} | tel:手机号码             | 获取6位手机验证码               |
| POST | account       | {"tel":'',"_code":'',"new_psw":''} | {code =200，mag="OK"} | 找回密码，需要鉴权               |
| PUT  | account/      |                                 {} | {code =200，mag="OK"} | 修改密码,需要鉴权               |
| PUT  | account/[tel] |                                 {} | {code =200，mag="OK"} | tel: 手机号码（账号）,修改密码,需要鉴权 |

#### GET

`获取手机验证码`

请求参数 ，附带在 url 上

| 参数   | 类型     |            |
| ---- | ------ | ---------- |
| tel  | string | 11位有效的手机号码 |

验证码发送到手机，web端返回 {"code":200,"msg":"OK"}

```
请求示例 http://172.16.44.2:8010/account?tel=18825052321
```

#### POST

`找回密码`

请求参数 （支持类型：Content-Type":"application/x-www-form-urlencoded" or  “application/json“）

| 参数      | 类型     |         |
| ------- | ------ | ------- |
| _code   | string | 手机验证码   |
| tel     | string | 账号（手机号） |
| new_psw | string | 新的密码    |

请求示例(“application/json“)

```json
{"_code":"694832",
  "tel":"18825052321",
  "new_psw":"cnicggis_!@#"
  }
```

#### PUT

`密码修改、手机绑定`

请求参数  （支持类型：Content-Type":"application/x-www-form-urlencoded" or  “application/json“）

| 参数      | 类型     |         |
| ------- | ------ | ------- |
| new_key | sting  | 可选，新密码  |
| _key    | string | 必选，原密码。 |
| account | string | 必选，原账号。 |

请求示例

```json
 {
  "account":"18825052321",
  "new_key":"cnicggis_!@#",
  "_key":"cnicggis_!@#4"
 
  }
```

### 5.account_supp

`绑定、修改 手机、联系人`

| verb | path               | request | response             | note                                     |
| ---- | ------------------ | ------: | -------------------- | ---------------------------------------- |
| PUT  | supp_account/      |      {} | {code =200，mag="OK"} | 修改账号绑定的手机号、联系人，新的手机号成为新的登录账号,需要鉴权        |
| PUT  | supp_account/[tel] |      {} | {code =200，mag="OK"} | tel: (原绑定手机号，即账号)；修改账号绑定的手机号、联系人，新的手机号成为新的登录账号,需要鉴权 |

#### PUT

| 参数      |                                |      |
| ------- | ------------------------------ | ---- |
| account | 必选，账号（原先绑定的手机号）                |      |
| _key    | 必选，登录密码                        |      |
| _code   | 必选，获取的6位手机验证码                  |      |
| tel     | 可选，联系人手机号，当修改手机号时，新的手机号成为了用户账号 |      |
| person  | 可选，新绑定的联系人                     |      |

请求示例

```json

{
  "account": "18852052875",
  "_key":"er3456",
  "tel":"18825052321",
  "_code":"594862",
  "token": "gAAAAABZpGBJhf3XGDJU5PRf-MZnNEIBfWMSvjssRWrPHaYALRpwNt65ysL7uh6QnhYUYlUmKjSrqdzo-yRqwroQKLrVLbBqkTUhrh5L_Qp71Ie_tfecdPc1fGaAWvSH93Ot3_Mar4eyf5kwcxkmNozbeYCAECgSE1-GM1OcMWXebgfNJgkO4mynBGu8tPB3sYmxq9DnzKdEvIpb3RVoMKCNaU4_hHHma-0jpubvXqiwjrJtzgiv0Qo"
  }
```

### 6.token

登录验证,返回token, 获得token后，每次请求均需带上token 认证

| verb | path   |                  request | response               | note         |
| ---- | ------ | -----------------------: | ---------------------- | ------------ |
| POST | token/ | {"account":xx,"_key":xx} | {code =200 ,token =xx} | 登录验证，返回token |

#### POST

`账号登录,获取token`  当前token 过期时间为 1个小时

请求参数  （支持类型：Content-Type":"application/x-www-form-urlencoded" or  “application/json“）

| 参数      | 类型     |                                          |
| ------- | ------ | ---------------------------------------- |
| account | string | 必选，账号。手机号，初始账号为 公司 注册联系人手机号码，修改手机号后为新的手机号码。 |
| _key    | string | 必选，密码。 初始密码为cid （企业社会信用代码）后六位            |

返回值

| 参数        | 类型     |                                          |
| --------- | ------ | ---------------------------------------- |
| user      | string | 用户类型说明，“cororation”: 企业  ;  "manager": 管理员 |
| user_code | int    | 参见附表`数据表 status 字段数字对照`   iot_user.type(账号类型) 的介绍 |
| token     | string | token 值                                  |
| msg       | string | 返回值提示信息                                  |
| code      | int    | http 响应吗                                 |

```json
{
    "user_code": 50,
    "user": "corporation",
    "msg": "OK",
    "cid": "0178900-AGHDod90887ASU",
    "code": 200,
    "token": "gAAAAABZnGkAKHyCJ_6Zd0t2eRcGN5h4mxYlMS8C6G9F1NvPxXLN0KF63I1Q6Ta6kJ0Ze7Squ12knQkAdbopuDnO7SR_26xMLY3MjyYr0pKSaU3-M7m-YUjNfWtrnFszUa7R7DNfv_DNSp3a2IUaumNVzAiiS2ivYihgjvffZcuF0CV1OhQKdGOgOEf4W1pUxP_yOKnk2LXRAQFXTwxZd4SNQ3SUZHC4BqKWl8HQGq9x9HeuzGgwTVo"
}
```

### 7.mobile_code

`发送手机验证码`

| verb | path              | request | response                  | note                 |
| ---- | ----------------- | ------: | ------------------------- | -------------------- |
| GET  | mobile_code/?     |      {} | {"msg": "OK","code": 200} | 发送手机验证，有效期为2分钟，不需要鉴权 |
| GET  | mobile_code/[tel] |      {} | {"msg":“OK”,"code":200}   | 发送手机验证，有效期为2分钟，不需要鉴权 |

#### GET

请求参数

| 参数   | note   |
| ---- | ------ |
| tel  | 必选，手机号 |

请求示例

```
http://172.16.44.2:8010/mobile_code/?tel=18825052321

or  http://172.16.44.2:8010/mobile_code/18825052321
```

### 8.tag

`标签图片生成`

| verb | path | request | response                     | note             |
| ---- | ---- | ------: | ---------------------------- | ---------------- |
| GET  | tag/ |      {} | {code = 200,msg = "success"} | 返回标签图片，测试暂时不需要鉴权 |
| POST | tag/ |      {} | {code =200 , msg ="success"} | 返回图片，测试暂不需要权限    |

#### GET

   同post

#### POST

请求参数

| 参数       | note         |
| -------- | ------------ |
| barcode  | 必选，13位数字，条形码 |
| geocode  | 必选，地址编码      |
| category | 必选，物品类别编码    |

请求示例

```json
{
 	"geocode":"440823",
  "version":"01",
  "category": "A02010207",
  "brand":"Haier",
 "name1":"小蚁(YI)行车记录仪",
"name2":"-青春版",
"intr":"1296p超高清夜视165°广角智能辅助驾驶（太空灰）",
"price":"27900.0",
"ori_price":"279",
"promotion":"端午促销",
"barcode":"6902890884910"
 }
```

### 附表

#### 测试账号

- 管理员

```json
{   "account":"18825052324",
  	"_key":"ef9868"
  }
```

- 企业用户

```json
{	"account":"18852052875",
  	"_key":"er3456"
  }
```

#### HTTP  响应码

200 请求成功

400  404 客户端错误

401 未授权

500  服务器错误

#### 数据表 status 字段数字对照

> - employee_range  ( 企业员工规模 ) :
>
>
> ​      (0, "未设置"), (1, "50人 以下"), (2, "50-100 人"), (3, "100-500 人"), (4, "500-2000 人"), (5, "2000 人以上")
>
> - iot_corporation.status  (  注册公司状态) ：  0 :未审核； 1: 已审核 通过； 2： 已审核未通过 ; 4:企业账号被注销
>
> - iot_id.status ( 标识状态)：   0: 未使用 ；1： 在使用                                
>
> - iot_id_apply.status ( 标识申请状态 ) ：0： 未审核 ；1：审核通过； 2：审核不通过
>
> - iot_corporation_slave.blist (是否上市)：0：未上市；1：已上市
>
> - iot_user.status(账号状态)：0: 未修改初始密码  1:在使用  ,已修改初始密码     4：被注销
>
> - iot_user.type(账号类型)  ： 
>
> ​       32位的bit  类型存储， 
>
> ​      0位 表示 用户身份，超级管理员 0 位为1，通过用户名判断
>
> ​       0: 企业用户 ，如  000000  000000  000000  000000  000000  00,  ~0 ^1
>
> ​       1 : 管理员用户 ，如 000000  000000  000000  000000  000000  01,1&1