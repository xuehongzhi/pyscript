import os
import colorsys
import math
import sys
from PIL import Image

def replace_rgb(img, olds, new):
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = []
    for item in datas:
        if any([item[0] == r and item[1] == g and item[2]==b for r, g, b in olds]):
            newData.append(new)
        else:
            newData.append(item)
    img.putdata(newData)
    return img


def replace_rgba(img, olds, new):
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = []
    for item in datas:
        if any([item[0] == r and item[1] == g and item[2]==b and item[3] == a for r, g, b, a in olds]):
            newData.append(new)
        else:
            newData.append(item)
    img.putdata(newData)
    return img

def replace_hsl(img, old, new):
    oh, os, ol = old[0], old[1], old[2]
    nh, ns, nl = new[0], new[1], new[2]
    img = img.convert('RGB')
    datas = img.getdata()
    newData = []
    for item in datas:
        h, l, s = colorsys.rgb_to_hls(item[0]/255, item[1]/255, item[2]/255)
        h = int(h*239)
        l = int(l*240)
        s=int(s*240)
        if abs(h - oh) <= 1 :  #and abs(l - ol) <= 1:
            #print(h,s,l)
            r, g, b = colorsys.hls_to_rgb((nh+h-oh)/239, (nl+l-ol)/240, (ns+s-os)/240)
            #print(r,g,b)
            newData.append((int(r*255), int(g*255), int(b*255)))
        else:
            newData.append(item)
    img.putdata(newData)
    return img


def tranparent(img):
    return replace_rgb(img, [(255, 255, 255),(192, 192, 192)], (255, 255, 255, 0))

def export_image(im, index, fpath, fmt='png', step=16):
    subimg = im.crop((index, 0, index+step-1, im.height))
    #subimg = tranparent(subimg)
    #subimg = replace_rgb(subimg, [(133, 210, 131)], (125, 176, 243))
    subimg = replace_rgba(subimg, [(4, 4, 4, 255)], (63, 72, 204, 225))
    subimg = replace_rgb(subimg, [(0, 255, 0)], (237, 28, 36, 225))
    subimg = replace_rgb(subimg, [(108, 131, 59)], (44, 114, 199))
    #subimg = replace_hsl(subimg, (79, 126, 160), (143, 202, 165))
    #subimg = replace_hsl(subimg, (148, 80, 120), (234, 240, 53))
    #subimg = replace_hsl(subimg, (12, 160, 124), (80, 240, 60))
    subimg.save('%s.%s' %(fpath, fmt))


def main(args):
    steps = [8, 16, 22, 24, 32, 64]
    dstpath = 'd:\\outico1'
    if len(args)<1:
        return

    if len(args)>1:
        print(dstpath)
        dstpath = args[1]

    os.makedirs(dstpath, exist_ok= True)
    im = Image.open(args[0])
    fn = os.path.splitext(os.path.basename(im.filename))[0]
    step = min(steps, key=lambda x:abs(x-im.height))
    for i in range(0, im.width, step):
        export_image(im, i, os.path.join(dstpath, '%s_%d' %(fn, i/step+1)), 'png', step)

    im.close()

if __name__ == "__main__":
    main(sys.argv[1:])
