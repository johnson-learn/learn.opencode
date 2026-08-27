# -*- coding: utf-8 -*-
"""BWP/PDCCH 补主线串联 v2：用每讲第二个 h2 精确定位讲次开头"""
import re

d = r'<3GPP文档库目录>'
BRIDGE_CSS = '.bridge { background:#f3f6fa; border:1px dashed #9db8d2; padding:10px 14px; margin:12px 0; font-size:14.5px; }'
LINE_CSS = '.mainline { background:#fff8e6; border:2px solid #c55a11; padding:12px 16px; margin:16px 0; font-size:14.5px; }'

def insert_before_first_h2(h, sec_anchor, block):
    p = h.find(sec_anchor)
    assert p > 0, '第二 h2 锚点缺失: ' + sec_anchor[:40]
    q = h.rfind('<h2', 0, p)
    assert q > 0, '未找到讲次首个 h2'
    return h[:q] + block + '\n' + h[q:]

def patch(fname, mainline, lectures, closing_anchor, closing_text):
    f = d + '\\' + fname
    h = open(f, encoding='utf-8').read()
    h = h.replace('</style>', BRIDGE_CSS + '\n' + LINE_CSS + '\n</style>', 1)
    i = h.index('</h1>')
    h = h[:i+5] + '\n<div class="mainline"><b>本专题主线（一条问题链贯穿全部讲次）</b>：' + mainline + '</div>\n' + h[i+5:]
    for sec_anchor, text in lectures:
        h = insert_before_first_h2(h, sec_anchor, '<div class="bridge"><b>承接</b>：' + text + '</div>')
    k = h.find(closing_anchor)
    assert k > 0, '收口锚点缺失'
    h = h[:k] + '<div class="mainline"><b>主线收口</b>：' + closing_text + '</div>\n' + h[k:]
    open(f, 'w', encoding='utf-8').write(h)
    print(fname, '完成 | 大小:', len(h))

patch('BWP-带宽部分全梳理.html',
      '① BWP 是什么、为什么引入（第 1 讲）→ ② 在频域网格上怎么精确定位（第 2 讲）→ ③ 怎么切换：DCI 动态切换（第 5 讲）→ ④ 计时器 / RRC / 随机接入三种补充切换（第 6 讲）→ ⑤ 切换要多久、业务中断多少（第 7 讲）→ ⑥ 配置链溯源与 10 步全流程回顾（第 9 讲）→ 练习册与计算器。每讲只回答主线一个问题。',
      [
        ('<h2>2. 坐标系：Point A', '第 1 讲回答了主线的第一个问题——BWP 是什么、为什么引入（带宽自适应、省电、适配能力差异 UE）。现在进入主线的第二个问题：这些 BWP 在频域网格上到底怎么精确定位？——这需要先建立 Point A → CRB → PRB 的坐标系（第 2 讲）。'),
        ('<h2>2. bandwidth part indicator', '承上：BWP 怎么"说"清楚位置的问题解决了（第 2 讲，配置链见第 9 讲第 2 节）；但真正让 BWP 跑起来的核心能力是"切换"——主线进入第三步：切换方式。本讲先讲最快、最常用的 DCI 动态切换；计时器/RRC/RA 三种补充方式在第 6 讲。'),
        ('<h2>2. bwp-InactivityTimer 超时', '承上：DCI 切换（第 5 讲）是最快但不是唯一——UE 没数据时靠 bwp-InactivityTimer 自动回退、配置变更靠 RRC、需要上行同步时靠随机接入触发。本讲把三种补充切换方式与并存时的裁决规则一次讲清。'),
        ('<h2>2. 切换时延要求', '承上：四种切换方式（DCI/计时器/RRC/RA）都讲完了（第 5/6 讲），主线下一个问题：一次切换要花多长时间、业务中断多少？——这决定切换策略的取舍（38.133 的时延与中断要求，第 7 讲）。'),
        ('<h2>2. 配置链（一级级溯源', '承上：前面各讲从概念、定位、切换到时延逐题解决；但"这些参数到底挂在哪个 IE 下、怎么一级级配下来"的完整配置链还没系统梳理。第 9 讲补全配置链溯源与 10 步全流程回顾，把整条主线收拢。'),
        ('<h2>第一部分：概念（第 1 讲）', '主线七步走完，进入练习册自测：概念 → 资源网格 → 配置 → DCI 切换 → 计时器/RRC/RA 切换 → 时延 → 综合。'),
      ],
      '<h2>第一部分：概念（第 1 讲）',
      'BWP 全貌一句话：为了带宽自适应、省电与适配不同能力 UE，gNB 在小区带宽内为 UE 划出最多 4 个可切换的带宽部分（BWP）；配置链从 RRCReconfiguration → ServingCellConfig 一路下到 BWP-Downlink 的叶子字段（第 9 讲）；UE 按 DCI/计时器/RRC/RA 四种方式在 BWP 间切换（第 5/6 讲），每次切换时延在 0.125~4 ms 量级并伴随约 1~5 ms 业务中断（第 7 讲）。')

patch('PDCCH-物理下行控制信道全梳理.html',
      '① PDCCH 是什么、一条调度命令怎么送到 UE（第 1 讲）→ ② 资源结构：聚合等级/CORESET/CCE→REG 映射（第 2 讲）→ ③ 内容：DCI 格式与逐字段（第 3 讲）→ ④ UE 怎么找到它：盲检与哈希公式（第 4 讲）→ ⑤ 盲检预算怎么管（第 5 讲）→ ⑥ 配置链四链溯源（第 6 讲）→ ⑦ 编码处理链：CRC/Polar/速率匹配（第 9 讲）→ ⑧ 端到端 10 步全流程回顾（第 7 讲）→ 练习册与计算器。每讲只回答主线一个问题。',
      [
        ('<h2>2. §7.3.2.1：聚合等级', '第 1 讲说清了 PDCCH 的定位与三个资源概念（CORESET / 搜索空间 / 聚合等级）；主线第二个问题：PDCCH 的物理资源结构长什么样？——从聚合等级（1/2/4/8/16 个 CCE）与 CORESET 频域资源讲起（第 2 讲）。'),
        ('<h2>2. 格式总览：为什么', '承上：资源结构（第 2 讲）清楚了，主线第三个问题：PDCCH 里装的内容——DCI 格式与字段。回退格式（0_0/1_0）与非回退格式（0_1/1_1）为什么分两类？每个字段管什么？（第 3 讲）'),
        ('<h2>2. 监测时机判定公式', '承上：DCI 内容（第 3 讲）清楚了，主线第四个问题：UE 不知道 DCI 在哪个 CCE 上——它怎么"找"？——盲检 + 监测时机判定 + CCE 哈希公式（38.213 §10.1，第 4 讲）。'),
        ('<h2>2. CSS 默认聚合等级', '承上：盲检机制（第 4 讲）清楚了，主线第五个问题：盲检次数有预算上限，gNB 怎么配、UE 怎么数？——CSS 默认候选、每 slot 预算、CA 总预算与丢弃规则（第 5 讲）。'),
        ('<h2>2. 配置链（一级级溯源', '承上：机制各讲讲完（第 1~5 讲），主线第六个问题：PDCCH 的全部参数（CORESET/搜索空间/TPC 配置）挂在哪条配置链、由哪个字段配？——四链溯源与相同变量对比（第 6 讲）。'),
        ('<h2>2. 端到端全流程（10 步', '承上：配置链（第 6 讲）与编码链（第 9 讲）都清楚了，主线收拢：把从 DCI 生成到 UE 盲检的 10 步端到端全流程串一遍，并汇总所有注意点（第 7 讲）。'),
        ('<h2>2. §7.3 引言：四个编码步骤', '承上：主线第七个问题：DCI 比特从生成到上天的处理链——CRC 附加、Polar 编码、速率匹配、加扰与调制（38.212 §7.3，第 9 讲；在端到端第 7 讲之前讲，便于第 7 讲引用）。'),
        ('<h2>第一部分：概念与资源（第 1~2 讲）', '主线八步走完，进入练习册自测：概念与资源 → DCI 格式 → 盲检哈希 → 预算与配置 → 全流程 → 编码处理链。'),
      ],
      '<h2>第一部分：概念与资源（第 1~2 讲）',
      'PDCCH 全貌一句话：gNB 把 DCI 调度命令经 CRC/RNTI 加扰、Polar 编码、速率匹配与 QPSK 调制后，映射到 CORESET 内按聚合等级拼成的 CCE 上（第 2/9 讲）；UE 按配置链（MIB 查表 → SIB1 公共 → 专用信令，第 6 讲）获得 CORESET 与搜索空间，用哈希公式定位候选、按预算盲检（第 4/5 讲），解出 DCI 后执行调度（第 7 讲端到端）。')
