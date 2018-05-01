import os
import sys
import argparse
import CppHeaderParser
from tempfile import gettempdir

def handle_class_member_functions(classes):
    lines = []
    for cname, cv in classes.items():
        if not cv.get('template'):
            lines.extend(handle_fuctions(cv['methods']['public'], classes))
            lines.extend(handle_fuctions(cv['methods']['private'], classes))
            lines.extend(handle_fuctions(cv['methods']['protected'], classes))
    return lines

def get_func_ret(func, classes=None):
    rettp = func['returns'].strip().split(' ')[-1::]
    if func['constructor'] or func['destructor'] or not rettp:
        return '', ''

    rettp = rettp[0]
    retv = 'return NULL;'
    if rettp == 'double':
        retv = 'return 0.0;'
    elif rettp in ['float', 'int', 'bool']:
        retv = 'return '+str(eval(rettp+'(0)')).lower()+';'
    elif rettp=='void':
        retv = ''
    #namespace
    if classes:
        clsinst = classes.get(rettp)
        if clsinst and clsinst['namespace']:
            rettp = clsinst['namespace'] + '::' + rettp
    # const
    if func['returns_pointer']:
        rettp += '*'
    elif func['returns_reference']:
        rettp += '&'
        retv = 'return *(this);'
    ret_const = func.get('returns_const')
    if ret_const:
        if 'void' in func['rtnType'] and rettp.endswith('*'):
            rettp = rettp[:-1:] + ' const ' + rettp[-1::]
        else:
            rettp ='const ' + rettp

    return rettp, retv


def get_func_params(parameters):
    params = []
    for param in parameters:
        spar = ''
        if param.get('constant'):
            spar = 'const ' + spar  # const
        spar += param['raw_type']
        if param['pointer']:
            spar += '*'
        elif param['reference']:
            spar += '&'
        spar = spar + ' ' +  param['name']
        if param.get('array'):
            spar += '['
            sz = param.get('array_size')
            if sz:
                spar += str(sz)
            spar += ']'
        params.append(spar)
    return ','.join(params)

def handle_fuctions(functions, clsname=None):
    lines = []
    for func in functions:
        try:
            if not func.get('inline') and not func.get('defined') and not func.get('pure_virtual'):
                #retval [classname::]function(paramter list) [const]
                rettp, retv = get_func_ret(func, clsname)
                funcname = func['name']
                if func.get('destructor'):
                    funcname = '~'+funcname
                code ='''
%s %s%s(%s) %s
{
    %s
}
''' %(rettp, '%s::' %(func['path'],) if func.get('path') else '', funcname,
      get_func_params(func['parameters']), 'const' if func.get('const') else '', retv )
                lines.extend(code.splitlines())
        except Exception as e:
            print(e)
    return [line+'\n' for line in lines]


def generate_cpp_file(dstpath, fname, hdrdef):
    lines = ['#include "stdafx.h"\n', '#include "%s.h"\n' %(fname)]
    with open(os.path.join(dstpath, fname+'.cpp'), 'wt') as fp:
        lines.extend(handle_fuctions(hdrdef.functions, hdrdef.classes))
        lines.extend(handle_class_member_functions(hdrdef.classes))
        fp.writelines(lines)

#预处理头文件,去掉class前面的修饰符
def preprocss_header(fpath, tempdir, fname):
    os.makedirs(tempdir, exist_ok = True)
    tempath = os.path.join(tempdir, fname)
    lines = []
    with open(fpath, 'rt') as rfp, open(tempath, 'wt') as wfp:
        for line in rfp.readlines():
            pl = line.strip();
            if pl.startswith('class') or pl.startswith('struct'):
                e = pl.index(':') if ':' in pl else len(pl)
                clsname = pl[pl.index(' '):e:].strip()
                decorator, _ ,clsname = clsname.rpartition(' ')
                if decorator:
                    line = line.replace(decorator+' ', '')
            lines.append(line)
        wfp.writelines(lines)
    return tempath

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
                    tempdir = os.path.join(gettempdir(), os.path.basename(dirpath))
                    fpath = preprocss_header(fpath, tempdir, f)
                    extract_file(fpath, os.path.normpath(dstpath), fn)
    else:
        fn, _ = os.path.splitext(os.path.basename(args.srcpath))
        tempath = preprocss_header(args.srcpath,
                                   os.path.join(gettempdir(), os.path.basename(os.path.dirname(args.srcpath))),
                                   fn)
        print(tempath)
        extract_file(tempath, dstpath, fn)
