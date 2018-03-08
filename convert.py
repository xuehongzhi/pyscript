import os
import sys
import xlrd
import argparse


def _get_start_info(sheet):
    start, maxh = -1, 0
    for i in range(sheet.nrows):
        vals = sheet.row_values(i)
        if start < 0:
            try:
                start = vals.index('高度')
            except ValueError:
                pass
        if not maxh:
            for k, v in enumerate(vals):
                if isinstance(v, str) and '参照高度' in v:
                    maxh = int((vals[k+2])*1000+0.5)
                    break

        if start>=0 and maxh>0:
            break
    return start, maxh

#单文件转换
def _convert_single(book, dstpath, fname):
    vs, hs = [], []
    for i in range(book.nsheets):
        sheet = book.sheet_by_index(i)
        if sheet.nrows != 0:
            #main table
            start, maxh = _get_start_info(sheet)
            print(start, maxh)
            for col in range(0, 6, 2):
                col1 = sheet.col_values(start+col)
                col2 = sheet.col_values(start+col+1)
                assert(len(col1) == len(col2))
                for r, h in enumerate(col1):
                    try:
                        mmh = int(float(h)*1000 + 0.5)
                        lv = float(col2[r])
                        if mmh < maxh:
                            hs.extend(range(mmh, mmh+10))
                            vs.extend([float(lv)*1000]*10)
                        else:
                            hs.append(mmh)
                            vs.append(lv*1000)
                    except:
                        pass

            vs = [list(v) for v in zip(hs, vs)]
            vs.sort(key = lambda x: x[0])
            #print(','.join([str((k,v[0])) for k, v in enumerate(vs[:1000]) if k!=v[0]]))

            #mm table
            col6 = sheet.col_values(start+6)
            col8 = sheet.col_values(start+8)
            assert(len(col6) == len(col8))
            r = 0
            try:
                while r< len(col6):
                    if (col6[r] and isinstance(col6[r], float) or col6[r]==0) and isinstance(col8[r], float):
                        lh, uh = int(col6[r]*1000), int(col8[r]*1000)
                        h = lh + 1
                        while h < uh:
                            si = int(h % 10)
                            if si!=0:
                                vs[h][1] += 1000*float(col8[r+si])
                                #print('volume(%f) of height(%d)' %(vs[h+1][1], vs[h+1][0]))
                            h+=1
                        r += 10
                    else:
                        r+=1
            except:
                pass

            break
    assert(any([(vs[i][1] - vs[i-1][1])>0 for i, _ in enumerate(vs)]))

    fpath = os.path.join(dstpath, fname+'.csv')
    with open(fpath, 'wt') as fp:
        fp.write('罐高,体积\n')
        for v in vs:
            fp.write('%s\n' %(str(v).strip('[]')))
        fp.close()

def _convert_multiple(book, dstpath, fname):
    vtables = ['分米容量表', '厘米毫米容量表', '静压力修正容量表', '底量参考容量表']
    for i, tb in enumerate(vtables):
        sheet = book.sheet_by_name(tb)
        dstfpath = os.path.join(dstpath, fname)
        os.makedirs(dstfpath, exist_ok = True)
        dstfpath = os.path.join(dstfpath, 'vol%c.txt' %(i+ ord('a')))
        if tb!='厘米毫米容量表':
            col1 = sheet.col_values(0)
            col2 = sheet.col_values(1)
            assert(len(col1) == len(col2))
            vs = []
            for v in zip(col1, col2):
                try:
                    vs.append('%d\t%d\n' %(int(float(v[0]*100+0.5)), int(float(v[1]*1+0.5))))
                except:
                    pass
            if len(vs) != 0:
                with open(dstfpath, 'wt') as fp:
                    fp.writelines(vs)
                    fp.close()

        else:
            row, col = -1, -1
            for r in range(sheet.nrows):
                for c in range(sheet.ncols):
                    v = sheet.cell_value(r, c)
                    if isinstance(v, str) and v.startswith('起点'):
                        row, col = r, c
                        break
                if row>=0 and col >= 0:
                    break

            if row<0 or col<0:
                return
            with open(dstfpath, 'wt') as fp:
                for r in range(row+1, sheet.nrows, 2):
                    try:
                        fp.write('%s\n' %(' '.join([str(int(v*100+0.5)) for v in sheet.row_values(r, col+0, col+2)]),))
                    except:
                        pass
                    else:
                        fp.write('0 %s\n' %(' '.join([str(int(v+0.5)) for v in sheet.row_values(r, col+3, col+12)]),))
                        fp.write('0 %s\n' %(' '.join([str(int(v+0.5)) for v in sheet.row_values(r+1, col+3, col+12)]),))
                fp.close()




def convert_file(fpath, dstpath):
    try:
        book = xlrd.open_workbook(fpath)
        fname = os.path.splitext(os.path.basename(fpath))[0]
        os.makedirs(dstpath, exist_ok = True)
        if '分米容量表' in book.sheet_names():
            _convert_multiple(book, dstpath, fname)
        else:
            _convert_single(book, dstpath, fname)
    except Exception as e:
           print("%s convert failed, reason:(%s)" %(fpath, str(e)))
                    #SingleConverter(book, dstpath).convert()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='博瑞特罐容表转换器.')
    parser.add_argument('srcpath', metavar='PATH', type=str,
                    help='原文件或目录路径')
    parser.add_argument('-o', dest='outdir', help='导出文件存储路径')
    args = parser.parse_args(sys.argv[1:])
    if not os.path.exists(args.srcpath):
        raise Exception('无效文件路径')

    dstpath = args.outdir
    if not dstpath:
        dstpath = os.getcwd()

    if os.path.isdir(args.srcpath):
        for dirpath, _, filenames in os.walk(args.srcpath):
            for f in filenames:
                fpath = os.path.join(dirpath, f)
                convert_file(fpath, dstpath)
    else:
        convert_file(args.srcpath, dstpath)
