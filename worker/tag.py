
import string
import os
import time
import struct
from io import BytesIO


from PIL import Image
from PIL import ImageFont,ImageDraw
from PIL import PngImagePlugin
import qrcode
import barcode




# custom define barcode write mechanism
try:
    from .writer import ImageWriter
except:
    from writer import ImageWriter

try:
    from common.error import IoTError
except:
    from tornado.web import HTTPError as IoTError

_H1_FONT = None
_H2_FONT = None
_H3_FONT = None

def init_font(font_path='conf.d/font/simhei.ttf'):
    '''
    '''
    global _H1_FONT, _H2_FONT, _H3_FONT
    if _H1_FONT and _H2_FONT:
        return _H1_FONT, _H2_FONT, _H3_FONT

    _H1_FONT=ImageFont.truetype(font_path,20)
    _H2_FONT=ImageFont.truetype(font_path,16)
    _H3_FONT=ImageFont.truetype(font_path,32)
    
    return _H1_FONT, _H2_FONT, _H3_FONT


def dump_bg(size,color, mode):
    '''
        create a new background image
        the default mode is 'RGB'

        :parameters :
            mode  : str
                    RGB | CMYK | L   
            size  : tuple
                    image size (width,height)
            color : tuple
                    background color

        :returns : a new background image
        :rtype   : Image

    '''

    img_bg_new=Image.new(mode,size,color)
    return img_bg_new


def dump_qrcode(url):
    '''
        convert url to qrcode image 

        :parameters :
            url  : str
                   QR code charset : string.ascii_letters, string.digits, string.punctuation
        :returns : qrcode image
        :rtype   : Image

    '''
    qr=qrcode.main.QRCode(version=2,
                          error_correction=qrcode.constants.ERROR_CORRECT_Q,
                          box_size=4,
                          border=0)
    qr.add_data(url)
    qr.make(fit=True)
    img_qrcode=qr.make_image()
    #img_qrcode.save(os.path.join(os.path.dirname(__file__),'img','qrcode.jpg'))
    return img_qrcode


def dump_barcode(code):
    '''
        convert digits to barcode image, support ean13 & isbn
        :parameters : str
                      use ean13 : re.match(r'[0-9]{13}',code)
        :returns : barcode image
        :rtype   : Image

    '''
    if len(code) ==  13 and all(code[i] in string.digits for i in range(len(code))): 
        ean13=barcode.ean.EuropeanArticleNumber13(code,writer=ImageWriter())
        #img_barcode=ean13.make_image()
        img_barcode=ean13.render()
        img_barcode = img_barcode.crop((65,5,460,255))
        #img_barcode.save(os.path.join(os.path.dirname(__file__),'img','barcode.jpg'))
        return img_barcode
    else:
        raise IoTError(400, 'barcode: %s abnormal', code)


def render_product_info(img_bg,product,img_barcode, mode, color, 
                        # font_path='/web/iot/conf.d/font/simsun.ttc'):
                        font_path='conf.d/font/simhei.ttf'):
    '''
        render product information, includes: product base info & barcode image
        
        :parameters:
            img_bg      : Image
                          background image
            img_barcode : Image
                          barcode image
            product     : Dictionary
                          product info
                          product = {'name':'', 'intr':'', 'price':'279.00', 'ori_price':299.00, 'promotion':''}

        :returns : left part of background image
        :rtype   : Image

        Note: left region (170, 128)
        name : height 40 , font height 20, 2 line, most 16 chars
        price: height 20, font height 20
        promotion : height 16, dimgray, most 8 chars (88888.88)
        barcode : 170*50
            
    '''
    width,height=170,128
    x,y = 2,2
    # char height 
    h1,h2=20,16

    # init font
    font_h1, font_h2, font_h3 = init_font(font_path)

    # left image         
    img_left_size=(width, height)
    img_left=Image.new(mode,img_left_size,color)

    # left_top: product name
    img_left_top_size=(width,h1*2)
    img_left_top=Image.new(mode,img_left_top_size,color)
    draw_img_left_top=ImageDraw.Draw(img_left_top)

    # name
    # name_font=ImageFont.truetype(font_path,h1)
    name_coor=(0, 0)

    product['name'] = '\n'.join([product['name1'],product['name2']])
    draw_img_left_top.text(name_coor,product['name'],fill=0,font=font_h1)

    img_left.paste(img_left_top.crop(),(x,y))
    
    y+=(h1*2)

    # price 
    if product['promotion'] and product['ori_price']:
        img_price_size = (width, h1)
        img_price=Image.new(mode,img_price_size,color)
        draw_price = ImageDraw.Draw(img_price)

        # price_font=ImageFont.truetype(font_path,h1)
        price_coor=(0,0)

        draw_price.text(price_coor,'￥'+product['price'],fill=0,font=font_h1)
        img_left.paste(img_price.crop(),(x,y))

        y+=(h1)

        # ori_price & promotion
        if product['promotion'] and product['ori_price']:
            # promotion & ori_price must be True
            img_promotion_size = (width, h2)
            img_promotion=Image.new(mode,img_promotion_size,color)
            draw_promotion = ImageDraw.Draw(img_promotion)

            # promotion_font=ImageFont.truetype(font_path, h2)
            promotion_coor=(0,0)

            product['promotion']=product['promotion'][:4]

            _len = len(product['ori_price'])
            ori_price = product['ori_price']
            if _len < 8:
                ori_price = product['ori_price'] + (8-_len)*' '

            promotion = '原价 ' + ori_price + product['promotion']
            draw_promotion.text(promotion_coor,promotion,fill='dimgray',font=font_h2)
            price_line_start_coor = (0, h2/2)
            price_line_end_coor = ((5+_len)*h2/2, h2/2)

            draw_promotion.line([price_line_start_coor,price_line_end_coor],fill=0)

            img_left.paste(img_promotion.crop(),(x,y))

        y+=(h2)
    else:
        img_price_size = (width, h1+h2)
        img_price=Image.new(mode,img_price_size,color)
        draw_price = ImageDraw.Draw(img_price)
        price_coor=(0,0)

        draw_price.text(price_coor,'￥'+product['price'],fill=0,font=font_h3)
        img_left.paste(img_price.crop(),(x,y))
        
        y+=(h2*2)

    # barcode
    img_barcode=img_barcode.resize((150,50),Image.BILINEAR)

    img_left.paste(img_barcode.crop(),(x,y))
    
    return img_left


def dump_img(img_bg,img_left,img_qrcode):
    '''
        dump background image
        :parameters:
            img_left:   Image
                        left part of background image
            img_qrcode: Image
                        qrcode image
        :returns: dump background image
        :rtype  : Image

    '''
    # right: qrcode image
    if img_qrcode.size[0]<int(img_bg.size[0]*(2/5)):
       img_qrcode=img_qrcode.resize( (int(img_bg.size[0]*(2/5)),int(img_bg.size[0]*(2/5) )),Image.BILINEAR)
    elif img_qrcode.size[0]>int(img_bg.size[0]*(2/5)):
       img_qrcode=img_qrcode.resize( (int(img_bg.size[0]*(2/5)),int(img_bg.size[0]*(2/5))),Image.ANTIALIAS)
    else:
        pass

    # if (img_bg.size[1]- 20)<img_qrcode.size[1]:
    #     raise ValueError('limit the height of img_bg：',img_qrcode.size[1]+20 )
    img_bg.paste(img_qrcode.crop(),( int(img_bg.size[0]*(3/5)),int((img_bg.size[1]-int(img_bg.size[0]*(2/5)))/2)))

    img_bg.paste(img_left.crop(),(0,0))
    return img_bg


def convert_bg(img_bg,mode):
    '''
        if the mode of img_bg is not 'RGB', it is converted to the corresponding mode
        :parameters:
            img_bg : Image
                     the rendered background image
            mode   : str
                     CMYK | L | 1 | RGBA
        :returns : the converted img_bg
        :rtype   : Image 

    '''
    if mode!='RGB':
        img_bg_convert=img_bg.convert(mode, colors=2)
        return img_bg_convert
        

def save_bg(img_bg, path='/cnicg/iot/www/static/img/ ',img_name= 'logo_img.bmp'):
#def save_bg(img_bg, path='E://'):
     '''
        save the final background image
        :parameters:
            img_bg : Image
                     the final background image

     '''
     # Image.register_save('PNG', PngImagePlugin._save)
     img_bg.save(os.path.join(path,img_name),
                 optimize=True)

def make_img(url, product, size=(296,128), color='white'):
    '''
        make the result of iamge
        :parameters:
            size    : tuple
                      img_bg size
            color   : tuple
                      img_bg color
            url     : str
                      qroode url
            product : dict
                      product info

    '''
    mode = 'L'
    img_bg_new=dump_bg(size, color, mode=mode)
    img_qrcode=dump_qrcode(url)
    img_barcode=dump_barcode(product['barcode'])
    img_left=render_product_info(img_bg_new,product,img_barcode, mode=mode, color=color)
    img_bg=dump_img(img_bg_new,img_left,img_qrcode)
    return img_bg
    # save_bg(img_bg)
    #img_bg.show()
    #img_bg_convert=convert_bg(img_bg,args.mode)
    #save_bg(img_bg_convert)


def bmp_to_bin(bmp_v,_value=152,outpath ="/cnicg/iot/www/static/img/",bin_name="prodcut.bin"):
    """
    图片扫描方式：从右上角至左下角垂直扫描
    :param bmp_v: bmp bytes
    :param _value: convert value
    :param outpath: output path
    :param bin_name: file name
    :return: bytes or save img without header
    """

    im = Image.open(BytesIO(bmp_v))
    #im = Image.frombytes(mode= "L")
    pixels = im.load()

    outpath = outpath + bin_name
    f = open(outpath, 'wb')
    res = []
    for x in range(im.width-1,-1,-1):
        for y in range(0,im.height,8):
            _list =[]
            for i in range (0,8):
                pixel_ = pixels[x,y+i]
                if isinstance(pixel_,tuple):
                   pixel_ = pixel_[0]
                if pixel_ >_value:
                    p = "0"
                else:
                    p = "1"
                _list.append(p)
            b = ''.join(_list)
            oc_b = int(b, 2)
            res.append(oc_b)
    f.write(bytes(res))
    #return bytes(res)


if __name__=='__main__':
    '''
        test
    '''
    import argparse
    parse=argparse.ArgumentParser()
    parse.add_argument('--mode',default='L',help='bg img mode')
    parse.add_argument('--size',default=(296,128),type=tuple,help='bg img size (width,height)')
    parse.add_argument('--color',default=(255,255,255),type=tuple,help='bg img color (r,g,b)' )
    parse.add_argument('--url',default='http://item.jd.com/2554180.html',help='qrcode url')
    parse.add_argument('--product',
                       default={'name1':'小蚁(YI)行车记录仪',
                                'name2':'-青春版',
                                'intr':'1296p超高清夜视165°广角智能辅助驾驶（太空灰）',
                                'price':'27900.0',
                                'ori_price':'279',
                                'promotion':'端午促销',
                                'barcode':'6902890884910'},
                       type=dict,
                       help='product info')
    args=parse.parse_args()
    
    start_time=time.clock()

    img = make_img(args.url,args.product,args.size, 'white')
    # img = convert_bg(img, 'P')
    img_buf = BytesIO()
    img.save(img_buf, format='BMP')
    #save_bg(img)

    print (img_buf.getvalue())
    bin = bmp_to_bin(img_buf.getvalue())
    print (bin)

    # from io import BytesIO

    # img_buf = BytesIO()
    # img.save(img_buf, format='PNG', optimion=True)
    # img = convert_bg(img, 'P')
    # import tinify
    # tinify.key='AkQ4KjMgiTqvCEt8Y1WaOp21TGjLJORQ'
    # source = tinify.from_file('/cnicg/iot/www/static/logo_img.png')
    # source.to_file('/cnicg/iot/www/static/logo_img2.png')

    # tinify.from_buffer(img_buf.getvalue()).to_file('/cnicg/iot/www/static/logo_img.png')

    end_time=time.clock()

    print('total time: %s s' % (end_time-start_time))
    
    
    
=======
'''
'''
import string
import os
import time
import struct
from io import BytesIO


from PIL import Image
from PIL import ImageFont,ImageDraw
from PIL import PngImagePlugin
import qrcode
import barcode




# custom define barcode write mechanism
try:
    from .writer import ImageWriter
except:
    from writer import ImageWriter

try:
    from common.error import IoTError
except:
    from tornado.web import HTTPError as IoTError

_H1_FONT = None
_H2_FONT = None
_H3_FONT = None
h1,h2=20,16

def init_font(font_path='conf.d/font/simhei.ttf'):
    '''
    '''
    global _H1_FONT, _H2_FONT, _H3_FONT
    if _H1_FONT and _H2_FONT:
        return _H1_FONT, _H2_FONT, _H3_FONT

    _H1_FONT=ImageFont.truetype(font_path,h1)
    _H2_FONT=ImageFont.truetype(font_path,h2)
    _H3_FONT=ImageFont.truetype(font_path,h2*2)
    
    return _H1_FONT, _H2_FONT, _H3_FONT


def dump_bg(size,color, mode):
    '''
        create a new background image
        the default mode is 'RGB'

        :parameters :
            mode  : str
                    RGB | CMYK | L   
            size  : tuple
                    image size (width,height)
            color : tuple
                    background color

        :returns : a new background image
        :rtype   : Image

    '''

    img_bg_new=Image.new(mode,size,color)
    return img_bg_new


def dump_qrcode(url):
    '''
        convert url to qrcode image 

        :parameters :
            url  : str
                   QR code charset : string.ascii_letters, string.digits, string.punctuation
        :returns : qrcode image
        :rtype   : Image

    '''
    qr=qrcode.main.QRCode(version=2,
                          error_correction=qrcode.constants.ERROR_CORRECT_Q,
                          box_size=4,
                          border=0)
    qr.add_data(url)
    qr.make(fit=True)
    img_qrcode=qr.make_image()
    #img_qrcode.save(os.path.join(os.path.dirname(__file__),'img','qrcode.jpg'))
    return img_qrcode


def dump_barcode(code):
    '''
        convert digits to barcode image, support ean13 & isbn
        :parameters : str
                      use ean13 : re.match(r'[0-9]{13}',code)
        :returns : barcode image
        :rtype   : Image

    '''
    if len(code) ==  13 and all(code[i] in string.digits for i in range(len(code))): 
        ean13=barcode.ean.EuropeanArticleNumber13(code,writer=ImageWriter())
        #img_barcode=ean13.make_image()
        img_barcode=ean13.render()
        img_barcode = img_barcode.crop((65,5,460,255))
        #img_barcode.save(os.path.join(os.path.dirname(__file__),'img','barcode.jpg'))
        return img_barcode
    else:
        raise IoTError(400, 'barcode: %s abnormal', code)


def render_product_info(img_bg,product,img_barcode, mode, color, 
                        # font_path='/web/iot/conf.d/font/simsun.ttc'):
                        font_path='conf.d/font/simhei.ttf'):
    '''
        render product information, includes: product base info & barcode image
        
        :parameters:
            img_bg      : Image
                          background image
            img_barcode : Image
                          barcode image
            product     : Dictionary
                          product info
                          product = {'name':'', 'intr':'', 'price':'279.00', 'ori_price':299.00, 'promotion':''}

        :returns : left part of background image
        :rtype   : Image

        Note: left region (170, 128)
        name : height 40 , font height 20, 2 line, most 16 chars
        price: height 20, font height 20
        promotion : height 16, dimgray, most 8 chars (88888.88)
        barcode : 170*50
            
    '''
    width,height=170,128
    x,y = 2,2
    # char height 
    # h1,h2=20,16

    # init font
    font_h1, font_h2, font_h3 = init_font(font_path)

    # left image         
    img_left_size=(width, height)
    img_left=Image.new(mode,img_left_size,color)

    # left_top: product name
    img_left_top_size=(width,h1*2)
    img_left_top=Image.new(mode,img_left_top_size,color)
    draw_img_left_top=ImageDraw.Draw(img_left_top)

    # name
    # name_font=ImageFont.truetype(font_path,h1)
    name_coor=(0, 0)

    product['name'] = '\n'.join([product['name1'],product['name2']])
    draw_img_left_top.text(name_coor,product['name'],fill=0,font=font_h1)

    img_left.paste(img_left_top.crop(),(x,y))
    
    y+=(h1*2)

    # price 
    if product['promotion'] and product['ori_price']:
        img_price_size = (width, h1)
        img_price=Image.new(mode,img_price_size,color)
        draw_price = ImageDraw.Draw(img_price)

        # price_font=ImageFont.truetype(font_path,h1)
        price_coor=(0,0)

        draw_price.text(price_coor,'￥'+product['price'],fill=0,font=font_h1)
        img_left.paste(img_price.crop(),(x,y))

        y+=(h1)

        # ori_price & promotion
        if product['promotion'] and product['ori_price']:
            # promotion & ori_price must be True
            img_promotion_size = (width, h2)
            img_promotion=Image.new(mode,img_promotion_size,color)
            draw_promotion = ImageDraw.Draw(img_promotion)

            # promotion_font=ImageFont.truetype(font_path, h2)
            promotion_coor=(0,0)

            product['promotion']=product['promotion'][:4]

            _len = len(product['ori_price'])
            ori_price = product['ori_price']
            if _len < 8:
                ori_price = product['ori_price'] + (8-_len)*' '

            promotion = '原价 ' + ori_price + product['promotion']
            draw_promotion.text(promotion_coor,promotion,fill='dimgray',font=font_h2)
            price_line_start_coor = (0, h2/2)
            price_line_end_coor = ((5+_len)*h2/2, h2/2)

            draw_promotion.line([price_line_start_coor,price_line_end_coor],fill=0)

            img_left.paste(img_promotion.crop(),(x,y))

        y+=(h2)
    else:
        img_price_size = (width, h1+h2)
        img_price=Image.new(mode,img_price_size,color)
        draw_price = ImageDraw.Draw(img_price)
        price_coor=(0,0)

        draw_price.text(price_coor,'￥'+product['price'],fill=0,font=font_h3)
        img_left.paste(img_price.crop(),(x,y))
        
        y+=(h1+h2)

    # barcode
    img_barcode=img_barcode.resize((150,50), Image.BILINEAR)
    img_left.paste(img_barcode.crop(),(x,y))

    # y+=40
    # 
    # img_text_size = (width, 10)
    # img_text = Image.new(mode, img_text_size, color)
    # draw_text = ImageDraw.Draw(img_text)
    # text_coor = (0,0)

    # draw_text.text(text_coor,product['barcode'],fill=0,font=font_h3)
    # img_left.paste(img_text.crop(),(x,y))
    
    return img_left


def dump_img(img_bg,img_left,img_qrcode):
    '''
        dump background image
        :parameters:
            img_left:   Image
                        left part of background image
            img_qrcode: Image
                        qrcode image
        :returns: dump background image
        :rtype  : Image

    '''
    # right: qrcode image
    if img_qrcode.size[0]<int(img_bg.size[0]*(2/5)):
       img_qrcode=img_qrcode.resize( (int(img_bg.size[0]*(2/5)),int(img_bg.size[0]*(2/5) )),Image.BILINEAR)
    elif img_qrcode.size[0]>int(img_bg.size[0]*(2/5)):
       img_qrcode=img_qrcode.resize( (int(img_bg.size[0]*(2/5)),int(img_bg.size[0]*(2/5))),Image.ANTIALIAS)
    else:
        pass

    # if (img_bg.size[1]- 20)<img_qrcode.size[1]:
    #     raise ValueError('limit the height of img_bg：',img_qrcode.size[1]+20 )
    img_bg.paste(img_qrcode.crop(),( int(img_bg.size[0]*(3/5)),int((img_bg.size[1]-int(img_bg.size[0]*(2/5)))/2)))

    img_bg.paste(img_left.crop(),(0,0))
    return img_bg


def convert_bg(img_bg,mode):
    '''
        if the mode of img_bg is not 'RGB', it is converted to the corresponding mode
        :parameters:
            img_bg : Image
                     the rendered background image
            mode   : str
                     CMYK | L | 1 | RGBA
        :returns : the converted img_bg
        :rtype   : Image 

    '''
    if mode!='RGB':
        img_bg_convert=img_bg.convert(mode, colors=2)
        return img_bg_convert
        

def save_bg(img_bg, path='/cnicg/iot/www/static/img/',img_name= 'logo_img.bmp'):
#def save_bg(img_bg, path='E://'):
     '''
        save the final background image
        :parameters:
            img_bg : Image
                     the final background image

     '''
     # Image.register_save('PNG', PngImagePlugin._save)
     img_bg.save(os.path.join(path,img_name),
                 optimize=True)

def make_img(url, product, size=(296,128), color='white'):
    '''
        make the result of iamge
        :parameters:
            size    : tuple
                      img_bg size
            color   : tuple
                      img_bg color
            url     : str
                      qroode url
            product : dict
                      product info

    '''
    mode = 'L'
    img_bg_new=dump_bg(size, color, mode=mode)
    img_qrcode=dump_qrcode(url)
    img_barcode=dump_barcode(product['barcode'])
    img_left=render_product_info(img_bg_new,product,img_barcode, mode=mode, color=color)
    img_bg=dump_img(img_bg_new,img_left,img_qrcode)
    return img_bg
    # save_bg(img_bg)
    #img_bg.show()
    #img_bg_convert=convert_bg(img_bg,args.mode)
    #save_bg(img_bg_convert)


def bmp_to_bin(bmp_v,_value=152,outpath ="/cnicg/iot/www/static/img/",bin_name="prodcut.bin"):
    print ("type:",type(bmp_v))
    im = Image.open(BytesIO(bmp_v))
    #im = Image.frombytes(mode= "L")
    pixels = im.load()
    print("original =", im.mode, im.size)
    outpath = outpath + bin_name
    f = open(outpath, 'wb')
    res = []
    for x in range(im.width-1,-1,-1):
        for y in range(0,im.height,8):
            _list =[]
            for i in range (0,8):
                pixel_ = pixels[x,y+i]
                if isinstance(pixel_,tuple):
                   pixel_ = pixel_[0]
                if pixel_ >_value:
                    p = "0"
                else:
                    p = "1"
                _list.append(p)
            b = ''.join(_list)
            oc_b = int(b, 2)
            res.append(oc_b)
    f.write(bytes(res))
    #return bytes(res)
            #print (struct.pack('B', oc_b))
            #f.write(struct.pack('B', oc_b))
    #print ("len of res:",len(res),"len of bytes:",len(bytes(res)))
    #f.write(bytes(res))

if __name__=='__main__':
    '''
        test
    '''
    import argparse
    parse=argparse.ArgumentParser()
    parse.add_argument('--mode',default='L',help='bg img mode')
    parse.add_argument('--size',default=(296,128),type=tuple,help='bg img size (width,height)')
    parse.add_argument('--color',default=(255,255,255),type=tuple,help='bg img color (r,g,b)' )
    parse.add_argument('--url',default='http://item.jd.com/2554180.html',help='qrcode url')
    parse.add_argument('--product',
                       default={'name1':'小蚁AB行车记录仪',
                                'name2':'-青春版',
                                'intr':'1296p超高清夜视165°广角智能辅助驾驶（太空灰）',
                                'price':'27900.0',
                                'ori_price':'',
                                'promotion':'端午促销',
                                'barcode':'6902890884910'},
                       type=dict,
                       help='product info')
    args=parse.parse_args()
    
    start_time=time.clock()

    img = make_img(args.url,args.product,args.size, 'white')
    # img = convert_bg(img, 'P')
    img_buf = BytesIO()
    img.save(img_buf, format='BMP')
    #save_bg(img)

    print (img_buf.getvalue())
    bin = bmp_to_bin(img_buf.getvalue())
    print (bin)

    # from io import BytesIO

    # img_buf = BytesIO()
    # img.save(img_buf, format='PNG', optimion=True)
    # img = convert_bg(img, 'P')
    # import tinify
    # tinify.key='AkQ4KjMgiTqvCEt8Y1WaOp21TGjLJORQ'
    # source = tinify.from_file('/cnicg/iot/www/static/logo_img.png')
    # source.to_file('/cnicg/iot/www/static/logo_img2.png')

    # tinify.from_buffer(img_buf.getvalue()).to_file('/cnicg/iot/www/static/logo_img.png')

    end_time=time.clock()

    print('total time: %s s' % (end_time-start_time))
    
    
    
>>>>>>> 6b2a4575fb2f55b104a570af2fae2ce38915ebf0
