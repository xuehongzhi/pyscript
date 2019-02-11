import os
import sys
import subprocess
import argparse
import glob
import winreg as reg
'''
  https://docs.microsoft.com/en-us/visualstudio/install/create-an-offline-installation-of-visual-studio?view=vs-2017

  vs_buildtools.exe --layout d:\VS_BuildTools2017_offline
  --add Microsoft.VisualStudio.Component.VC.140 --lang en-US
'''
def install_file(fpath, dstpath):
    try:
        os.makedirs(dstpath, exist_ok = True)
        subprocess.call(['msiexec.exe', '/a', fpath, 'TARGETDIR=%s' % (dstpath), '/qn'])
        print("%s install success!!" %(fpath, ))
    except Exception as e:
           print("%s install failed, reason:(%s)" %(fpath, str(e)))
                    #SingleConverter(book, dstpath).convert()




def get_app_bit(dstpath):
    import struct
    import platform
    IMAGE_FILE_MACHINE_I386=332
    IMAGE_FILE_MACHINE_IA64=512
    IMAGE_FILE_MACHINE_AMD64=34404
    filepath = glob.glob(os.path.join(dstpath, '*.dll'))[:1]
    if not filepath:
        return None

    app_bit = 32
    with open(filepath, 'rb') as f:
        s=f.read(2)
        if s == 'MZ':
            f.seek(60)
            s=f.read(4)
            header_offset=struct.unpack("<L", s)[0]
            f.seek(header_offset+4)
            s=f.read(2)
            machine=struct.unpack("<H", s)[0]

            if machine==IMAGE_FILE_MACHINE_I386:
                app_bit = 32
            elif machine==IMAGE_FILE_MACHINE_IA64:
                app_bit = 64
            elif machine==IMAGE_FILE_MACHINE_AMD64:
                os_bit = 64
    return  app_bit



def reg_visual_studio(dstpath):
    rkey = reg.CreateKey(reg.HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\VisualStudio\SxS')
    reg.SetValue(reg.CreateKey(rkey, 'VS7'), '14.0', reg.REG_SZ, dstpath)
    vc_key = reg.CreateKey(rkey, 'VC7')
    reg.SetValue(vc_key, '14.0', reg.REG_SZ, os.path.join(dstpath))
    # NETFRAMEWORK register
    # folder and version
    osbit = get_app_bit(dstpath)
    ver = os.path.basename(dstpath)
    fwk_folder =  input("Enter .NET Framework Directory:")
    reg.SetValue(vc_key, 'FrameWorkDir{0}'.format(osbit), reg.REG_SZ, fwk_folder)
    fwk_ver =  input("Enter .NET Framework Version:")
    reg.SetValue(vc_key, 'FrameWorkVer{0}'.format(osbit), reg.REG_SZ, fwk_ver)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='vs2015 install.')
    parser.add_argument('srcpath', metavar='PATH', type=str,
                    help='资源路径')
    parser.add_argument('-o', dest='outdir', help='安装路径')
    args = parser.parse_args(sys.argv[1:])
    if not os.path.exists(args.srcpath):
        raise Exception('无效文件路径')

    dstpath = args.outdir
    if not dstpath:
        dstpath = os.getcwd()

    os.makedirs(dstpath, exist_ok = True)

    #msis = glob.glob(os.path.join(args.srcpath, '*VisualC.140*', '*.msi'), recursive=True)
    msis = glob.glob(os.path.join(args.srcpath, '**', '*.msi'), recursive=True)
    print(msis)
    for installer in msis:
        install_file(installer, dstpath)
