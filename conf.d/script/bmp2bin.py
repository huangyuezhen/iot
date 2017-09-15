def pilrbmp(inpath,outpath,_value=1):
    """
    把一张bmp图(RGB 或者8bit)转换为一个不带头文部信息
    的二值化二进制文件(一个字节存储8个像素)
    :param inpath: bmp 文件路径
    :param outpath: 二进制文件输出路径（含文件名）
    :param _value:灰度图转化为二值图的阈值，默认为164(经测试这个值较好)
    :return:
    """
    import struct
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
if __name__ == '__main__':
    inpath = "E:\\bmp\\格力壁挂式2匹 KFR-26GW.bmp"
    for _value in range (164,176,4):
         bmp_name = str(_value) + "_格力壁挂式2匹 KFR-26G.bin"
         outpath = "E:\\bmp\\result\\" + bmp_name
         pilrbmp(inpath, outpath, _value)