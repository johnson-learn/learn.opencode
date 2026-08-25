# -*- coding: utf-8 -*-
"""PDSCH 深化：① 第1讲补含义/作用/目的/场景 ② 新增双视角讲次 ③ 编号顺延"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
d = r'C:\Users\job_p\Desktop\NR-f40'
f = d + r'\PDSCH-物理下行共享信道全梳理.html'
h = open(f, encoding='utf-8').read()

# ============ ① 第 1 讲补"含义/作用/目的/应用场景" ============
sec12 = '''<h3>1.2 含义、作用、目的与应用场景（四问定位）</h3>
<table>
<tr><th>四问</th><th>内容</th></tr>
<tr><td><b>含义</b>（是什么）</td><td>PDSCH 是承载下行共享信道（DL-SCH）传输块的物理信道——多 UE 分时/分频共享的一套物理资源，由 PDCCH 的 DCI 逐次动态指示"谁在何时何地用"</td></tr>
<tr><td><b>作用</b>（承载什么）</td><td>① 业务数据（C-RNTI/CS-RNTI 调度的 TB）；② 系统消息（SIB1/OSI，SI-RNTI）；③ 寻呼消息（P-RNTI）；④ 随机接入响应 RAR（RA-RNTI）与 Msg4（TC-RNTI）；⑤ 与 UCI 无关的下行控制类数据（SPS 释放确认等）</td></tr>
<tr><td><b>目的</b>（为什么存在）</td><td>① <b>链路自适应</b>：按每个 UE 的瞬时信道（CSI 反馈）选 MCS/层数/预编码，把频谱效率压到信道能承受的极限；② <b>多用户复用</b>：时频资源动态共享，多个 UE 错峰/错频使用；③ <b>HARQ 增益</b>：异步增量冗余重传，用时间换可靠性；④ <b>空分复用</b>：最多 8 层 MIMO，把空间维也用起来</td></tr>
<tr><td><b>应用场景</b></td><td>eMBB 大吞吐（256QAM/8 层/双码字）、URLLC 低时延（低谱效 MCS 表/CBG 重传/短时域分配）、mMTC 小包（Type B 短分配）、广播与接入（SIB1/寻呼/RAR 的固定 QPSK 保守调度）</td></tr>
</table>
<div class="jiexi"><b>场景决定参数</b>（各 RNTI 场景的调度差异，先给全景，第 7 讲展开）：SI-RNTI/P-RNTI/RA-RNTI 用公共资源（Default A/B/C 时域表、type 1、QPSK、与 SSB QCL）；C-RNTI 业务用专用配置（TCI 波束、256QAM、动态 PRB bundling）。同一套物理层处理链服务全部场景——这就是"共享信道"的含义。</div>

'''
anchor12 = '<h3>1.2 传输方案与 HARQ 进程（38.214 §5.1.1 + §5.1 原文）</h3>'
i = h.find(anchor12)
assert i > 0
h = h[:i] + sec12 + h[i:]
h = h.replace('<h3>1.2 传输方案与 HARQ 进程', '<h3>1.3 传输方案与 HARQ 进程')
h = h.replace('<h3>1.3 本讲小结（把球交给下一讲）</h3>', '<h3>1.4 本讲小结（把球交给下一讲）</h3>')

# ============ ② 新增第 7 讲：基站-UE 双视角落地 ============
sec7 = '''<h2>7. 第 7 讲　基站-UE 双视角落地：参数谁配、谁用、怎么用</h2>

<div class="q">设问（承接第 1~6 讲）：前六讲把 PDSCH 的机制讲完了，但还差"落地"这一层——<b>每个参数到底是配置给谁的？基站侧怎么用它们发送？UE 侧怎么用它们接收？</b>——本讲把全部参数按"配置方 / 使用者 / 基站如何使用 / UE 如何使用"四个维度落表，并给出基站发送链与 UE 接收链的逐步对照。</div>

<h3>7.1 双端流程对照（基站发送 8 步 ↔ UE 接收 8 步）</h3>
<table>
<tr><th>#</th><th>基站侧（gNB 如何使用参数发送）</th><th>#</th><th>UE 侧（UE 如何解析参数接收）</th></tr>
<tr><td>1</td><td><b>调度决策</b>：MAC 调度器按各 UE 的缓冲状态、CSI（CQI/RI/PMI 反馈）、QoS 权重选出本次传输的 UE 与 HARQ 进程</td><td>1</td><td><b>盲检 DCI</b>：在搜索空间按哈希公式盲检 DCI 1_0/1_1（CRC 用 C-RNTI 等解扰）</td></tr>
<tr><td>2</td><td><b>参数选择</b>：MCS（外环 CQI 修正）→ Qm/R；层数/预编码（CSI 的 RI/PMI 或互易性）；时频资源（RA type、PRG）；TCI 波束（L1-RSRP 反馈）</td><td>2</td><td><b>解析 DCI</b>：读时域分配字段→查 pdsch-TimeDomainAllocationList 得 K0/S/L；读频域字段→按 resourceAllocation 解 type 0 位图或 type 1 RIV</td></tr>
<tr><td>3</td><td><b>计算 TBS</b>：按 N'_RE/N_RE/N_info 四步（xOverhead 参与）；组 DCI（MCS/RV/NDI/资源/TCI 字段）</td><td>3</td><td><b>计算 TBS</b>：同一四步公式（N'_RE 用 DCI 指示的 DM-RS CDM 组数 + xOverhead）</td></tr>
<tr><td>4</td><td><b>编码链</b>：TB CRC → BG 选 → 分段 → LDPC → RV 速率匹配 → 级联 → 加扰（dataScramblingIdentityPDSCH 参与 c_init）→ 调制 → 层映射</td><td>4</td><td><b>解码链</b>：解调（按 MCS）→ 解扰 → 解速率匹配（RV）→ LDPC 译码 → 分段重组 → CRC 校验</td></tr>
<tr><td>5</td><td><b>预编码与映射</b>：按所选预编码器把层映射到天线端口 1000+；绕开 rateMatchPattern/ZP CSI-RS/SSB/DM-RS 映射 RE</td><td>5</td><td><b>信道估计</b>：按 DCI 的天线端口字段确定 DM-RS 端口/CDM 组 → 前载+附加 DM-RS 估信道 → PRG 内合并（PRB bundling 假设）</td></tr>
<tr><td>6</td><td><b>波束发射</b>：按所选 TCI 状态（QCL-TypeD）用对应波束发射；功率按 §4.1 的 EPRE 折算（powerControlOffset 关系）</td><td>6</td><td><b>波束接收</b>：按 DCI 的 TCI 字段→MAC CE 激活的 8 状态池→QCL-TypeD 源定接收波束；EPRE 假设按功率参数还原</td></tr>
<tr><td>7</td><td><b>等反馈</b>：K1 时隙后在 PUCCH 收 HARQ-ACK；NACK → 换 RV 重传（0→2→3→1）；CBG 场景只重传错的那组码块</td><td>7</td><td><b>反馈</b>：解码成功→ACK；失败→NACK（按 CBG 配置逐组反馈）；软合并存储</td></tr>
<tr><td>8</td><td><b>SPS 场景</b>：按 SPS-config 周期免 DCI 重发（CS-RNTI 激活）；聚合因子 n2/n4/n8 时按表轮换 RV</td><td>8</td><td><b>SPS 场景</b>：按 SPS 配置周期盲检/接收，无 DCI 时用 RRC 配置的整套参数</td></tr>
</table>

<h3>7.2 参数双端使用总表（谁配 / 给谁 / 基站如何使用 / UE 如何使用）</h3>
<table>
<tr><th>参数</th><th>配置方→配置给谁</th><th>基站如何使用</th><th>UE 如何使用</th></tr>
<tr><td>pdsch-TimeDomainAllocationList</td><td>RRC（gNB）→ UE</td><td>DCI 的时域分配字段指行号，选定 K0/S/L/映射类型</td><td>查表把 m 字段翻译成 K0/S/L</td></tr>
<tr><td>resourceAllocation / rbg-Size</td><td>RRC → UE</td><td>按类型生成 type 0 位图或 type 1 RIV 填 DCI</td><td>按类型解析字段得 RB 集合</td></tr>
<tr><td>mcs-Table</td><td>RRC → UE</td><td>按所选表把调度决策的 Qm/R 编成 I_MCS</td><td>按表把 I_MCS 翻回 Qm/R 算 TBS</td></tr>
<tr><td>xOverhead</td><td>RRC → UE</td><td>TBS 公式扣 6/12/18 开销——基站与 UE 必须同口径</td><td>TBS 公式同一 N_oh 值（口径一致是 TBS 对上的前提）</td></tr>
<tr><td>nrofHARQ-ProcessesForPDSCH</td><td>RRC → UE</td><td>限制并行 HARQ 进程数（调度器记账）</td><td>按进程 ID 软合并管理</td></tr>
<tr><td>dmrs-DownlinkForPDSCH-MappingTypeA/B</td><td>RRC → UE</td><td>按配置生成 DM-RS（类型/前载位置/附加位置）</td><td>按配置在正确 RE 上做信道估计</td></tr>
<tr><td>tci-StatesToAddModList</td><td>RRC → UE + MAC CE 激活</td><td>DCI 的 TCI 字段选激活池中的状态 → 用该波束发</td><td>按 TCI→QCL-TypeD 定接收波束</td></tr>
<tr><td>rateMatchPattern* / zp-CSI-RS-*</td><td>RRC → UE（DCI 可动态选组）</td><td>在这些 RE 上不发 PDSCH（绕开）</td><td>解速率匹配时把这些 RE 视为未占用</td></tr>
<tr><td>prb-BundlingType</td><td>RRC → UE（DCI 可选）</td><td>PRG 内保持同一预编码（约束预编码器设计）</td><td>PRG 内跨 RB 合并信道估计</td></tr>
<tr><td>pdsch-AggregationFactor</td><td>RRC → UE</td><td>同一分配跨 n 时隙重复发（RV 轮换）</td><td>跨时隙软合并（单层传输）</td></tr>
<tr><td>maxNrofCodeWordsScheduledByDCI</td><td>RRC → UE</td><td>双码字时组两套 MCS/RV/NDI</td><td>按字段数解析 DCI、解两 TB</td></tr>
<tr><td>dataScramblingIdentityPDSCH</td><td>RRC → UE</td><td>用 n_ID 生成加扰序列</td><td>用同一 n_ID 解扰</td></tr>
<tr><td>vrb-ToPRB-Interleaver</td><td>RRC → UE</td><td>VRB 按交织单元映射到 PRB 发射</td><td>逆映射还原 VRB</td></tr>
<tr><td>maxMIMO-Layers / codeBlockGroupTransmission</td><td>RRC → UE</td><td>限制层数上限；CBG 场景按组重传</td><td>层数内解调；CBG 逐组反馈</td></tr>
<tr><td><b>调度器决策（MCS 精确值、预编码器、波束、功率）</b></td><td><b>gNB 内部实现（规范不规定）</b></td><td>外环 CQI 修正选 MCS；CSI 反馈/互易性选预编码；L1-RSRP 选波束；EPRE 功率分配</td><td>不感知——UE 只按 DCI 的最终指示执行</td></tr>
<tr><td><b>QoS 参数（5QI/GBR）</b></td><td><b>核心网 → gNB（QoS flow 映射）</b></td><td>调度优先级权重（GBR 优先、非 GBR 比例公平）→ 影响"谁先被调度"</td><td>不感知——但时延/吞吐体验由此决定</td></tr>
</table>

<h3>7.3 基站内部如何使用（规范外实现原理，标注【解读/推导】）</h3>
<div class="jiexi"><b>① 调度器</b>：周期（如每时隙）收集各 UE 的 BSR（上行报的缓冲状态）、CSI 反馈、HARQ 状态、QoS 权重，按比例公平（吞吐/历史平均）选 UE 与资源——PDSCH 的"共享"由它实现。<br><b>② MCS 外环</b>：以 CSI 的 CQI 为起点，按 ACK/NACK 统计微调（连续 NACK 降档、连续 ACK 升档）——CQI 是"开环输入"，外环是"闭环修正"。<br><b>③ 预编码选择</b>：TDD 用上行 SRS 互易性直接算；FDD 用 UE 上报的 PMI（或自算）。<br><b>④ 波束选择</b>：波束管理的 L1-RSRP/CRI 反馈 → 选 TCI；移动中周期重评。<br><b>⑤ 功率</b>：总功率在 RE/层间分配，按 powerControlOffset 保持 PDSCH↔CSI-RS 的 EPRE 比例（UE 算 CQI 的功率假设来源）。</div>

<h3>7.4 应用场景矩阵（各场景的参数差异）</h3>
<table>
<tr><th>场景</th><th>RNTI</th><th>时域表</th><th>频域/调制</th><th>QCL/TCI</th><th>其他特征</th></tr>
<tr><td>SIB1/OSI</td><td>SI-RNTI</td><td>Default A/B/C（按复用模式）</td><td>type 1、QPSK（Qm≤2）</td><td>与 SSB QCL</td><td>TBS≤2976 bit；周期 160/80ms</td></tr>
<tr><td>寻呼</td><td>P-RNTI</td><td>Default A/B/C</td><td>type 1、QPSK</td><td>与 SSB QCL</td><td>PO 内多波束重复</td></tr>
<tr><td>RAR</td><td>RA-RNTI</td><td>Default A</td><td>type 1、QPSK</td><td>与所选 SSB/CSI-RS QCL</td><td>TB scaling 字段 0.5/0.25</td></tr>
<tr><td>Msg4</td><td>TC-RNTI</td><td>Default A</td><td>type 1、QPSK</td><td>与所选 SSB QCL</td><td>冲突解决</td></tr>
<tr><td>业务数据</td><td>C-RNTI</td><td>专用列表（可配）</td><td>type 0/1 动态、至 256QAM</td><td>TCI 动态指示</td><td>最多 8 层/双码字/CBG</td></tr>
<tr><td>SPS 业务</td><td>CS-RNTI</td><td>专用/SPS 配置</td><td>同上</td><td>同上</td><td>周期免 DCI；激活/释放</td></tr>
<tr><td>URLLC</td><td>MCS-C-RNTI</td><td>Type B 短分配</td><td>表 3 低谱效（BLER 10⁻⁵）</td><td>同上</td><td>CBG 重传、低时延</td></tr>
</table>

<h3>7.5 本讲小结（把球交给下一讲）</h3>
<div class="bridge"><b>小结</b>：PDSCH 的每个参数都有明确的"配置方与使用者"——RRC 参数给 UE 按图索骥、DCI 参数给本次传输的即时指示、基站内部决策（调度/MCS/预编码/波束/功率）是规范外实现、QoS 从核心网输入调度权重；基站发送 8 步与 UE 接收 8 步逐环对应。<b>引出下一讲</b>：第 8 讲把 1~7 讲的机制串成端到端回顾并汇总易错点。</div>

'''
anchor7 = '<h2>7. 第 7 讲　端到端回顾与易错点</h2>'
i = h.find(anchor7)
assert i > 0
h = h[:i] + sec7 + h[i:]

# ============ ③ 编号顺延 + 目录 ============
h = h.replace('<h2>7. 第 7 讲　端到端回顾与易错点</h2>', '<h2>8. 第 8 讲　端到端回顾与易错点</h2>')
h = h.replace('<h3>7.1 PDSCH 接收全流程', '<h3>8.1 PDSCH 接收全流程')
h = h.replace('<h3>7.2 易错点/澄清总表</h3>', '<h3>8.2 易错点/澄清总表</h3>')
h = h.replace('<h3>7.3 主线收口</h3>', '<h3>8.3 主线收口</h3>')
h = h.replace('把 1~6 讲串成一条线', '把 1~7 讲串成一条线')
h = h.replace('（第 7 讲端到端）', '（第 8 讲端到端）')
h = h.replace('<h2>8. 练习册（25 题含答案）</h2>', '<h2>9. 练习册（25 题含答案）</h2>')
h = h.replace('<h3>8.1 选择题（1~10）</h3>', '<h3>9.1 选择题（1~10）</h3>')
h = h.replace('<h3>8.2 填空题（11~16）</h3>', '<h3>9.2 填空题（11~16）</h3>')
h = h.replace('<h3>8.3 判断题（17~20）</h3>', '<h3>9.3 判断题（17~20）</h3>')
h = h.replace('<h3>8.4 计算题（21~25）</h3>', '<h3>9.4 计算题（21~25）</h3>')
h = h.replace('<h2>9. 交互式计算器</h2>', '<h2>10. 交互式计算器</h2>')
h = h.replace('<h2>10. 专题总结</h2>', '<h2>11. 专题总结</h2>')
h = h.replace('③ 按第 7 讲八步流程默写一次', '③ 按第 7/8 讲的双端流程默写一次')
h = h.replace('<li>第 7 讲　端到端回顾与易错点</li>', '<li>第 7 讲　基站-UE 双视角落地（参数谁配、谁用、怎么用）</li>\n<li>第 8 讲　端到端回顾与易错点</li>')
h = h.replace('<li>练习册（25 题含答案）+ 交互式计算器</li>', '<li>练习册（25 题含答案）+ 交互式计算器</li>')

open(f, 'w', encoding='utf-8').write(h)
print('PDSCH 深化完成 | 大小:', len(h))
print('h2:', len(re.findall(r'<h2>', h)), '| 双端表:', h.count('基站如何使用'), '| 场景矩阵:', h.count('应用场景矩阵'))
