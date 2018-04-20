import os
import sys
import subprocess
import argparse

def extract_file(fpath, dstpath):
    try:
        os.makedirs(dstpath, exist_ok = True)
        subprocess.call(['ResourcesExtract.exe', '/Source', fpath, '/DestFolder','%s' % (dstpath),
                        '/ExtractIcons', '1', '/ExtractCursors', '1', '/ExtractBitmaps', '1',
                         '/ExtractAnimatedIcons ','1', '/ExtractAnimatedCursors', '1',
                         '/OpenDestFolder', '0'])
        print("%s convert success!!" %(fpath, ))
    except Exception as e:
           print("%s convert failed, reason:(%s)" %(fpath, str(e)))
                    #SingleConverter(book, dstpath).convert()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='资源批量提取.')
    parser.add_argument('srcpath', metavar='PATH', type=str,
                    help='资源路径')
    parser.add_argument('-o', dest='outdir', help='导出资源存储路径')
    args = parser.parse_args(sys.argv[1:])
    if not os.path.exists(args.srcpath):
        raise Exception('无效文件路径')

    dstpath = args.outdir
    if not dstpath:
        dstpath = os.getcwd()

    if os.path.isdir(args.srcpath):
        for dirpath, _, filenames in os.walk(args.srcpath):
            for f in filenames:
                f = f.lower()
                if '.dll' in f or '.exe' in f:
                    fpath = os.path.join(dirpath, f)
                    fn, _ = os.path.splitext(os.path.basename(f))
                    extract_file(fpath, os.path.join(dstpath,fn))
    else:
        extract_file(args.srcpath, dstpath)
