# -*- coding: utf-8 -*-
"""CSI 文档：比喻词清理 + 裸变量 MathJax 化"""
import re

f = r'C:\Users\job_p\Desktop\NR-f40\CSI-01-信道状态信息全梳理.html'
h = open(f, encoding='utf-8').read()
parts = re.split(r'(<svg\b[\s\S]*?</svg>)', h)

def repl(s):
    # 比喻词
    s = s.replace('CSI 测量的"尺子"是什么？——CSI-RS（信道状态信息参考信号），一把 gNB 放下行参考信号、UE 测量信道的"尺子"。本讲讲它的序列生成',
                  'CSI 测量的参考信号是什么？——CSI-RS（信道状态信息参考信号），即 gNB 发送、UE 用于测量信道的下行参考信号。本讲讲它的序列生成')
    s = s.replace('<b>NZP CSI-RS = 有能量的"尺子"</b>', '<b>NZP CSI-RS = 有能量的参考信号</b>')
    s = s.replace('<b>ZP CSI-RS = "挖空的洞"</b>——这些 RE 上 gNB 不发任何东西', '<b>ZP CSI-RS = 不发射能量的预留 RE</b>——这些 RE 上 gNB 不发任何东西')
    s = s.replace('NZP CSI-RS = 信道测量尺子；ZP CSI-RS（含 CSI-IM）= 干扰测量的"空位"。', 'NZP CSI-RS 用于信道测量；ZP CSI-RS（含 CSI-IM）用于干扰测量。')
    s = s.replace('gNB 用 NZP CSI-RS 当"尺子"让 UE 量信道、用 CSI-IM 当"空位"让 UE 量干扰', 'gNB 用 NZP CSI-RS 供 UE 做信道测量、用 CSI-IM 供 UE 做干扰测量')
    s = s.replace('上报配置是"UE 的作业本"（怎么答题），资源配置是"考卷"（在哪测），触发状态是"点名"（何时交卷）。三者解耦后',
                  '上报配置规定报什么与何时报，资源配置规定测什么与在哪测，触发状态把两者绑定并由 DCI/MAC CE 触发。三者解耦后')
    s = s.replace('按 periodic/SP/aperiodic 三种节奏交卷；gNB 收卷后做链路自适应与波束管理', '按 periodic/SP/aperiodic 三种类型上报；gNB 收到后做链路自适应与波束管理')
    s = s.replace('（DCI 触发时一并"点名"资源）', '（DCI 触发时一并指示资源）')
    s = s.replace('触发状态点名：ReportConfig', '触发状态指示：ReportConfig')
    # 裸变量（负向断言避免命中已 LaTeX 的 \(M_s 形式）
    s = re.sub(r'(?<![\\a-zA-Z])K_s(?![}])', r'\\(K_s\\)', s)
    s = re.sub(r'(?<![\\a-zA-Z])M_s(?![}])', r'\\(M_s\\)', s)
    return s

for i in range(0, len(parts), 2):
    parts[i] = repl(parts[i])
h2 = ''.join(parts)
open(f, 'w', encoding='utf-8').write(h2)

body = re.sub(r'<svg\b[\s\S]*?</svg>', '', h2)
bw = len(re.findall(r'尺子|交卷|考卷|作业本|点名|挖空', body))
vr = len(re.findall(r'(?<![\\a-zA-Z])(?:K_s|M_s|N_CPU|Z_ref|nCSI_ref)(?![}])', body))
print('比喻词残留:', bw)
print('变量残留:', vr)
print('MathJax inline:', len(re.findall(r'(?<!\\)\\\(', h2)), '/', len(re.findall(r'(?<!\\)\\\)', h2)))
