import os
import sys
from PIL import Image
import numpy as np
import glob


def export_image(im, index, fpath, fmt, step):
    subimg = im.crop((0, index, im.width, index+step-1))
    #subimg = tranparent(subimg)
    #subimg = replace_rgb(subimg, [(133, 210, 131)], (125, 176, 243))
    #subimg = replace_rgba(subimg, [(4, 4, 4, 255)], (63, 72, 204, 225))
    #subimg = replace_rgb(subimg, [(0, 255, 0)], (237, 28, 36, 225))
    #subimg = replace_rgb(subimg, [(108, 131, 59)], (44, 114, 199))
    #subimg = replace_hsl(subimg, (79, 126, 160), (143, 202, 165))
    #subimg = replace_hsl(subimg, (148, 80, 120), (234, 240, 53))
    #subimg = replace_hsl(subimg, (12, 160, 124), (80, 240, 60))
    subimg.save('%s.%s' %(fpath, fmt))

def seek_step(data, ch, height, step):
    while ch+step < height and not (np.all(data[ch+step, :] == [255, 255, 255, 255]) or np.all(data[ch+step, :] == [0, 0, 0, 0])):
        step += 1
    return step

def handle_image(fpath, srcdir, dstdir, step):
    rfd = os.path.relpath(os.path.dirname(fpath), srcdir)
    dstpath = os.path.join(dstdir, rfd)
    os.makedirs(dstpath, exist_ok = True)
    im = Image.open(fpath)
    data = np.asarray(im)
    count, ch = [0] * 2
    fn, ft = os.path.splitext(os.path.basename(im.filename))
    if im.height < step:
        export_image(im, ch, os.path.join(dstpath, fn), 'png', im.height)
    else:
        while ch < im.height:
            nstep = seek_step(data, ch, im.height, step)
            fnn, fnt = os.path.splitext(fn)
            print(fpath, count, ch)
            export_image(im, ch, os.path.join(dstpath, '%s_%d%s' %(fnn, count+1, fnt)), ft[1:], nstep)
            ch += nstep
            count += 1
    im.close()


def main(args):
    if len(args)<2:
        return

    steps = 500
    srcdir = os.path.normpath(os.path.abspath(args[0]))
    destdir = os.path.normpath(os.path.abspath(args[1]))

    if os.path.isdir(srcdir):
        for fpath in glob.glob(os.path.join(srcdir, '**', '*.png'), recursive=True):
            handle_image(fpath, srcdir, destdir, steps)
    else:
        handle_image(srcdir, os.path.dirname(srcdir), destdir, steps)


if __name__ == "__main__":
    main(sys.argv[1:])
