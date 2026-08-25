# -*- coding: utf-8 -*-
import re

f = r'<用户桌面目录>\NR-f40\CSI-信道状态信息全梳理.html'
h = open(f, encoding='utf-8').read()
# 1) 翻译段 </div> 笔误
h = h.replace('包含一个关联的 CSI-ReportConfig。</div>', '包含一个关联的 CSI-ReportConfig。</p>')
# 2) 比喻词
h = h.replace(
    'gNB 用 NZP CSI-RS 当"尺子"让 UE 量信道、用 CSI-IM 当"空位"让 UE 量干扰；UE 按依赖链（CRI→RI→PMI→CQI→LI）算好答案，按 periodic/SP/aperiodic 三种节奏交卷；gNB 收卷后做链路自适应与波束管理',
    'gNB 用 NZP CSI-RS 供 UE 做信道测量、用 CSI-IM 供 UE 做干扰测量；UE 按依赖链（CRI→RI→PMI→CQI→LI）计算上报值，按 periodic/SP/aperiodic 三种类型上报；gNB 收到后做链路自适应与波束管理')
h = h.replace('算好了，怎么交卷？', '算好了，怎么交付？')
h = h.replace('一次 DCI/MAC CE 把哪些上报配置与资源集一起点名', '一次 DCI/MAC CE 把哪些上报配置与资源集一起触发')
open(f, 'w', encoding='utf-8').write(h)
body = re.sub(r'<svg\b[\s\S]*?</svg>', '', h)
print('比喻词:', len(re.findall(r'尺子|交卷|考卷|作业本|点名|挖空|灯塔|司令|户口本', body)))
toks = re.findall(r'<div[\s>]|</div>|<table[\s>]|</table>|<pre[\s>]|</pre>|<figure[\s>]|</figure>|<h2>|</h2>|<h3>|</h3>', h)
depth = 0; err = 0
for t in toks:
    depth += -1 if t.startswith('</') else 1
    if depth < 0:
        err += 1
        depth = 0
print('标签深度:', depth, '负深度:', err)
print('h2:', len(re.findall(r'<h2>', h)), '| SVG:', h.count('<svg'), '| 大小:', len(h))
