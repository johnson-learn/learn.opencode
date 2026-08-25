# -*- coding: utf-8 -*-
import re

f = r'<3GPP文档库目录>\系统消息-01-SSB-MIB-SIB1与OSI.html'
html = open(f, encoding='utf-8').read()

# 1) 清空所有 figure（当前 6 个）
html, n_del = re.subn(r'<figure[\s\S]*?</figure>', '', html)
print('清除 figure:', n_del)

# 2) 恢复 1.3~2.8 节正文（插到 <h3>2.9 本讲小结 之前）
restore = open(r'<用户临时目录>\opencode\si-restore.html', encoding='utf-8').read()
i = html.find('<h3>2.9 本讲小结')
assert i > 0, '2.9 锚点缺失'
html = html[:i] + restore + '\n' + html[i:]
print('恢复 1.3~2.8 正文')

# 3) 重插 9 张图
anchors = [
    ('fig1', '<h3>1.3 SI 的"两层结构', 'before'),
    ('fig2', '<h3>2.2 原文表', 'before'),
    ('fig3', '<h3>2.9 本讲小结</h3>', 'before'),
    ('fig4', '<div class="example"><b>例题 2.5</b>', 'before'),
    ('fig5', '<h3>3.4 PBCH 后续处理链（加扰 → CRC → Polar → 速率匹配 → 调制）</h3>', 'after'),
    ('fig6', '<div class="example"><b>例题 6.1</b>', 'before'),
    ('fig7', '<div class="orig"><b>38.331 V15.4.0 §6.5 Short Message', 'before'),
    ('fig8', '<h3>6.4 按需 SI（on-demand SI）的两种请求方式（38.331 §5.2.2.3.3 + 38.321）</h3>', 'after'),
    ('fig9', '<h2>7. 第 7 讲', 'after'),
]
for key, anchor, pos in anchors:
    seg = open(rf'<用户临时目录>\opencode\si-figs\{key}.html', encoding='utf-8').read()
    i = html.find(anchor)
    if i < 0:
        print('锚点缺失:', key, '->', anchor[:50])
        continue
    if pos == 'after':
        i += len(anchor)
    html = html[:i] + seg + '\n' + html[i:]
    print('已插入', key)

open(f, 'w', encoding='utf-8').write(html)
print('SVG 总数:', html.count('<svg'), '| figure 总数:', html.count('<figure'))
