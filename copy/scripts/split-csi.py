# -*- coding: utf-8 -*-
"""CSI 拆分 v2：从完整文件切分（含图），插入新第 8 讲，编号顺延"""
import re, os

base = r'<用户临时目录>\opencode'
outdir = r'<用户桌面目录>\NR-f40'
src = os.path.join(outdir, 'CSI-01-信道状态信息全梳理.html')

h = open(src, encoding='utf-8').read()
head = h[h.index('<head>'):h.index('</head>')+7]

# 1) 插入新第 8 讲（csi-r5 的 h2 段）到原第 8 讲前
r5 = open(os.path.join(base, 'csi-r5.html'), encoding='utf-8').read()
new8 = r5[r5.index('<h2>8. 第 8 讲'):]
i = h.index('<h2>8. 第 8 讲　端到端流程串联与易错点总表</h2>')
h = h[:i] + new8 + '\n' + h[i:]

# 2) 编号顺延
h = h.replace('<h2>8. 第 8 讲　端到端流程串联与易错点总表</h2>', '<h2>9. 第 9 讲　端到端流程串联与易错点总表</h2>')
h = h.replace('<h2>9. 练习册（25 题含答案）</h2>', '<h2>10. 练习册（25 题含答案）</h2>')
h = h.replace('<h2>10. 交互式计算器</h2>', '<h2>11. 交互式计算器</h2>')
h = h.replace('<h2>11. 专题总结</h2>', '<h2>12. 专题总结</h2>')
h = h.replace('④ 最后按第 8 讲的端到端流程默写一遍', '④ 最后按第 9 讲的端到端流程默写一遍')

# 3) 按 h2 切分
def cut(start, end=None):
    a = h.index(start)
    b = h.index(end) if end else len(h)
    return h[a:b]

sec1 = cut('<h2>1. 第 1 讲', '<h2>2. 第 2 讲')
sec2 = cut('<h2>2. 第 2 讲', '<h2>3. 第 3 讲')
sec3 = cut('<h2>3. 第 3 讲', '<h2>4. 第 4 讲')
sec4 = cut('<h2>4. 第 4 讲', '<h2>5. 第 5 讲')
sec5 = cut('<h2>5. 第 5 讲', '<h2>6. 第 6 讲')
sec6 = cut('<h2>6. 第 6 讲', '<h2>7. 第 7 讲')
sec7 = cut('<h2>7. 第 7 讲', '<h2>8. 第 8 讲')
sec8 = cut('<h2>8. 第 8 讲', '<h2>9. 第 9 讲')
sec9 = cut('<h2>9. 第 9 讲', '<h2>10. 练习册')
sec10 = cut('<h2>10. 练习册', None)

nav = '''<div style="background:#eef4fa;border:1px solid #b8cce4;padding:8px 14px;margin:14px 0;font-size:14px;">
<b>CSI 专题导航</b>：<a href="CSI-00-学习地图与规范索引.html">学习地图</a> ｜
<a href="CSI-01-框架与CSI-RS物理层.html">01 框架与 CSI-RS 物理层</a> ｜
<a href="CSI-02-RRC配置与上报量.html">02 RRC 配置与上报量</a> ｜
<a href="CSI-03-CQI码本与上报类型.html">03 CQI/码本与上报类型</a> ｜
<a href="CSI-04-参考资源与计算时延.html">04 参考资源与计算时延</a> ｜
<a href="CSI-05-38.213流程与UCI编码.html">05 38.213 流程与 UCI 编码</a> ｜
<a href="CSI-06-端到端流程与易错点.html">06 端到端与易错点</a> ｜
<a href="CSI-07-练习册与计算器.html">07 练习册与计算器</a>
</div>'''

files = [
    ('CSI-01-框架与CSI-RS物理层.html', 'CSI 专题 01：框架与 CSI-RS 物理层', sec1 + sec2),
    ('CSI-02-RRC配置与上报量.html', 'CSI 专题 02：RRC 配置与上报量', sec3 + sec4),
    ('CSI-03-CQI码本与上报类型.html', 'CSI 专题 03：CQI/码本与三种上报类型', sec5 + sec6),
    ('CSI-04-参考资源与计算时延.html', 'CSI 专题 04：参考资源与计算时延 Z/Z′', sec7),
    ('CSI-05-38.213流程与UCI编码.html', 'CSI 专题 05：38.213 流程与 UCI 编码（38.212/38.215/38.321）', sec8),
    ('CSI-06-端到端流程与易错点.html', 'CSI 专题 06：端到端流程与易错点', sec9),
    ('CSI-07-练习册与计算器.html', 'CSI 专题 07：练习册与计算器', sec10),
]

for fname, title, body in files:
    doc = ('<!DOCTYPE html>\n<html lang="zh-CN">\n' + head
           + f'\n<body>\n<h1>{title}</h1>\n' + nav + body
           + '\n<p class="src">本系列依据：TS 38.211/38.212/38.213/38.214/38.215/38.321/38.331 V15.4.0（本机文档库，Rel-15 2018-12 版）。本文为教学讲义，协议最终解释以 3GPP 官网正式文档为准。</p>\n</body>\n</html>\n')
    open(os.path.join(outdir, fname), 'w', encoding='utf-8').write(doc)
    print(fname, len(doc))

# 4) 删除旧单文件
os.remove(src)
print('旧文件已删除:', src)
