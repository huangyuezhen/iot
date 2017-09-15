# -*- coding: utf-8 -*-
import json
import datetime
import hashlib
import  struct
from PIL import Image





def insert_into_corparetion(conn,cur):
    """
    往corporation 和 corporation_slave 表插入测试数据

    """

    name_o = "请求测试"
    cid_o = "ATeidng2djuief"
    liable = "崔成泽"
    address= "外星6号"
    tel= "020-39335678"
    mobile_o= "15745200"
    addr_pro= "44"
    addr_city= "02"
    addr_com= "06"
    site= "https"
    email= "455com"
    status= 0
    scope= "物联网、车"
    ctime= "2016-01-03"
    blist= 0
    employee_range= 1
    note= "备注"


    for i in range(1,10000):
        name = name_o +str(i)
        cid = cid_o + str(i)
        mobile = mobile_o + str(i)

        sql_co = "INSERT INTO iot_corporation (name, cid,liable,address,site,tel,mobile,email,status,note)" \
                 "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s',%d,'%s')" % (
                 name, cid, liable, address, site, tel, mobile, email, status, note)

        print("Sql:", sql_co)

        sql_sl = "INSERT INTO iot_corporation_slave (scope, addr_pro,addr_city,addr_com,ctime,blist,employee_range,f_cid)" \
                 "VALUES ('%s','%s','%s','%s','%s','%s',%d,'%s')" % (
                 scope, addr_pro, addr_city, addr_com, ctime, blist, employee_range, cid)
        print("Sql:", sql_sl)
        cur.execute(sql_co)
        cur.execute(sql_sl)
        conn.commit()



def dict_from_automap(obj):
    if isinstance(obj, sqlalchemy.ext.automap.AutomapBase):
        return obj_to_dict(obj)
    else :
        return  None
def query_to_dict(obj):
    # 定义一个字典数组
    fields = []
    # 定义一个字典对象
    autobase = []
    # 检索结果集的行记录
    for rec in obj:
        print("is in loop and type of rec", type(rec), rec)
        # 检索记录中的成员
        print("dir(rec):", dir(rec))
        # print (dict(rec))
        record = obj_to_dict(obj)
        autobase.append(record)

    # 返回字典数组
    return fields


class AlchemyEncoder_2(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, sqlalchemy.ext.automap.AutomapBase):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' and hasattr(obj.__getattribute__(x), '__call__') == False]:
                data = obj.__getattribute__(field)
                if isinstance(data, datetime):
                     data=  data.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(obj, datetime.date):
                    data=  obj.strftime('%Y-%m-%d')
                fields[field] = data

            return fields

        return json.JSONEncoder.default(self, obj)

def obj_to_dict(obj):
    record = {}
    for field in [x for x in dir(obj) if
                  # 过滤属性
                  not x.startswith('_')
                  # 过滤掉方法属性
                  and hasattr(obj.__getattribute__(x), '__call__') == False
                  # 过滤掉不需要的属性
                  and x != 'metadata']:
        data = obj.__getattribute__(field)
        try:
            record[field] = data
        except TypeError:
            record[field] = None
    return record

def sha1(*args):
    sha1 = hashlib.sha1()
    sha1.update(''.join(args).encode('utf-8'))
    return sha1
def sha256(*args):
    sha1 = hashlib.sha256()
    sha1.update(''.join(args).encode('utf-8'))
    return sha1

def  rbmp(path):
    with open(path, 'rb') as f:
        #stream = f.read()
        byte = f.read(1)
        while byte:
            # Do stuff with byte.
            print ("byte:",byte)
            print(struct.unpack("B",byte))
            byte = f.read(1)
def wtriteBin(path):
    with open(path, 'wb') as f:
        f.write(b'Hello World')
def pilrbmp(inpath,outpath,_value):
    from PIL import Image
    im = Image.open(inpath)
    img_info = "format: {},size:{},mode:{}".format(im.format, im.size, im.mode)
    print("data of image:",img_info)
    #im.convert('1')
    pixels = im.load()
    f= open(outpath, 'wb')
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
            f.write(struct.pack('B', oc_b))

def cteateImg():
    mode ="1"
    size = (296,128)
    new_im = Image.new(mode, size, color=0)
    new_im.save(outpath, "BMP")
def enhanceimg(inpath):
    from PIL import ImageEnhance
    im = Image.open(inpath)
    enh = ImageEnhance.Contrast(im)
    enh.enhance(1).show("30% more contrast")
def converImg(inpath,outpath):
    from PIL import Image, ImageEnhance
    im = Image.open(inpath)
    #im = im.convert("1")
    im.save(outpath, "BMP")


class Node(object):
    """节点"""
    def __init__(self,data,pnext=None):
        self.data = data
        self._next = pnext

class LinkList(object):
    """链表"""
    def __init__(self,head = None):
        self.head = head
        if head :
            self.length = 1
        else :
            self.length =  0

    def append(self,data):
        item = self.check_data(data)
        if self.head :
            _node = self.head
            while _node._next :
                _node = _node._next
            _node._next =  item
            self.length +=1
        else :
            self.head = item
            self.length +=1


    def check_data (self,data):
        if isinstance(data,Node):
            item = data
        else :
            item = Node(data)
        return  item


    def  insert(self,index,data):

        item = self.check_data(data)


        if not self.head :
            self.head = item
            self.length += 1
            return

        node = self.head
        ii = 2
        while node._next and ii <index:
            node = node._next
            ii += 1
        pre_next = node._next
        item._next = pre_next
        node._next = item
        self.length +=1



def insertion_sort(_list):
    res =[]
   # for ii in _list:



if __name__ == '__main__':

   a  = LinkList()
   for  ii in range (1,20):

       a.append(ii)


   node = a.head
   while node._next:
        print ("first:",node.data)
        node = node._next

   a.insert(0,67)

   node = a.head
   while node._next:
       print(node.data)
       node = node._next


   print ("length:",a.length)

   print (bytes([1,2]))




