import os, sys
import base64
import hashlib as hl
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from datetime import datetime
import random, string
import json
import ssl
import time
import glob



def get_file_content(fpath):
    with open(fpath, 'rb') as fp:
        data = fp.read()
        return base64.b64encode(data)

def get_sign(params, appkey):
    try:
        par = urlencode(sorted(params.items(), key=lambda x:x[0].upper()))
        return hl.md5('{0}&app_key={1}'.format(par, appkey).encode()).hexdigest().upper()
    except Exception as e:
        print('get sign failed: '+ str(e))
    return None


def ocr(fpath, url, appkey):
    params = {
        'app_id': '2109043099'
    }
    params['time_stamp'] =  str(int(datetime.now().timestamp()))
    params['nonce_str']  = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    params['image'] = get_file_content(fpath)
    params['sign'] = get_sign(params, appkey)
    print(params['sign'], params['time_stamp'])
    ssl._create_default_https_context = ssl._create_unverified_context
    try:
        r = Request(url, data=urlencode(params).encode(), method='POST')
        resp = urlopen(r)
        data = json.loads(resp.read().decode())
        if data['ret'] != 0:
            print(fpath+' ocr failed:({0})'.format(data['msg']))
        else:
            with open(fpath.replace('.png', ''), 'wt') as fp:
                for item in data['data']['item_list']:
                    fp.write('.'.join([s.strip() for s in item['itemstring'].split('.')])+'\n')
            os.remove(fpath)
    except Exception as e:
        print('{1} ocr failed:({0})'.format(e, fpath))


def merge(dstpath):
    from itertools import groupby
    from shutil import copyfileobj
    files = list(glob.glob(os.path.join(dstpath, '**', '*.*'), recursive=True)).sort()
    for k, v in groupby(files, key=lambda f: f[:len(f) if '_' in f else f.index('-')]):
        with open(k, 'wb') as wfp:
            for vv in v:
                with open(vv, 'rb') as rfp:
                    copyfileobj(rfp, wfp, 1024*1024*10)




def main(args):
    fpath = os.path.normpath(os.path.abspath(args[0]))
    url = 'https://api.ai.qq.com/fcgi-bin/ocr/ocr_generalocr'
    appkey = 'B7TootEt2tcH33sU'

    if os.path.isdir(fpath):
        for f in glob.glob(os.path.join(fpath, '**', '*.png'), recursive=True):
            try:
                ocr(f, url, appkey)
                time.sleep(2.)
            except KeyboardInterrupt:
                break
    else:
        ocr(fpath, url, appkey)


if __name__ == '__main__':
    main(sys.argv[1:])

