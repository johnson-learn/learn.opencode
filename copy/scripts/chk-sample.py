# -*- coding: utf-8 -*-
import re

d = r'C:\Users\job_p\Desktop\NR-f40'
h = open(d + r'\系统消息-01-SSB-MIB-SIB1与OSI.html', encoding='utf-8').read()
i = h.find('MIB ::=')
print(h[i-40:i+700])
