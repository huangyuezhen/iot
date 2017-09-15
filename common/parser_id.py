import re

import time


# short_pattern = r'\d{2}\d{8}\d{10}[A-Z]\d{4,10}Z[A-Z0-9]{4}[A-Z0-9]{6}'
# long_pattern = r'[A-Z]{2}\d{2}\d{14}\d{14}[A-Z]{3}\d{4,10}Z[A-Z0-9]{6}[A-Z0-9]{8}'
KEYWORDS = {'version', 'time', 'postion', 'category', 'tail', 'brand', 'serial'}
short_id_specification = [
    ('version', r'\d{2}'), 			# version
    ('time', r'\d{8}'), 			# date : %Y%m%d
    ('postion', r'\d{10}'), 		# postion
    ('category', r'[A-Z]\d{4,10}'), # category
    ('tail', r'Z'), 				# category tial char 'Z'
    ('brand', r'[A-Z0-9]{4}'), 		# brand
    ('serial', r'[A-Z0-9]{6}')		# serial number
]
long_id_specification = [
    ('version', r'[A-Z]{2}\d{2}'), 			# version
    ('time', r'\d{14}'), 		 			# date : %Y%m%d
    ('postion', r'\d{14}'), 		 		# postion
    ('category', r'[A-Z]{3}\d{4,10}'),	 	# category
    ('tail', r'Z'), 				 		# category tial char 'Z'
    ('brand', r'[A-Z0-9]{6}'), 				# brand
    ('serial', r'[A-Z0-9]{8}')				# serial number
]

# 预编译，加速后续匹配速度
short_id_regex = re.compile(''.join('(?P<{}>{})'.format(pair[0], pair[1]) for pair in short_id_specification))
long_id_regex = re.compile(''.join('(?P<{}>{})'.format(pair[0], pair[1]) for pair in long_id_specification))

def parser(_id):
    regex = short_id_regex if _id[0] in '0123456789' else long_id_regex
    m = regex.match(_id)
    if m:
        # {'brand': 'DELL', 'version': '01', 'postion': '0020511400', 'category': 'A02010104',
        # 'time': '20170511', 'serial': 'CN0001', 'tail':'Z'}
        return m.groupdict()
    raise ValueError('id: {} is abnormal'.format(_id))

def parser_category(cate,category):#code to name
    #res = parser(_id)
    #cate = res["category"]
    #category = code_to_category()
    cate =cate.replace(" ",'')
    if len(cate)==5:
        c1, c2,c3 =str(cate[0]), str(cate[1:3]), str(cate[3:5])
        if isinstance(category[c1][c2][c3], dict):
            last_one = category[c1][c2][c3]['name']
        else:
            last_one = category[c1][c2][c3]
        res = '.'.join([category[c1]["name"], category[c1][c2]["name"], last_one])
        return res
    elif len(cate)==7:
        c1, c2, c3, c4 = str(cate[0]), str(cate[1:3]), str(cate[3:5]), str(cate[5:7])
        if isinstance(category[c1][c2][c3][c4], dict):
            last_one = category[c1][c2][c3][c4]['name']
        else:
            last_one = category[c1][c2][c3][c4]
        res = '.'.join([category[c1]["name"], category[c1][c2]["name"], category[c1][c2][c3]["name"],
                                    last_one])
        return res
    elif len(cate)==9:
        c1, c2, c3, c4, c5 = str(cate[0]), str(cate[1:3]), str(cate[3:5]), str(cate[5:7]), str(cate[7:9])
        if  isinstance(category[c1][c2][c3][c4][c5],dict) :
            last_one = category[c1][c2][c3][c4][c5]['name']
        else :
            last_one = category[c1][c2][c3][c4][c5]
        res = '.'.join([category[c1]["name"], category[c1][c2]["name"], category[c1][c2][c3]["name"],
                                    category[c1][c2][c3][c4]["name"], last_one])
        print (res)
        return res
    elif len(cate)==11:
        c1, c2, c3, c4, c5 ,c6= str(cate[0]), str(cate[1:3]), str(cate[3:5]), str(cate[5:7]), str(cate[7:9]),str(cate[9:11])
        if  isinstance(category[c1][c2][c3][c4][c5][c6],dict) :
            last_one = category[c1][c2][c3][c4][c5][c6]['name']
        else :
            last_one = category[c1][c2][c3][c4][c5][c6]
        res = '.'.join([category[c1]["name"], category[c1][c2]["name"], category[c1][c2][c3]["name"],
                                    category[c1][c2][c3][c4]["name"], category[c1][c2][c3][c4][c5]]['name'],last_one)
        return res
def parser_geocode(position,geocode):#code to name
    #postion =res["postion"]
    #geocode = code_to_geo(path='conf.d/geocode.yml')
    province, city, dis = str(position[4:6]), str(position[6:8]), str(position[8:10])
    #res["postion"] = ''.join([geocode[province]["name"], geocode[province][city]["name"], geocode[province][city][dis]])
    return ''.join([geocode[province]["name"], geocode[province][city]["name"], geocode[province][city][dis]])

if __name__ == '__main__':
    #print (parser_category("A02010207", CATEGORYS))
    start =time.time()
    print (parser("01201604050020440113A02010206Z07Q3002KO5"))
    print ("parser in %ss",time.time()-start)
