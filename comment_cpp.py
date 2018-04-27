import re

def loadtxt(filename):
    "Load text file into a string. I let FILE exceptions to pass."
    f = open(filename)
    txt = ''.join(f.readlines())
    f.close()
    return txt

# regex group1, name group2, arguments group3
rproc = r"((\w+(\*)*)\s+([\w::]*\w+)\s*\(([\w\s,<>\[\].=&':/*]*?)\)\s*(const)?\s*)"
cppwords = ['if', 'while', 'do', 'for', 'switch']
fl = []
lines = []
isfunc = False
rettype = 'void'
with open('proxydchelp.cpp', 'r+') as fp:
    for line in fp.readlines():
        compress_line = line.strip()
        if 'return pRefDC->' in compress_line and compress_line.startswith('//'):
            line = line.replace('/', '')
        lines.append(line)
    fp.seek(0)
    fp.writelines(lines)

def main():
    with open('proxydchelp.cpp', 'r+') as fp:
        for line in fp.readlines():
            compress_line = line.strip()
            mo = re.match(rproc, compress_line)
            if mo:
                isfunc = True
                rettype = mo.group(2)
            if isfunc:
                if compress_line.endswith('{'):
                    if fl:
                        line = '//' + line
                    fl.append('{')

                elif compress_line.endswith('}'):
                    fl.pop()
                    if fl:
                        line = '//'+line
                    else:
                        if 'void' not in rettype:
                            lines.append('\treturn NULL;\n')
                        isfunc = False
                elif not mo:
                    line = '//'+line
            lines.append(line)
        fp.seek(0)
        fp.writelines(lines)

