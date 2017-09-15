'''返回二维码解析内容'''
from .base import BaseHandler
from common.parser_id import  parser,parser_category,parser_geocode
from  conf.category import  CATEGORYS
from conf.geocode import  GEOCODE

class ThingsHandler(BaseHandler):
    def get(self, _id):
        print(_id)
        res = parser(_id)
        print(res, type(res))
        #res = parser_category(res)
        #res = parser_geocode(res)
        position = parser_category(res["postion"],GEOCODE)
        category = parser_geocode(res["category"],CATEGORYS)
        time = res["time"]
        brand, serial = res["brand"], res['serial']

        self.write('<!DOCTYPE html>'
                   '<html>'
                       '<head>'
                           '<meta charset="utf-8"> '
                           '<title> 物品信息</title>'
                           '<link rel="stylesheet" href="https://cdn.bootcss.com/bootstrap/3.3.7/css/bootstrap.min.css">'
                           '<script src="https://cdn.bootcss.com/jquery/2.1.1/jquery.min.js"></script>'
                           ' <script src="https://cdn.bootcss.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>'
                       '</head>'
                       '<body>'
                           ' <ul class="list-group"style="margin-left:10%;margin-top:10%;">'
                              ' <li class="list-group-item">category :' + category + '</li>'
                                '<li class="list-group-item">time:' + time + '</li>'
                                '<li class="list-group-item">brand:' + brand + '</li>'
                                '<li class="list-group-item">position:' + position + '</li>'
                               '<li class="list-group-item">serial:' + serial + '</li>'
                            '</ul>'
                        '</body>'
                   '</html>')
