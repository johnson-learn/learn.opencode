# -*- coding: utf-8 -*-
"""系统消息：补四问定位 + 双视角落地讲次"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
d = r'<3GPP文档库目录>'
f = d + r'\系统消息-01-SSB-MIB-SIB1与OSI.html'
h = open(f, encoding='utf-8').read()

# ① 第 1 讲后插四问定位（1.1 之前）
sec = '''<h3>1.0 含义、作用、目的与应用场景（四问定位）</h3>
<table>
<tr><th>四问</th><th>内容</th></tr>
<tr><td><b>含义</b>（是什么）</td><td>系统消息（System Information，SI）是基站经 BCCH 逻辑信道周期广播的小区级公共信息——MIB（PBCH 承载）+ SIB1（SI-RNTI 调度）+ SI 消息（SIB2~SIB9 打包），三级递进</td></tr>
<tr><td><b>作用</b>（承载什么）</td><td>① 驻留判定（cellBarred/S 准则门限）；② 接入配置（RACH/初始 BWP/CORESET#0）；③ 移动性参数（SIB2~5 重选）；④ 公共告警（SIB6/7/8 ETWS/CMAS）；⑤ 时间同步（SIB9 GPS/UTC）</td></tr>
<tr><td><b>目的</b>（为什么存在）</td><td>UE 开机时对小区一无所知——SI 用"无先验知识可解"的广播让 UE 从零完成：找到小区（SSB）→ 拿到调度信息（MIB）→ 拿到驻留与接入参数（SIB1）→ 拿到完整配置（OSI）；空闲/非激活/连接三态共用</td></tr>
<tr><td><b>应用场景</b></td><td>开机接入、空闲态驻留与重选、寻呼监听、初始接入（RACH 参数）、灾难告警（ETWS/CMAS 秒级送达）、非激活态 RNA 更新、连接态的 SI 变更跟踪</td></tr>
</table>

'''
anchor = '<h3>1.1 原文：38.300 §5.2.5.5（MIB 与 SIB1 的递进关系）</h3>'
i = h.find(anchor)
assert i > 0
h = h[:i] + sec + h[i:]

# ② 第 7 讲前插双视角落地讲次
sec2v = '''<h2>7. 第 7 讲　基站-UE 双视角落地：系统消息谁配、谁用、怎么用</h2>

<div class="q">设问（承接第 1~6 讲）：前六讲把系统消息的机制讲完了，现在落到"使用"层——<b>每类参数由谁配置？基站侧怎么组织与广播？UE 侧怎么按序获取与使用？</b>——本讲给出双端流程对照与参数双端使用总表。</div>

<h3>7.1 双端流程对照（基站广播组织 ↔ UE 获取使用）</h3>
<table>
<tr><th>#</th><th>基站侧（gNB 如何组织与广播）</th><th>#</th><th>UE 侧（UE 如何获取与使用）</th></tr>
<tr><td>1</td><td><b>SSB 周期扫描</b>：按 Case A~E 的候选位置发 SSB 波束（ssb-PositionsInBurst 决定实际发哪些）</td><td>1</td><td><b>搜 SSB</b>：PSS/SSS 得 PCI 与帧边界、PBCH DM-RS 盲检得 SSB 索引低位</td></tr>
<tr><td>2</td><td><b>MIB 组包</b>：SFN 高 6 位 + subCarrierSpacingCommon + \(k_{SSB}\) 低 4 位 + pdcch-ConfigSIB1 查表索引 + cellBarred 等；按 80ms 周期塞进 PBCH</td><td>2</td><td><b>解 MIB</b>：PBCH Polar 解码 → 拼 SFN、查 CORESET#0/SS#0、记 cellBarred；\(k_{SSB}=31\)(FR1) 则判"无 SIB1"改找别的频率</td></tr>
<tr><td>3</td><td><b>SIB1 调度</b>：SI-RNTI 加扰的 DCI 1_0 在 SS#0 按 160ms/80ms 周期调度 SIB1（内容含 si-SchedulingInfo 全表）</td><td>3</td><td><b>收 SIB1</b>：Type0 CSS 盲检 SI-RNTI → 存 SIB1 → PLMN/驻留判定 → 应用 servingCellConfigCommon → 记 OSI 调度总表</td></tr>
<tr><td>4</td><td><b>OSI 广播</b>：按 si-SchedulingInfo 把 SIB2~9 打包进 SI 消息（同周期才同包），在各 SI 窗口内发（SI-RNTI）</td><td>4</td><td><b>收 OSI</b>：按窗口公式（x=(n−1)w、SFN mod T=⌊x/N⌋）逐个窗口盲检；SIB6/7/8 平时不读等 Short Message</td></tr>
<tr><td>5</td><td><b>变更管理</b>：内容要变 → 在修改周期 m 的寻呼时机发 Short Message（systemInfoModification=1）→ 周期 m+1 才播新内容</td><td>5</td><td><b>变更跟踪</b>：每 DRX 周期在 PF/PO 查 P-RNTI 的 Short Message → 置位则在下一修改周期重读；etwsAndCmasIndication 则立即重读 SIB1+SIB6/7/8</td></tr>
<tr><td>6</td><td><b>按需 SI 服务</b>：配 si-RequestConfig（专用前导）→ 收到请求前导后回 RAR(RAPID only) → 在 SI 窗口临时播该 SI 消息</td><td>6</td><td><b>按需请求</b>：需要 notBroadcasting 的 SI → Msg1 专用前导（或 Msg3 RRCSystemInfoRequest）→ 收到 ACK 立即进窗口收</td></tr>
<tr><td>7</td><td><b>参数一致性维护</b>：valueTag/areaScope/systemInformationAreaID 组织（区域级 SIB 跨小区复用）</td><td>7</td><td><b>存储复用</b>：跨小区比对 valueTag/areaScope 决定能否复用存储版本（3 小时有效期）</td></tr>
</table>

<h3>7.2 参数双端使用总表（谁配 / 给谁 / 基站如何使用 / UE 如何使用）</h3>
<table>
<tr><th>参数/信号</th><th>配置方→配置给谁</th><th>基站如何使用</th><th>UE 如何使用</th></tr>
<tr><td>SSB 序列/位置（PSS/SSS/PBCH）</td><td>gNB 自身决定（按 PCI 生成）</td><td>按 Case A~E 波束扫描发射；波束数按覆盖设计</td><td>相关检测得 \(N_{ID}^{(2)}\)/\(N_{ID}^{(1)}\)、DM-RS 盲检得索引低位</td></tr>
<tr><td>MIB（8 字段）</td><td>gNB（RRC 组包）→ UE</td><td>pdcch-ConfigSIB1 按小区 CORESET#0 设计查表反推；cellBarred 按运营策略</td><td>查表得 CORESET#0/SS#0；\(k_{SSB}\) 对齐资源网格；cellBarred 判驻留</td></tr>
<tr><td>SIB1 内容（cellSelectionInfo/si-SchedulingInfo/servingCellConfigCommon）</td><td>gNB（OAM 规划）→ UE</td><td>S 准则门限按小区覆盖设计；SI 窗口/周期按内容更新频率分配；RACH/初始 BWP 按容量规划</td><td>驻留判定、SI 窗口计算、初始接入参数</td></tr>
<tr><td>ssb-PositionsInBurst</td><td>gNB → UE（SIB1 内）</td><td>指示实际发射的波束位图（省功率只发需要的波束）</td><td>只在指示位置测 SSB；寻呼/OSI 监测时机与之一一对应</td></tr>
<tr><td>Short Message（systemInfoModification/etwsAndCmasIndication）</td><td>gNB 动态（P-RNTI DCI）→ UE</td><td>变更前一个修改周期发预告；灾情立即发</td><td>按位执行重读动作</td></tr>
<tr><td>si-RequestConfig（专用前导/时机）</td><td>gNB（RRC，SIB1 内）→ UE</td><td>为每个 notBroadcasting SI 消息预留前导组；收到请求即临时播</td><td>发对应前导（或 Msg3）→ 收 ACK → 进窗口</td></tr>
<tr><td>寻呼参数（defaultPagingCycle/nAndPagingFrameOffset/firstPDCCH-MonitoringOccasionOfPO）</td><td>gNB（RRC，SIB1 内）→ UE</td><td>按 UE 分组与寻呼容量配置 N/Ns/偏移</td><td>PF/PO 公式算自己的监听时机</td></tr>
<tr><td>ETWS/CMAS 内容（SIB6/7/8）</td><td>核心网（告警服务器）→ gNB → UE</td><td>收到告警即播、不受修改周期约束</td><td>告警能力 UE 立即接收显示</td></tr>
<tr><td>修改周期 m / valueTag / areaScope</td><td>gNB（RRC）→ UE</td><td>内容变更与预告的节奏控制</td><td>边界 SFN mod m=0；valueTag/areaScope 判存储复用</td></tr>
</table>

<h3>7.3 基站内部如何使用（规范外实现原理，标注【解读/推导】）</h3>
<div class="jiexi"><b>① SI 内容规划</b>：OAM 按小区角色（宏站/微站）、频段、PLMN 策略决定 SIB 内容——重选门限按邻区拓扑、SI 周期按内容更新频率（频变参数用短周期）。<br><b>② 窗口分配</b>：把 SIB 按周期分组打包（同周期同包），窗口数 × 窗口长度 ≤ 修改周期的预算内排布。<br><b>③ 波束与寻呼联动</b>：PO 的监测时机与 SSB 波束一一对应（每个波束轮发寻呼/Short Message）——保证波束全覆盖。<br><b>④ 变更纪律</b>：所有内容变更严格"预告→生效"两步走；ETWS/CMAS 例外直发。</div>

<h3>7.4 本讲小结（把球交给下一讲）</h3>
<div class="bridge"><b>小结</b>：系统消息参数分三类——gNB 自身决定（SSB 序列/波束）、RRC 广播给 UE（MIB/SIB1/OSI）、核心网输入（ETWS/CMAS 告警）；基站广播组织 7 步与 UE 获取使用 7 步逐环对应。<b>引出下一讲</b>：第 8 讲把 1~7 讲串成端到端九步流程并汇总易错点。</div>

'''
anchor7 = '<h2>7. 第 7 讲　端到端流程串联与易错点总表</h2>'
i = h.find(anchor7)
assert i > 0
h = h[:i] + sec2v + h[i:]

# 编号顺延
h = h.replace('<h2>7. 第 7 讲　端到端流程串联与易错点总表</h2>', '<h2>8. 第 8 讲　端到端流程串联与易错点总表</h2>')
h = h.replace('<h3>7.1 端到端全流程（系统消息视角）</h3>', '<h3>8.1 端到端全流程（系统消息视角）</h3>')
h = h.replace('<h3>7.2 易错点/澄清总表</h3>', '<h3>8.2 易错点/澄清总表</h3>')
h = h.replace('<h2>8. 练习册（25 题含答案）</h2>', '<h2>9. 练习册（25 题含答案）</h2>')
h = h.replace('<h2>9. 交互式计算器</h2>', '<h2>10. 交互式计算器</h2>')
h = h.replace('<h2>10. 专题总结</h2>', '<h2>11. 专题总结</h2>')
h = h.replace('④ 最后按第 7 讲的端到端流程默写一遍', '④ 最后按第 7/8 讲的双端流程默写一遍')
h = h.replace('<li>第 7 讲　端到端流程串联与易错点总表</li>', '<li>第 7 讲　基站-UE 双视角落地（谁配、谁用、怎么用）</li>\n<li>第 8 讲　端到端流程串联与易错点总表</li>')

open(f, 'w', encoding='utf-8').write(h)
print('系统消息深化完成 | 大小:', len(h), '| h2:', len(re.findall(r'<h2>', h)))
