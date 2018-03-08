import os
import sys
import struct
import ctypes
import win32api
import win32gui
import win32gui_struct
from win32con import PAGE_READWRITE, MEM_COMMIT, MEM_RESERVE, MEM_RELEASE, PROCESS_ALL_ACCESS
from commctrl import TVI_ROOT, TVM_GETITEM, TVM_GETNEXTITEM, TVIF_SELECTEDIMAGE, TVGN_NEXT,\
    TVIF_CHILDREN, TVIF_IMAGE, TVIF_TEXT, TVIF_HANDLE, TVGN_CHILD, TVM_EXPAND, TVE_COLLAPSE,\
    TVE_EXPAND, TVIS_STATEIMAGEMASK, TVIF_STATE
from PIL import Image

dstpath = 'd:\\outico'


GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
VirtualAllocEx = ctypes.windll.kernel32.VirtualAllocEx
VirtualFreeEx = ctypes.windll.kernel32.VirtualFreeEx
OpenProcess = ctypes.windll.kernel32.OpenProcess
WriteProcessMemory = ctypes.windll.kernel32.WriteProcessMemory
ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory

def get_table_maps():
    from tabledef import table_definition
    ts = {}
    for k, v in table_definition.items():
        if not ts.get(v[0]):
            ts[v[0]] = k.lower()

    return ts

def get_item_info(hwnd,hProcHnd, pTVI, pBuffer, hItem, expand=TVE_COLLAPSE):

    '''
        _menuinfo_fmt = 'iPiiPiiiiP'
        UINT      mask;
        HTREEITEM hItem;
        UINT      state;
        UINT      stateMask;
        LPTSTR    pszText;
        int       cchTextMax;
        int       iImage;
        int       iSelectedImage;
        int       cChildren;
        LPARAM    lParam;
    '''

   #win32gui.SendMessage(hwnd, TVM_EXPAND, expand, hItem)
    tvitem_str = struct.pack('iPiiPiiiiP',
                            *[TVIF_TEXT| TVIF_HANDLE | TVIF_IMAGE | TVIF_CHILDREN, hItem, 0, 0, pBuffer, 4096, 0,0,0,0])
    tvitem_buffer = ctypes.create_string_buffer(tvitem_str)
    copied = ctypes.create_string_buffer(4)
    p_copied = ctypes.addressof(copied)

    WriteProcessMemory(hProcHnd, pTVI, ctypes.addressof(tvitem_buffer), ctypes.sizeof(tvitem_buffer), p_copied)
    win32gui.SendMessage(hwnd, TVM_GETITEM, 0, pTVI)

    text_buff = ctypes.create_string_buffer(4096)
    target_buff = ctypes.create_string_buffer(40)
    ReadProcessMemory(hProcHnd, pBuffer, ctypes.addressof(text_buff), 4096, p_copied)
    ReadProcessMemory(hProcHnd, pTVI, target_buff, 40, p_copied)


    target_str = struct.unpack('iPiiPiiiiP', target_buff)
    return text_buff.value.decode('gbk'), target_str[8], target_str[6]

def getItems(hwnd):
    from split_image import export_image
    tbs = get_table_maps()
    dstpath = "d:\\outico3"
    os.makedirs(dstpath, exist_ok = True)
    im = Image.open('E:\\02.resource\\ico\\gptico\\GPTMap_179.bmp')
    pid = ctypes.create_string_buffer(4)
    p_pid = ctypes.addressof(pid)

    GetWindowThreadProcessId(hwnd, p_pid) # process owning the given hwnd
    hProcHnd = OpenProcess(PROCESS_ALL_ACCESS, False, struct.unpack("i",pid)[0])
    pTVI = VirtualAllocEx(hProcHnd, 0, 4096, MEM_RESERVE|MEM_COMMIT, PAGE_READWRITE)
    pBuffer = VirtualAllocEx(hProcHnd, 0, 4096, MEM_RESERVE|MEM_COMMIT, PAGE_READWRITE)

    # iterate items in the SysListView32 control

    hRoot = win32gui.SendMessage(hwnd, TVM_GETNEXTITEM, TVGN_CHILD, TVI_ROOT)
    hChild = win32gui.SendMessage(hwnd,  TVM_GETNEXTITEM, TVGN_CHILD, hRoot)
    while hChild:
        itxt, istate, iimage = get_item_info(hwnd, hProcHnd, pTVI, pBuffer, hChild)
        print(itxt, istate)
        try:
            fn = itxt[:itxt.index('(')]
            if fn.startswith('井斜'):
                fn = '井轨迹'
            if fn.startswith('测井'):
                fn = '测井曲线'
        except:
            fn = itxt
        fn = tbs.get(fn)

        if fn:
            fn = os.path.join(dstpath, 'data-'+fn)
            export_image(im, iimage*16, fn)
            if istate!=0:
                export_image(im, (iimage+1)*16, fn+'-expand')

        hChild = win32gui.SendMessage(hwnd,  TVM_GETNEXTITEM, TVGN_NEXT, hChild)

    VirtualFreeEx(hProcHnd, pBuffer, 0, MEM_RELEASE)
    VirtualFreeEx(hProcHnd, pTVI, 0, MEM_RELEASE)
    win32api.CloseHandle(hProcHnd)


if __name__ == "__main__":
    hwnd = int(sys.argv[1].lstrip('0x'), base=16)
    print(hwnd)
    getItems(hwnd)
