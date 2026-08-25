# -*- coding: utf-8 -*-
"""SRS 双视角插入（锚点修正）+ 伪公式修复"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
d = r'<用户桌面目录>\NR-f40'
f = d + r'\SRS-探测参考信号全梳理.html'
h = open(f, encoding='utf-8').read()

sec2v = '''<h2>7. 第 7 讲　基站-UE 双视角落地：SRS 谁配、谁用、怎么用</h2>
<div class="q">设问（承接第 1~6 讲）：SRS 的配置与触发讲完了，现在落到"使用"层——<b>参数由谁配置？基站侧怎么组织测量与使用？UE 侧怎么按配置发送？</b>——本讲给出四问定位、双端流程对照与参数双端使用总表。</div>
<h3>7.1 四问定位</h3>
<table>
<tr><th>四问</th><th>内容</th></tr>
<tr><td><b>含义</b></td><td>SRS 是 UE 发送给 gNB 的上行探测参考信号：低峰均比 ZC 序列 × 梳齿 × 循环移位，按资源集组织（usage 决定用途）</td></tr>
<tr><td><b>作用</b></td><td>上行信道的"探针"：gNB 收到后估计上行信道（各 UE 天线的频响/时延）</td></tr>
<tr><td><b>目的</b></td><td>① 上行调度与预编码（码本/非码本方案的前置测量）；② 上行波束管理（beamManagement）；③ TDD 互易性获取下行 CSI（antennaSwitching）</td></tr>
<tr><td><b>应用场景</b></td><td>码本上行（多端口 SRS→TPMI/TRI）、非码本上行（单端口多资源→SRI 层组合）、波束管理（多资源多波束轮发）、天线切换探测（1T2R/1T4R 等，辅载波获取 DL CSI）</td></tr>
</table>
<h3>7.2 双端流程对照（基站组织测量 ↔ UE 发送）</h3>
<table>
<tr><th>#</th><th>基站侧</th><th>#</th><th>UE 侧</th></tr>
<tr><td>1</td><td><b>配置规划</b>：按用途配资源集（beamManagement 多资源多波束/codebook 多端口/nonCodebook 关联 CSI-RS/antennaSwitching 按 UE 能力）与功控参数（p0/α/路损参考）</td><td>1</td><td><b>接收配置</b>：srs-Config 存资源/资源集/空间关系/功控</td></tr>
<tr><td>2</td><td><b>启动</b>：periodic 靠 RRC；SP 靠 MAC CE（n+3N+1 生效、可覆盖空间关系）；aperiodic 靠 DCI SRS request（slotOffset 定时）</td><td>2</td><td><b>启动执行</b>：按配置/激活/触发发送；SP 按 MAC CE 的空间关系发</td></tr>
<tr><td>3</td><td><b>接收测量</b>：在梳齿/CS 位置提取各 UE 的 SRS → 估上行信道（各天线端口）</td><td>3</td><td><b>发送</b>：序列按 c_init/组跳频生成；CS 按端口错开；功率按 P_SRS 公式；冲突时按优先级</td></tr>
<tr><td>4</td><td><b>测量使用</b>：码本→上行码本选 TPMI/TRI；非码本→SRI 选层；波束→上行波束配对（互易性推下行）；antennaSwitching→下行 CSI</td><td>4</td><td>—（发送完成）</td></tr>
<tr><td>5</td><td><b>调度联动</b>：测量结果在调度窗口内有效；移动 UE 提高 SRS 周期</td><td>5</td><td>—</td></tr>
</table>
<h3>7.3 参数双端使用总表</h3>
<table>
<tr><th>参数</th><th>配置方→给谁</th><th>基站如何使用</th><th>UE 如何使用</th></tr>
<tr><td>transmissionComb（梳齿/偏移/CS）</td><td>RRC → UE</td><td>多 UE 正交复用规划（梳齿×CS 容量分配）</td><td>按梳齿位置与 CS 生成序列</td></tr>
<tr><td>resourceMapping（startPosition/符号数/重复因子）</td><td>RRC → UE</td><td>时隙末尾资源与 PUSCH/PUCCH 错开规划</td><td>在倒数第 startPosition+1 个符号起发</td></tr>
<tr><td>freqHopping（c-SRS/b-SRS/b-hop）</td><td>RRC → UE</td><td>宽带探测策略（窄带逐跳覆盖宽带）</td><td>按跳频公式逐跳发送</td></tr>
<tr><td>spatialRelationInfo（SSB/CSI-RS/SRS 参考）</td><td>RRC → UE（SP 可 MAC CE 覆盖）</td><td>波束对应规划（哪个 SRS 用哪个波束）</td><td>用参考信号的发射滤波器发送</td></tr>
<tr><td>alpha/p0/pathlossReferenceRS</td><td>RRC → UE</td><td>目标接收功率与路损补偿设计</td><td>P_SRS 开环计算</td></tr>
<tr><td>SRS request / slotOffset / 激活 MAC CE</td><td>gNB 动态 → UE</td><td>按需触发（调度窗口前预留 slotOffset）</td><td>按触发发送</td></tr>
<tr><td><b>测量使用决策（TPMI/波束配对/上行调度）</b></td><td><b>gNB 内部实现</b></td><td>SRS 测量 → 上行预编码/调度/波束选择</td><td>不感知</td></tr>
</table>
<h3>7.4 本讲小结（把球交给下一讲）</h3>
<div class="bridge"><b>小结</b>：SRS 参数分 RRC（资源/集/空间关系/功控）、DCI/MAC CE（触发）、gNB 内部（测量使用决策）；基站组织测量 5 步与 UE 发送 5 步对应。<b>引出下一讲</b>：练习册自测。</div>

'''
anchor = '<h2>7. 练习册（25 题含答案）</h2>'
i = h.find(anchor)
assert i > 0, '练习册锚点缺失'
h = h[:i] + sec2v + '\n' + h[i:]
h = h.replace('<h2>7. 练习册（25 题含答案）</h2>', '<h2>8. 练习册（25 题含答案）</h2>')
h = h.replace('<h2>8. 交互式计算器</h2>', '<h2>9. 交互式计算器</h2>')
h = h.replace('<h2>9. 专题总结</h2>', '<h2>10. 专题总结</h2>')
h = h.replace('<li>第 6 讲　端到端回顾与易错点</li>', '<li>第 6 讲　端到端回顾与易错点</li>\n<li>第 7 讲　基站-UE 双视角落地（谁配、谁用、怎么用）</li>')
open(f, 'w', encoding='utf-8').write(h)
print('SRS 深化完成 | h2:')
for m in re.finditer(r'<h2>([\s\S]*?)</h2>', h):
    print(' ', re.sub(r'<[^>]+>', '', m.group(1))[:42])
