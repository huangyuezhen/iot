# 商品标签生成页面

## tag.html （页面名称）

- 加载地区编码(/static/conf/geocode.json)
- 加载商品类别编码（/static/conf/category.json）
- 提供商品信息输入框，具体参考 tag接口
- 提供生成图片显示，原尺寸显示（296*128）
- 提供图片下载按钮

### /tag

- method ： post
- request： 
  - version: 01
  - geocode: 110111
  - category: A010203
  - name : 商品名称，限制16个字符（包括汉字）
  - <u>intr</u> :  商品简介，此参数移除
  - price: 商品价格，浮点型，检测类型
  - ori_price: 商品原价, 浮点型，检测类型， 可选
  - promotion: 促销活动名称， 可选，最长6个字符。
  - barcode: 商品一维条码，13位整数，检测类型   
- response
  - content-type ： image/png
  - body : png stream