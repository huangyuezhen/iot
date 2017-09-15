'''
'''
import random

from worker import tag
from .base import BaseHandler
from common import util
from io import BytesIO
from conf import settings

import tinify
tinify.key='AkQ4KjMgiTqvCEt8Y1WaOp21TGjLJORQ'


IMG_URL =settings['serve']['img_prefix']

class TagHandler(BaseHandler):
    '''
    '''
    URL_BASE = 'http://183.63.152.237:7880/things/'
    def get(self):
        self.post()

    def post(self):
        version = self.get_argument('version', '01')
        geocode = self.get_argument('geocode')
        category = self.get_argument('category')
        brand = self.get_argument('brand')

        # product information
        product = {}
        product['name1'] = self.get_argument('name1')
        product['name2'] = self.get_argument('name2', '')
        #product['intr'] = self.get_argument('intr', '')
        product['price'] = str(float(self.get_argument('price')))
        origin = str(float(self.get_argument('ori_price', 0)))
        product['ori_price'] = origin if origin else '' 
        product['promotion'] = self.get_argument('promotion', '')
        product['barcode'] = self.get_argument('barcode')

        #  
        brand = '0001'
        serial_no = '{:06d}'.format(random.randint(1, 999999))

        id_ = ''.join([version, util.now('%Y%m%d'), geocode, category, 'Z', brand, serial_no])

        url = self.URL_BASE + id_

        img = tag.make_img(url, product)

        """ bmp  to bin"""
        img_buf = BytesIO()
        img.save(img_buf, format='BMP')
        bmp_b = img_buf.getvalue()

        bin_name = product['name1'] + '.bin'
        tag.bmp_to_bin(bmp_b, bin_name=bin_name)

        """save bmp"""
        img_name =  product['name1'] +'.bmp'
        tag.save_bg(img,img_name=img_name)
        

        #self.set_header('Content-Type', 'image/bmp')
        #bmp_b = img_buf.getvalue()
        #bin_b = tag.bmp_to_bin(bmp_b)
        #self.finish(bin_b)
        bmp_url =IMG_URL+ img_name
        bin_url = IMG_URL + bin_name
        self.render_json_response(code =200,msg="OK",bmp_url = bmp_url,bin_url= bin_url)



