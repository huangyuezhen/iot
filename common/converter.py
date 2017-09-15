'''
    实现36进制-int的转换。
    不同位数，其范围不同，需要重新实现，并注意异常
    4位 ： 0000-ZZZZ （0-1679615）
    6位 ： 000000-ZZZZZZ 

    是否需要补全(4|6)：
        AF ： 00AF
'''

import string

_36_SETS_ = string.digits + string.ascii_uppercase

_36_MAPS_ = {v:n for n,v in enumerate(_36_SETS_)}


def to_36(_in):
    '''
        int to 36进制
    '''
    # 是否需要输入类型检测
    assert isinstance(_in, int) and _in > 0
    _out = []
    while _in:
        _in,_r = divmod(_in, 36)
        _out.insert(0, _36_SETS_[_r])

    return ''.join(_out)

def to_int(_data):
    '''
        36 to in
        convert to upper ?
        check charsets[0-9A-Z] ?
    '''
    _rdata = _data[::-1]
    _out = 0
    for n,v in enumerate(_rdata):
        _out += _36_MAPS_[v]*36**n

    return _out


if __name__ == '__main__':
    #n = 1000000
    n = 10009
    _out = to_36(n)
    print(n, _out)

    #_in = to_int('ZZZZ')
    _in = to_int('00255R')
    print(_out, _in)
    


