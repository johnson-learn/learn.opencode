# -*- coding: utf-8 -*-
"""PUSCH 深化：① 第1讲补含义/作用/目的/场景 ② 新增双视角讲次 ③ 编号顺延"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
d = r'<3GPP文档库目录>'
f = d + r'\PUSCH-物理上行共享信道全梳理.html'
h = open(f, encoding='utf-8').read()

# ① 第 1 讲补四问定位
sec12 = '''<h3>1.2 含义、作用、目的与应用场景（四问定位）</h3>
<table>
<tr><th>四问</th><th>内容</th></tr>
<tr><td><b>含义</b>（是什么）</td><td>PUSCH 是承载上行共享信道（UL-SCH）传输块的物理信道——UE 向 gNB 发业务数据与上行控制（UCI 复用）的共享物理资源，由 UL grant（DCI 0_0/0_1）动态调度或配置授权周期触发</td></tr>
<tr><td><b>作用</b>（承载什么）</td><td>① 上行业务数据（TB）；② UCI 复用：HARQ-ACK / CSI Part1 / CSI Part2 与数据同传；③ Msg3（RRC 连接请求/重配完成）与 MsgA（2 步 RACH 的载荷）；④ 配置授权业务（Type1/Type2）</td></tr>
<tr><td><b>目的</b>（为什么存在）</td><td>① <b>上行链路自适应</b>：gNB 测 SRS 得上行信道 → 选 MCS/预编码/层数，把上行谱效压满；② <b>上行功率效率</b>：开环+闭环功率控制，UE 以"够用"功率发送（省电、控干扰）；③ <b>波形适配</b>：CP-OFDM（谱效）与 DFT-s-OFDM（峰均比/覆盖）按 UE 功率余量切换；④ <b>可靠传输</b>：HARQ 重传 + 跳频分集</td></tr>
<tr><td><b>应用场景</b></td><td>eMBB 上行大吞吐（CP-OFDM/256QAM/码本 MIMO）、小区边缘覆盖（DFT-s-OFDM/π2-BPSK/跳频/聚合因子）、URLLC 上行（配置授权免调度时延/CBG 重传）、VoIP 小包（配置授权周期资源）、Msg3 初始接入（保守 QPSK）</td></tr>
</table>
<div class="jiexi"><b>场景决定波形与调度</b>：小区中心（功率余量大）→ CP-OFDM + 高 MCS + 码本预编码；小区边缘 → DFT-s-OFDM + 跳频 + 聚合因子重复。Msg3 走公共配置（msg3-transformPrecoder/公共时域表/公共功率参数），业务走专用配置——第 7 讲展开双端使用。</div>

'''
anchor12 = '<h3>1.2 两种传输方案（38.214 §6.1.1 原文）</h3>'
i = h.find(anchor12)
assert i > 0
h = h[:i] + sec12 + h[i:]
h = h.replace('<h3>1.2 两种传输方案', '<h3>1.3 两种传输方案')
h = h.replace('<h3>1.3 本讲小结（把球交给下一讲）</h3>', '<h3>1.4 本讲小结（把球交给下一讲）</h3>')

# ② 新增第 7 讲双视角
sec7 = '''<h2>7. 第 7 讲　基站-UE 双视角落地：参数谁配、谁用、怎么用</h2>

<div class="q">设问（承接第 1~6 讲）：前六讲把 PUSCH 机制讲完了，现在落到"使用"层——<b>每个参数配置给谁？gNB 侧怎么用它们调度与解调？UE 侧怎么用它们发送？</b>——本讲把参数按"配置方 / 使用者 / gNB 如何使用 / UE 如何使用"落表，并给出 gNB 调度解调链与 UE 发送链的逐步对照。</div>

<h3>7.1 双端流程对照（gNB 调度解调 8 步 ↔ UE 发送 8 步）</h3>
<table>
<tr><th>#</th><th>gNB 侧（如何使用参数调度与解调）</th><th>#</th><th>UE 侧（如何解析参数发送）</th></tr>
<tr><td>1</td><td><b>调度决策</b>：收 BSR/SR 知 UE 有数据；按 QoS 权重与各 UE 功率余量（PHR 上报）选本次调度的 UE</td><td>1</td><td><b>请求资源</b>：有数据→发 SR/BSR；收到 UL grant（DCI 0_0/0_1）或按配置授权周期</td></tr>
<tr><td>2</td><td><b>参数选择</b>：测 SRS 得上行信道 → MCS、层数、预编码（码本：TPMI/TRI 查上行码本；非码本：SRI 选层组合）；时频资源与跳频</td><td>2</td><td><b>解析 grant</b>：K2/SLIV 定时域；type 0/1 定频域；跳频则两跳分频；SRI/TPMI/TRI 定预编码</td></tr>
<tr><td>3</td><td><b>组 DCI</b>：MCS/RV/NDI/资源/预编码字段/β_offset indicator（动态 UCI）填 DCI 0_0/0_1</td><td>3</td><td><b>计算 TBS</b>：同一四步公式（含 UCI 扣 RE）；按 MCS 表得 Qm/R</td></tr>
<tr><td>4</td><td>—（等待接收）</td><td>4</td><td><b>编码链</b>：UL-SCH LDPC 链 + UCI 复用（按 β_offset 折算 RE 插 HARQ-ACK/CSI）→ 加扰（dataScramblingIdentityPUSCH）→ 调制 →（可选）变换预编码 → 层映射（≤4 层）→ 预编码 → RE 映射</td></tr>
<tr><td>5</td><td>—（等待接收）</td><td>5</td><td><b>功率计算</b>：P_PUSCH = min{P_CMAX, P_O+带宽项+α·PL+Δ_TF+f}（pusch-PowerControl 的开环参数 + DCI 的 TPC 闭环）</td></tr>
<tr><td>6</td><td><b>接收解调</b>：按配置的 DM-RS 类型/位置估信道（CP-OFDM 用 Gold、DFT-s-OFDM 用低峰均比 ZC）→ 解调 →（可选）IDFT → 解层映射 → 解扰</td><td>6</td><td><b>发送</b>：按 TA 提前发送；DM-RS 随数据同发（前载+附加位置按映射类型）</td></tr>
<tr><td>7</td><td><b>解码</b>：解速率匹配（RV）→ LDPC 译码 → CRC；分离 UCI 与数据（按 Part 顺序与 β_offset 位置）</td><td>7</td><td>—（发送完成）</td></tr>
<tr><td>8</td><td><b>反馈/重传</b>：CRC 失败→NDI 翻转的重传 grant（RV 轮换）；CBG 场景按组反馈</td><td>8</td><td><b>等重传</b>：NDI 翻转→重传（软合并）；SPS/配置授权场景按周期自发</td></tr>
</table>

<h3>7.2 参数双端使用总表（谁配 / 给谁 / gNB 如何使用 / UE 如何使用）</h3>
<table>
<tr><th>参数</th><th>配置方→配置给谁</th><th>gNB 如何使用</th><th>UE 如何使用</th></tr>
<tr><td>txConfig / codebookSubset / maxRank</td><td>RRC（gNB）→ UE</td><td>按方案（码本/非码本）测 SRS 后选 TPMI/TRI 或 SRI；码本子集限制可选范围</td><td>按 DCI 的 TPMI/TRI 查上行码本应用预编码；或按 SRI 选资源组合</td></tr>
<tr><td>transformPrecoder / tp-pi2BPSK</td><td>RRC → UE</td><td>按 UE 功率余量/场景选择波形（近点 CP-OFDM、边缘 DFT-s-OFDM）</td><td>enabled → 调制后做 DFT 扩频；π2-BPSK 用旋转 BPSK</td></tr>
<tr><td>mcs-Table / mcs-TableTransformPrecoder</td><td>RRC → UE</td><td>按所选波形用对应表编 I_MCS</td><td>按表翻 I_MCS 得 Qm/R</td></tr>
<tr><td>frequencyHopping / frequencyHoppingOffsetLists</td><td>RRC → UE</td><td>边缘 UE 配跳频求分集；偏移错开小区内 UE</td><td>两跳按偏移映射资源</td></tr>
<tr><td>pusch-TimeDomainAllocationList</td><td>RRC → UE（公共列表在 PUSCH-ConfigCommon）</td><td>DCI 时域字段指行</td><td>查表得 K2/S/L</td></tr>
<tr><td>pusch-PowerControl（p0-AlphaSets/pathlossReferenceRS）</td><td>RRC → UE</td><td>p0/α 按小区负载与目标 SINR 设置（开环部分）</td><td>P_PUSCH 公式的开环输入</td></tr>
<tr><td>TPC 命令（DCI 0_0/0_1/2_2）</td><td>gNB 动态 → UE</td><td>按收到的功率测量修正 UE 功率（闭环）</td><td>累积/绝对值更新 f 闭环</td></tr>
<tr><td>uci-OnPUSCH（betaOffsets/scaling）</td><td>RRC → UE</td><td>按 UCI 可靠性需求设 β_offset（HARQ-ACK 给高）</td><td>按 β_offset 折算各类 UCI 的 RE 数</td></tr>
<tr><td>dmrs-UplinkForPUSCH-MappingTypeA/B</td><td>RRC → UE</td><td>按配置生成 DM-RS 供自己解调</td><td>按配置在正确 RE 发 DM-RS</td></tr>
<tr><td>groupHoppingEnabledTransformPrecoding（公共）</td><td>RRC → UE（小区级）</td><td>小区间 DM-RS 干扰随机化</td><td>组跳频的序列生成</td></tr>
<tr><td>msg3-DeltaPreamble / p0-NominalWithGrant（公共）</td><td>RRC → UE（小区级）</td><td>Msg3 功率从 preamble 功率补偿起步</td><td>Msg3 功率计算用公共参数</td></tr>
<tr><td>dataScramblingIdentityPUSCH / sequenceId 类</td><td>RRC → UE</td><td>解扰/解 DM-RS 用同一 ID</td><td>加扰/DM-RS 生成用同一 ID</td></tr>
<tr><td>pusch-AggregationFactor</td><td>RRC → UE</td><td>覆盖不足时配重复发送</td><td>跨时隙重复发（RV 轮换）</td></tr>
<tr><td>configuredGrantConfig（Type1/2）</td><td>RRC → UE（Type2 加 CS-RNTI DCI 激活）</td><td>周期资源免调度（低时延/小包）</td><td>按周期自发；Type2 等激活 DCI</td></tr>
<tr><td><b>调度器决策（MCS 精确值、预编码、跳频开关、功率目标）</b></td><td><b>gNB 内部实现（规范不规定）</b></td><td>基于 SRS 测量 + PHR + QoS 权重综合决策</td><td>不感知——按 grant 执行</td></tr>
<tr><td><b>QoS（5QI/GBR）</b></td><td><b>核心网 → gNB</b></td><td>上行调度优先级权重</td><td>不感知——但时延/速率体验由此决定</td></tr>
</table>

<h3>7.3 gNB 内部如何使用（规范外实现原理，标注【解读/推导】）</h3>
<div class="jiexi"><b>① 上行调度器</b>：周期收集 SR/BSR（UE 请求）、PHR（功率余量）、SRS 测量（信道质量），按 QoS 权重与功率余量选 UE/资源/MCS——PUSCH 的"共享"由它实现。<br><b>② 预编码决策</b>：码本方案——测 SRS 后从上行码本选 TPMI/TRI（如非相干 UE 只能选对角型预编码）；非码本方案——UE 自算，gNB 只选 SRI 层组合。<br><b>③ 功率目标</b>：p0/α 按目标接收 SINR 与小区的 IoT（热噪抬升）管理设置；TPC 闭环按测量误差修正。<br><b>④ 波形选择</b>：UE 功率余量大（PHR 高）→ CP-OFDM 高谱效；余量小→ DFT-s-OFDM 省功率。<br><b>⑤ 定时</b>：TA 命令管理上行同步；调度时预留 TA 提前量。</div>

<h3>7.4 应用场景矩阵（各场景的参数差异）</h3>
<table>
<tr><th>场景</th><th>调度方式</th><th>波形/调制</th><th>预编码</th><th>其他特征</th></tr>
<tr><td>Msg3（初始接入）</td><td>RAR UL grant</td><td>msg3-transformPrecoder 决定；QPSK 保守</td><td>单端口</td><td>公共功率参数；跳频按 RAR 标志</td></tr>
<tr><td>eMBB 上行（近点）</td><td>动态 grant</td><td>CP-OFDM、至 256QAM</td><td>码本 TPMI/TRI 或非码本 SRI</td><td>高 MCS、多层</td></tr>
<tr><td>边缘覆盖</td><td>动态 grant</td><td>DFT-s-OFDM、π2-BPSK 可选</td><td>单端口/低秩</td><td>跳频 + 聚合因子 + 高功率</td></tr>
<tr><td>URLLC 上行</td><td>配置授权 Type1/2</td><td>CP-OFDM</td><td>码本</td><td>免调度时延；CBG 重传</td></tr>
<tr><td>VoIP 小包</td><td>配置授权</td><td>DFT-s-OFDM 常见</td><td>单端口</td><td>周期小资源；UCI 复用限制</td></tr>
</table>

<h3>7.5 本讲小结（把球交给下一讲）</h3>
<div class="bridge"><b>小结</b>：PUSCH 参数分四类来源——RRC 给 UE 的配置、DCI/grant 的即时指示、gNB 内部决策（调度/预编码/功率/波形）、核心网 QoS 输入；gNB 调度解调 8 步与 UE 发送 8 步逐环对应。<b>引出下一讲</b>：第 8 讲把 1~7 讲串成端到端回顾并汇总易错点。</div>

'''
anchor7 = '<h2>7. 第 7 讲　端到端回顾与易错点</h2>'
i = h.find(anchor7)
assert i > 0
h = h[:i] + sec7 + h[i:]

# ③ 编号顺延 + 目录
h = h.replace('<h2>7. 第 7 讲　端到端回顾与易错点</h2>', '<h2>8. 第 8 讲　端到端回顾与易错点</h2>')
h = h.replace('<h3>7.1 PUSCH 发送全流程', '<h3>8.1 PUSCH 发送全流程')
h = h.replace('<h3>7.2 易错点/澄清总表</h3>', '<h3>8.2 易错点/澄清总表</h3>')
h = h.replace('<h3>7.3 主线收口</h3>', '<h3>8.3 主线收口</h3>')
h = h.replace('把 1~6 讲串成一条线', '把 1~7 讲串成一条线')
h = h.replace('<h2>8. 练习册（25 题含答案）</h2>', '<h2>9. 练习册（25 题含答案）</h2>')
h = h.replace('<h3>8.1 选择题（1~10）</h3>', '<h3>9.1 选择题（1~10）</h3>')
h = h.replace('<h3>8.2 填空题（11~16）</h3>', '<h3>9.2 填空题（11~16）</h3>')
h = h.replace('<h3>8.3 判断题（17~20）</h3>', '<h3>9.3 判断题（17~20）</h3>')
h = h.replace('<h3>8.4 计算题（21~25）</h3>', '<h3>9.4 计算题（21~25）</h3>')
h = h.replace('<h2>9. 交互式计算器</h2>', '<h2>10. 交互式计算器</h2>')
h = h.replace('<h2>10. 专题总结</h2>', '<h2>11. 专题总结</h2>')
h = h.replace('③ 按第 7 讲八步流程默写一次', '③ 按第 7/8 讲的双端流程默写一次')
h = h.replace('<li>第 7 讲　端到端回顾与易错点</li>', '<li>第 7 讲　基站-UE 双视角落地（参数谁配、谁用、怎么用）</li>\n<li>第 8 讲　端到端回顾与易错点</li>')

open(f, 'w', encoding='utf-8').write(h)
print('PUSCH 深化完成 | 大小:', len(h))
print('h2:', len(re.findall(r'<h2>', h)), '| 双端表:', h.count('gNB 如何使用'), '| 场景矩阵:', h.count('应用场景矩阵'))
