import os, sys
import glob
import shutil

def merge(dstpath):
    from itertools import groupby
    files = list(glob.glob(os.path.join(dstpath, '**', '*[!.png]'), recursive=True))
    for k, v in groupby(files, key=lambda f: f.split('_')[0] + os.path.splitext(f)[1]):
        v = list(v)
        if len(v) > 1:
            with open(k, 'wt') as wfp:
                for vv in v:
                    print('merge file:({0})'.format(vv))
                    try:
                        with open(vv, 'rt') as rfp:
                            for line in rfp.readlines():
                                line = line.strip()
                                print(line)
                                if line:
                                    wfp.write(line+'\n')
                        os.remove(vv)
                    except Exception as e:
                        print('{0} copy failed:({1})'.format(vv, e))


def main(args):
    fpath = os.path.normpath(os.path.abspath(args[0]))
    merge(fpath)


if __name__ == '__main__':
    main(sys.argv[1:])

