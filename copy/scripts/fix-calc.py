# -*- coding: utf-8 -*-
import io, re

p = r'<用户桌面目录>\NR-f40\PUCCH-物理上行控制信道全梳理.html'
t = io.open(p, encoding='utf-8').read()
a = 'var ms=1000/(scs/15)*0.5;'
b = 'var ms=0.5*15/scs;'
n = t.count(a)
t = t.replace(a, b)
io.open(p, 'w', encoding='utf-8').write(t)
print('PUCCH calc fixed:', n)

p2 = r'<用户桌面目录>\NR-f40\随机接入-SSB到RRC全流程.html'
t = io.open(p2, encoding='utf-8').read()
m = re.search(r'<li>非限制集下一根 L=839.{0,220}?</li>', t)
if m:
    new = '<li>非限制集下 L=839、N_CS=13，一根可产几个前导、64 个前导需几根？　A. 63 个、2 根　B. 64 个、1 根　C. 64 个、2 根　D. 65 个、1 根　<span class="ans">答案：B（⌊839/13⌋=64 恰满，一根产齐 64 个前导）</span></li>'
    t = t.replace(m.group(0), new)
    io.open(p2, 'w', encoding='utf-8').write(t)
    print('RA q7 fixed')
else:
    print('RA q7 NOT FOUND')
