import os
import sys
import argparse
import CppHeaderParser

def handle_class_member_functions(classes):
    lines = []
    for cname, cv in classes.items():
        lines.extend(handle_fuctions(cv['methods']['public'], cname))
        lines.extend(handle_fuctions(cv['methods']['private'], cname))
    return lines

def handle_fuctions(functions, clsname=None):
    lines = []
    for func in functions:
        try:
            if not func['inline']:
                fh = func['debug'].strip(' \t\n;')
                if func['static']:
                    fh = fh[6::]
                if func['virtual']:
                    print(fh, func['returns'])
                else:
                    print(func['returns'])
                fh = fh.strip()
                rettp =  func['returns'].strip(' \t')
                if clsname:
                    sep = len(rettp)+1
                    fh = fh[:sep:] + clsname+ '::' +fh[sep::].lstrip()
                ret = func['returns_pointer']
                if not ret:
                    rettp = rettp.split(' ')
                    if len(rettp)>1:
                        fh = fh[len(rettp[0])::]
                ns = func['namespace']
                code ='''
%s%s
{
    return NULL;
}
                ''' %(ns if ns else '', fh.rstrip(), )
                lines.extend(code.splitlines())
        except Exception as e:
            print(func, e)
    return [line+'\n' for line in lines]


def generate_cpp_file(dstpath, fname, hdrdef):
    lines = ['#include "%s.h"\n' %(fname)]
    with open(os.path.join(dstpath, fname+'.cpp'), 'wt') as fp:
        #lines.extend(handle_fuctions(hdrdef.functions))
        lines.extend(handle_class_member_functions(hdrdef.classes))
        fp.writelines(lines)

def extract_file(fpath, dstpath, fname):
    try:
        os.makedirs(dstpath, exist_ok = True)
        hdrdef = CppHeaderParser.CppHeader(fpath)
        generate_cpp_file(dstpath, fname, hdrdef)
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
                if '.h' in f:
                    fpath = os.path.join(dirpath, f)
                    fn, _ = os.path.splitext(os.path.basename(f))
                    extract_file(fpath, os.path.normpath(dstpath), fn)
    else:
        fn, _ = os.path.splitext(os.path.basename(args.srcpath))
        extract_file(args.srcpath, dstpath, fn)
