# -*- coding: utf-8 -*-
"""CSI/SRS 两专题：补四问定位 + 双视角落地讲次（编号顺延）"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
d = r'C:\Users\job_p\Desktop\NR-f40'

# ================= CSI =================
f = d + r'\CSI-信道状态信息全梳理.html'
h = open(f, encoding='utf-8').read()

sec2v = '''<h2>7. 第 7 讲　基站-UE 双视角落地：CSI 谁配、谁用、怎么用</h2>
<div class="q">设问（承接第 1~6 讲）：CSI 的配置与上报讲完了，现在落到"使用"层——<b>CSI 参数由谁配置？基站侧怎么组织测量与使用反馈？UE 侧怎么测量、计算、上报？</b>——本讲给出四问定位、双端流程对照与参数双端使用总表。</div>
<h3>7.1 四问定位</h3>
<table>
<tr><th>四问</th><th>内容</th></tr>
<tr><td><b>含义</b></td><td>CSI 是 UE 对下行信道状态的量化反馈：CQI（质量）、PMI（预编码）、RI（秩）、LI（最强层）、CRI/SSBRI（资源/波束）、L1-RSRP（波束强度），由 gNB 控制上报的时频资源</td></tr>
<tr><td><b>作用</b></td><td>gNB 调度 PDSCH 的依据：MCS（CQI）、层数（RI）、预编码（PMI）、波束（CRI/L1-RSRP）</td></tr>
<tr><td><b>目的</b></td><td>下行链路自适应——把下行谱效压到信道能承受的极限；波束管理——跟踪最佳波束对</td></tr>
<tr><td><b>应用场景</b></td><td>eMBB 调度（cri-RI-PMI-CQI）、波束管理（cri-RSRP/ssb-Index-RSRP）、互易性上行（non-PMI 的 cri-RI-CQI）、半开环（cri-RI-i1-CQI）、URLLC（table3 低谱效）</td></tr>
</table>
<h3>7.2 双端流程对照（基站测量组织 ↔ UE 测量上报）</h3>
<table>
<tr><th>#</th><th>基站侧</th><th>#</th><th>UE 侧</th></tr>
<tr><td>1</td><td><b>配置规划</b>：按小区天线数/业务决定 CSI-RS 资源（端口/密度/周期）与上报配置（reportQuantity/周期/粒度）；波束管理类配多资源集</td><td>1</td><td><b>接收配置</b>：csi-MeasConfig 存资源池/上报池/触发状态</td></tr>
<tr><td>2</td><td><b>CSI-RS 发射</b>：periodic 按周期发；aperiodic 由触发状态内的 TCI 定波束、按 triggeringOffset 发</td><td>2</td><td><b>测量</b>：NZP CSI-RS 估信道、CSI-IM 测干扰（timeRestriction 决定用哪次时机）</td></tr>
<tr><td>3</td><td><b>触发</b>：需要反馈时 DCI 的 CSI request 触发（或 MAC CE 激活 SP）</td><td>3</td><td><b>计算</b>：依赖链 CRI→RI→PMI→CQI→LI；CQI 按表 + 参考资源假设；CPU 记账</td></tr>
<tr><td>4</td><td>—（等反馈）</td><td>4</td><td><b>上报</b>：Part1（RI/CRI/CQI1）→ Part2（PMI/CQI2）；PUCCH 或 PUSCH；时延满足 Z/Z′</td></tr>
<tr><td>5</td><td><b>反馈使用</b>：CQI 起点 + 外环修正 → MCS；RI/PMI → 层数与预编码；CRI/L1-RSRP → 波束（TCI 选择与波束失败恢复候选）</td><td>5</td><td>—（上报完成）</td></tr>
</table>
<h3>7.3 参数双端使用总表</h3>
<table>
<tr><th>参数</th><th>配置方→给谁</th><th>基站如何使用</th><th>UE 如何使用</th></tr>
<tr><td>NZP CSI-RS（resourceMapping/powerControlOffset/periodicity）</td><td>RRC → UE</td><td>按配置生成发射（功率偏移保证 EPRE 比例）</td><td>在指定 RE 上估计信道 H</td></tr>
<tr><td>CSI-IM 图案</td><td>RRC → UE</td><td>这些 RE 上不发任何能量（留给 UE 测干扰）</td><td>测干扰+噪声</td></tr>
<tr><td>CSI-ReportConfig（reportQuantity/类型/粒度/码本/CQI 表）</td><td>RRC → UE</td><td>按需求选上报内容与节奏（波束管理用 RSRP 类）</td><td>按配置计算并上报</td></tr>
<tr><td>触发状态（TCI 列表/资源集选择/偏移）</td><td>RRC → UE + DCI 码点</td><td>一次触发把"测哪、用哪个波束、报什么"打包</td><td>按码点取全套配置执行</td></tr>
<tr><td>powerControlOffset / 参考资源假设</td><td>RRC → UE</td><td>保证 CQI 口径与调度假设一致</td><td>CQI 计算按假设折算</td></tr>
<tr><td><b>反馈使用决策（MCS 外环/预编码/波束选择）</b></td><td><b>gNB 内部实现</b></td><td>CQI 起点+外环；PMI/RI 直接或互易性修正；RSRP 选波束</td><td>不感知——只负责如实反馈</td></tr>
<tr><td><b>QoS（5QI/GBR）</b></td><td><b>核心网 → gNB</b></td><td>调度权重 → CSI 上报的优先级/频率倾斜</td><td>不感知</td></tr>
</table>
<h3>7.4 本讲小结（把球交给下一讲）</h3>
<div class="bridge"><b>小结</b>：CSI 参数分 RRC（资源/上报配置）、DCI/MAC CE（触发）、gNB 内部（反馈使用决策）、核心网（QoS 权重）；基站测量组织 5 步与 UE 测量上报 5 步对应。<b>引出下一讲</b>：第 8 讲把 1~7 讲串成 aperiodic CSI 的九步全程并汇总易错点。</div>

'''
anchor = '<h2>8. 第 8 讲　主线回顾：一次 aperiodic CSI 的九步全程 + 易错点</h2>'
i = h.find(anchor)
assert i > 0
h = h[:i] + sec2v + h[i:]
h = h.replace('<h2>8. 第 8 讲　主线回顾', '<h2>8. 第 8 讲　主线回顾')  # 保持
h = h.replace('<li>第 7 讲　交付时限：CPU 占用与计算时延 Z/Z′（38.214 §5.2.1.6/§5.4）</li>',
              '<li>第 7 讲　交付时限：CPU 占用与计算时延 Z/Z′（38.214 §5.2.1.6/§5.4）</li>\n<li>第 7+ 讲　基站-UE 双视角落地（谁配、谁用、怎么用）</li>')
open(f, 'w', encoding='utf-8').write(h)
print('CSI 深化完成 | 大小:', len(h))

# ================= SRS =================
f = d + r'\SRS-探测参考信号全梳理.html'
h = open(f, encoding='utf-8').read()

sec2v = '''<h2>6.5 第 6+ 讲　基站-UE 双视角落地：SRS 谁配、谁用、怎么用</h2>
<div class="q">设问（承接第 1~6 讲）：SRS 的配置与触发讲完了，现在落到"使用"层——<b>参数由谁配置？基站侧怎么组织测量与使用？UE 侧怎么按配置发送？</b>——本讲给出四问定位、双端流程对照与参数双端使用总表。</div>
<h3>6.5.1 四问定位</h3>
<table>
<tr><th>四问</th><th>内容</th></tr>
<tr><td><b>含义</b></td><td>SRS 是 UE 发送给 gNB 的上行探测参考信号：低峰均比 ZC 序列 × 梳齿 × 循环移位，按资源集组织（usage 决定用途）</td></tr>
<tr><td><b>作用</b></td><td>上行信道的"探针"：gNB 收到后估计上行信道（各 UE 天线的频响/时延）</td></tr>
<tr><td><b>目的</b></td><td>① 上行调度与预编码（码本/非码本方案的前置测量）；② 上行波束管理（beamManagement）；③ TDD 互易性获取下行 CSI（antennaSwitching）</td></tr>
<tr><td><b>应用场景</b></td><td>码本上行（多端口 SRS→TPMI/TRI）、非码本上行（单端口多资源→SRI 层组合）、波束管理（多资源多波束轮发）、天线切换探测（1T2R/1T4R 等，辅载波获取 DL CSI）</td></tr>
</table>
<h3>6.5.2 双端流程对照（基站组织测量 ↔ UE 发送）</h3>
<table>
<tr><th>#</th><th>基站侧</th><th>#</th><th>UE 侧</th></tr>
<tr><td>1</td><td><b>配置规划</b>：按用途配资源集（beamManagement 多资源多波束/codebook 多端口/nonCodebook 关联 CSI-RS/antennaSwitching 按 UE 能力）与功控参数（p0/α/路损参考）</td><td>1</td><td><b>接收配置</b>：srs-Config 存资源/资源集/空间关系/功控</td></tr>
<tr><td>2</td><td><b>启动</b>：periodic 靠 RRC；SP 靠 MAC CE（n+3N+1 生效、可覆盖空间关系）；aperiodic 靠 DCI SRS request（slotOffset 定时）</td><td>2</td><td><b>启动执行</b>：按配置/激活/触发发送；SP 按 MAC CE 的空间关系发</td></tr>
<tr><td>3</td><td><b>接收测量</b>：在梳齿/CS 位置提取各 UE 的 SRS → 估上行信道（各天线端口）</td><td>3</td><td><b>发送</b>：序列按 c_init/组跳频生成；CS 按端口错开；功率按 P_SRS 公式；冲突时按优先级</td></tr>
<tr><td>4</td><td><b>测量使用</b>：码本→上行码本选 TPMI/TRI；非码本→SRI 选层；波束→上行波束配对（互易性推下行）；antennaSwitching→下行 CSI</td><td>4</td><td>—（发送完成）</td></tr>
<tr><td>5</td><td><b>调度联动</b>：测量结果在调度窗口内有效；移动 UE 提高 SRS 周期</td><td>5</td><td>—</td></tr>
</table>
<h3>6.5.3 参数双端使用总表</h3>
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
'''
anchor = '<h2>7. 第 7 讲　端到端回顾与易错点</h2>'
i = h.find(anchor)
assert i > 0
h = h[:i] + sec2v + h[i:]
open(f, 'w', encoding='utf-8').write(h)
print('SRS 深化完成 | 大小:', len(h))
