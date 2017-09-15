'''
    read geocode file
'''

from yaml import load, dump
from common import util
import json
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

CATEGORY_L1 = {}
CATEGORY_L2 = {}
CATEGORY_L3 = {}
CATEGORY_L4 = {}
CATEGORY_L5 = {}
CATEGORY_L6 = {}
CATEGORYS ={}

def read_json(path):
    stream = open(path, 'r')
    return json.load(stream)

def parse_category(path='conf.d/category.json'):
#def parse_category(path='../conf.d/category.json'):
    dict_a = read_json(path)
    c1, c2, c3, c4, c5, c6 = dict_a["CATEGORY_L1"], dict_a["CATEGORY_L2"], dict_a["CATEGORY_L3"], dict_a["CATEGORY_L4"], \
                             dict_a["CATEGORY_L5"], dict_a["CATEGORY_L6"]


    return c1, c2, c3, c4, c5, c6

def init():
    global CATEGORY_L1, CATEGORY_L2, CATEGORY_L3, CATEGORY_L4,CATEGORY_L5, CATEGORY_L6,CATEGORYS
    if CATEGORY_L1:
        return
    CATEGORY_L1, CATEGORY_L2, CATEGORY_L3, CATEGORY_L4,CATEGORY_L5, CATEGORY_L6 = parse_category()
    CATEGORYS = code_to_category()

def code_to_category(path='conf.d/category.yml'):
#def code_to_category(path='../conf.d/category.yml'):
    category = util.read_yaml(path)
    return category

if __name__ == '__main__':
    c1, c2 , c3,c4, c5, c6 = parse_category('../conf.d/category.json')
    print (c5["货物"]["通用设备"]["电气设备"]['生活用电器'].keys()) #获取第五层的选项
else:
    init()
