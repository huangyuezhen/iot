'''
    read geocode file
'''
from common import util

CITYS = {}
PROVINCES = {}
REGIONS = {}
GEOCODE ={}

def parse_geo(path='conf.d/geocode.yml'):
    geocode = util.read_yaml(path)
    provinces = {}
    citys = {}
    regions = {}

    for key in geocode:
        # province
        province = geocode[key]
        p_name = province.pop('name')
        provinces[p_name] = key
        citys[p_name] = {}
        regions[p_name] = {}
        for k1 in province:
            city = province[k1]
            if isinstance(city, dict):
                name = city.pop('name')
                citys[p_name][name] = k1
                regions[p_name][name] = {v:k for k,v in city.items()}
            else:
                citys[p_name][city] = k1

    return provinces, citys, regions

def init():
    global PROVINCES, CITYS, REGIONS,GEOCODE
    if PROVINCES:
        return
    PROVINCES, CITYS, REGIONS = parse_geo()
    GEOCODE = code_to_addr()
def code_to_addr(path='conf.d/geocode.yml'):
    GEOCODE = util.read_yaml(path)
    return GEOCODE

if __name__ == '__main__':
    provinces, citys, regions = parse_geo('../conf.d/geocode.yml')
    #print(provinces, citys)

else:
    init()
