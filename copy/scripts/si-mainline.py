# -*- coding: utf-8 -*-
"""系统消息补主线串联 + CSS"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
d = r'C:\Users\job_p\Desktop\NR-f40'
f = d + r'\系统消息-01-SSB-MIB-SIB1与OSI.html'
h = open(f, encoding='utf-8').read()

CSS = '.bridge { background:#f3f6fa; border:1px dashed #9db8d2; padding:10px 14px; margin:12px 0; font-size:14.5px; }\n.mainline { background:#fff8e6; border:2px solid #c55a11; padding:12px 16px; margin:16px 0; font-size:14.5px; }\n</style>'
h = h.replace('</style>', CSS, 1)

# 主线导览（插在 h1 后）
i = h.index('</h1>')
mainline = ('① 系统消息体系全景：三级递进（第 1 讲）→ ② SSB 同步信号块：UE 开机第一个要找的信号（第 2 讲）'
            '→ ③ MIB 与 PBCH：第一份参数与编码链（第 3 讲）→ ④ SIB1：小区接入标识与 OSI 调度总入口（第 4 讲）'
            '→ ⑤ OSI：SIB2~SIB9 逐块详解（第 5 讲）→ ⑥ SI 调度与获取：窗口公式 / 修改周期 / 按需请求 / 寻呼时机（第 6 讲）'
            '→ ⑦ 端到端九步流程回顾 + 易错点（第 7 讲）→ 练习册与计算器。每讲只回答主线一个问题。')
h = h[:i+5] + '\n<div class="mainline"><b>本专题主线（一条问题链贯穿全部讲次）</b>：' + mainline + '</div>\n' + h[i+5:]

bridges = [
    ('<h2>2. 第 2 讲', '第 1 讲全景说明了系统消息是三级递进体系（MIB → SIB1 → SI 消息）；主线下一个问题：三级递进的第一步——SSB 同步信号块，UE 开机后第一个要找的信号长什么样？（第 2 讲：时频结构、PSS/SSS 序列、PBCH DM-RS）'),
    ('<h2>3. 第 3 讲', 'SSB 找到了（第 2 讲），主线第二步：从 SSB 里的 PBCH 解出 MIB——UE 的第一份参数：24 bit 装了什么、怎么变成 864 bit 编码流？（第 3 讲）'),
    ('<h2>4. 第 4 讲', 'MIB 拿到了（第 3 讲），主线第三步：用它查表确定 CORESET#0，盲检得到 SIB1——小区接入标识与全部 OSI 调度信息的总入口（第 4 讲）。'),
    ('<h2>5. 第 5 讲', 'SIB1 拿到了（第 4 讲），主线第四步：按 si-SchedulingInfo 去收 OSI——SIB2~SIB9 分别是什么、给谁用（第 5 讲）。'),
    ('<h2>6. 第 6 讲', 'OSI 的内容清楚了（第 5 讲），主线第五步：UE 怎么按时按点把它们收下来——SI 窗口公式、修改周期、按需请求，以及寻呼时机 PF/PO 上的 Short Message 监听（第 6 讲）。'),
    ('<h2>7. 第 7 讲', '调度与获取机制清楚了（第 6 讲），主线收拢：把开机到驻留的端到端流程串成九步，并汇总全部易错点（第 7 讲）。'),
    ('<h2>8. 练习册', '主线七步走完，进入练习册自测（25 题）与交互式计算器。'),
]
for anchor, text in bridges:
    j = h.find(anchor)
    assert j > 0, '锚点缺失: ' + anchor[:20]
    h = h[:j] + '<div class="bridge"><b>承接</b>：' + text + '</div>\n' + h[j:]

# 主线收口（插在专题总结前）
closing = ('系统消息全貌一句话：SSB 提供同步与广播信道（第 2 讲）→ MIB 提供 CORESET#0 查表与 \\(k_{SSB}\\)（第 3 讲）'
           '→ SIB1 提供驻留、接入、公共配置与 OSI 调度信息（第 4 讲）→ SIB2~SIB9 按 SI 窗口周期播出、按需可取（第 5/6 讲）'
           '→ 寻呼时机上的 Short Message 驱动变更（第 6 讲补遗）→ 九步端到端（第 7 讲）。')
k = h.find('<h2>10. 专题总结')
assert k > 0, '收口锚点缺失'
h = h[:k] + '<div class="mainline"><b>主线收口</b>：' + closing + '</div>\n' + h[k:]

open(f, 'w', encoding='utf-8').write(h)
print('系统消息主线串联完成 | bridge:', h.count('class="bridge"'), '| mainline:', h.count('mainline'), '| 大小:', len(h))
