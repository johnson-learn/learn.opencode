# -*- coding: utf-8 -*-
"""BWP/PDCCH/CSI/SRS 四专题：补四问定位 + 双视角落地讲次"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
d = r'<用户桌面目录>\NR-f40'

# ================= BWP =================
f = d + r'\BWP-带宽部分全梳理.html'
h = open(f, encoding='utf-8').read()
sec = '''<h2>专题深化：BWP 的基站-UE 双视角落地（谁配、谁用、怎么用）</h2>
<div class="q">设问：BWP 的参数由谁配置？基站侧怎么规划与指示切换？UE 侧怎么执行切换？——本讲给出四问定位、双端流程对照与参数双端使用总表。</div>
<h3>A. 四问定位（含义/作用/目的/应用场景）</h3>
<table>
<tr><th>四问</th><th>内容</th></tr>
<tr><td><b>含义</b></td><td>BWP（Bandwidth Part）是 UE 在小区载波带宽内被配置的<b>连续 PRB 子集</b>（频域窗口）：最多 4 个 DL BWP + 4 个 UL BWP，任一时刻每方向最多 1 个激活 BWP</td></tr>
<tr><td><b>作用</b></td><td>限定 UE 的收发带宽与 SCS：UE 只需在自己 BWP 内做射频/基带处理，不必覆盖整个小区带宽</td></tr>
<tr><td><b>目的</b></td><td>① 带宽自适应（BA）：低负载切窄 BWP 省电、高负载切宽 BWP 提速；② 适配能力差异 UE（窄带 UE 配窄 BWP）；③ 频段共存（避开干扰/与其他系统错位）</td></tr>
<tr><td><b>应用场景</b></td><td>大带宽 NR 部署（100MHz 小区给 20MHz 窄带 UE 配 20MHz BWP）、UE 省电（bwp-InactivityTimer 回退窄 BWP）、SCS 切换（FR2 的 60/120kHz BWP 间切换）、TDD/FDD 与 SUL 组合</td></tr>
</table>
<h3>B. 双端流程对照（基站规划指示 ↔ UE 执行）</h3>
<table>
<tr><th>#</th><th>基站侧</th><th>#</th><th>UE 侧</th></tr>
<tr><td>1</td><td><b>BWP 规划</b>：按小区带宽、UE 能力分布、业务模型决定每 BWP 的位置（locationAndBandwidth）、带宽、SCS；定初始 BWP（UE 首次接入用）与默认 BWP（回退用）</td><td>1</td><td><b>初始驻留</b>：按 SIB1 的 initialDownlinkBWP 收系统消息与随机接入</td></tr>
<tr><td>2</td><td><b>RRC 下发</b>：ServingCellConfig 内配全部 BWP（每 BWP 的 bwp-Id/SCS/带宽/位置 + 各信道配置）+ firstActive BWP-Id + defaultDownlinkBWP-Id + bwp-InactivityTimer</td><td>2</td><td><b>存储配置</b>：按 bwp-Id 建 BWP 表；RRC 重配后按 firstActive 激活</td></tr>
<tr><td>3</td><td><b>DCI 切换</b>：需要换 BWP 时在 DCI 1_1/0_1 的 bandwidth part indicator 字段（0~2 bit）指示目标 BWP</td><td>3</td><td><b>DCI 切换执行</b>：解析 indicator → 激活目标 BWP → 新 BWP 上收发（字段按新 BWP 位宽解释）</td></tr>
<tr><td>4</td><td><b>计时器回退</b>：配 bwp-InactivityTimer（2~2560ms，0.5/1ms 粒度）——UE 超时自动回默认 BWP</td><td>4</td><td><b>计时器管理</b>：每次收下行分配/上行授权重启计时器；超时 → 切回 defaultDownlinkBWP-Id（无 default 则初始 BWP）</td></tr>
<tr><td>5</td><td><b>RA 触发切换</b>：随机接入场景（无 PRACH 的 BWP）按 38.321 §5.15 规则触发 BWP 切换</td><td>5</td><td><b>RA 联动</b>：按 MAC 流程切 BWP 后发 preamble；RA 完成回原 BWP 或按规则停留</td></tr>
<tr><td>6</td><td><b>时延规划</b>：调度时预留切换时延（38.133 §8.6：Type 1 约 0.5~1ms、Type 2 约 1~2.5ms、SCS 切换至 6ms）——切换期间不调度该 UE</td><td>6</td><td><b>切换执行</b>：在切换时隙前后不收发；按 Type 1/2 要求的时间完成射频重调</td></tr>
</table>
<h3>C. 参数双端使用总表</h3>
<table>
<tr><th>参数</th><th>配置方→给谁</th><th>基站如何使用</th><th>UE 如何使用</th></tr>
<tr><td>locationAndBandwidth（RIV 编码）</td><td>RRC（gNB）→ UE</td><td>按 BWP 规划算 RIV（起始 RB + 长度）</td><td>RIV 解码得 BWP 起点与带宽</td></tr>
<tr><td>subcarrierSpacing / cyclicPrefix</td><td>RRC → UE</td><td>每 BWP 的 SCS 按频段与业务选（FR2 高低 SCS 分场景）</td><td>该 BWP 上全部信道按此 SCS</td></tr>
<tr><td>bwp-Id / firstActiveDownlinkBWP-Id</td><td>RRC → UE</td><td>RRC 重配后首先激活的 BWP</td><td>重配完成即切到 firstActive</td></tr>
<tr><td>defaultDownlinkBWP-Id</td><td>RRC → UE</td><td>省电回退目标（通常窄 BWP）</td><td>计时器超时/不活动回退目标</td></tr>
<tr><td>bwp-InactivityTimer</td><td>RRC → UE</td><td>按业务模型设超时（数据突发后多久回退）</td><td>无调度超时即回退</td></tr>
<tr><td>bandwidth part indicator（DCI 字段）</td><td>gNB 动态 → UE</td><td>每次调度时按需指示切换</td><td>解析并按新 BWP 解释 DCI 其余字段</td></tr>
<tr><td><b>切换决策（何时切、切到哪）</b></td><td><b>gNB 内部实现</b></td><td>流量预测（BSR/下行缓冲）与 UE 省电权衡决定</td><td>不感知——只按指示执行</td></tr>
</table>
'''
anchor = '<h2>第一部分：概念（第 1 讲）</h2>'
i = h.find(anchor)
assert i > 0
h = h[:i] + sec + '\n' + h[i:]
open(f, 'w', encoding='utf-8').write(h)
print('BWP 深化完成 | 大小:', len(h))

# ================= PDCCH =================
f = d + r'\PDCCH-物理下行控制信道全梳理.html'
h = open(f, encoding='utf-8').read()
sec = '''<h2>专题深化：PDCCH 的基站-UE 双视角落地（谁配、谁用、怎么用）</h2>
<div class="q">设问：PDCCH 的 CORESET/搜索空间/DCI 由谁配置？基站侧怎么生成与发射？UE 侧怎么盲检与解析？——本讲给出四问定位、双端流程对照与参数双端使用总表。</div>
<h3>A. 四问定位</h3>
<table>
<tr><th>四问</th><th>内容</th></tr>
<tr><td><b>含义</b></td><td>PDCCH 是承载下行控制信息（DCI）的物理控制信道：DCI 经 CRC/RNTI 加扰、Polar 编码、QPSK 调制后映射到 CORESET 内按聚合等级聚合的 CCE 上</td></tr>
<tr><td><b>作用</b></td><td>承载：上下行调度（DCI 0_x/1_x）、时隙格式指示（2_0）、抢占指示（2_1）、功控命令（2_2/2_3）——下行一切动态指示的总入口</td></tr>
<tr><td><b>目的</b></td><td>多 UE 共享控制资源 + 链路自适应（聚合等级 1~16 适配信道）+ 盲检可靠（RNTI 加扰 CRC 区分 UE）+ 波束化（每 CORESET 配 TCI）</td></tr>
<tr><td><b>应用场景</b></td><td>业务调度（C-RNTI）、SPS（CS-RNTI）、系统消息/寻呼/随机接入（SI/P/RA-RNTI）、组功控（TPC-RNTI）、URLLC 抢占指示（INT-RNTI）</td></tr>
</table>
<h3>B. 双端流程对照（基站发射 ↔ UE 接收）</h3>
<table>
<tr><th>#</th><th>基站侧</th><th>#</th><th>UE 侧</th></tr>
<tr><td>1</td><td><b>DCI 组包</b>：调度器决策（资源/MCS/预编码/K0/K1 等）按 DCI 格式组字段</td><td>1</td><td><b>盲检准备</b>：按搜索空间配置（周期/偏移/符号/聚合等级/候选数）确定本时隙要盲检的位置集合</td></tr>
<tr><td>2</td><td><b>CRC/RNTI</b>：24 bit CRC 与目标 UE 的 RNTI 异或（RNTI 就是"收件人"）</td><td>2</td><td><b>盲检</b>：每个候选位置解 Polar、CRC 用自己 RNTI 解扰——对上即命中</td></tr>
<tr><td>3</td><td><b>Polar 编码</b>：DCI+CRC 按 38.212 §7.3.3 Polar 编码（冻结位按规范）</td><td>3</td><td><b>Polar 译码</b>：逐候选译码（盲检预算内）</td></tr>
<tr><td>4</td><td><b>速率匹配</b>：按聚合等级定 E 比特（AL1=108、AL2=216…）</td><td>4</td><td><b>解速率匹配</b>：按候选聚合等级</td></tr>
<tr><td>5</td><td><b>加扰/QPSK</b>：c_init 含小区 ID；QPSK 调制</td><td>5</td><td><b>解扰/解调</b>：按 CORESET 配置</td></tr>
<tr><td>6</td><td><b>CCE 映射</b>：按哈希公式（Y_p 递推 + 哈希）把候选映射到 CORESET 的 CCE</td><td>6</td><td><b>哈希定位</b>：同公式算自己的候选 CCE 位置（无需知道别人）</td></tr>
<tr><td>7</td><td><b>波束发射</b>：按 CORESET 的 TCI（QCL-TypeD）发射</td><td>7</td><td><b>波束接收</b>：按 CORESET TCI 定接收波束（QCL-TypeD 冲突规则）</td></tr>
<tr><td>8</td><td><b>聚合等级选择</b>：按 UE 信道质量（CSI/功率）选 AL——差信道用高 AL</td><td>8</td><td><b>全 AL 盲检</b>：配置的每个 AL 都试（预算内）</td></tr>
</table>
<h3>C. 参数双端使用总表</h3>
<table>
<tr><th>参数</th><th>配置方→给谁</th><th>基站如何使用</th><th>UE 如何使用</th></tr>
<tr><td>CORESET（频域位图/符号数/交织/precoderGranularity/TCI）</td><td>RRC → UE（CORESET#0 由 MIB 查表）</td><td>CCE 映射的资源池；TCI 定发射波束</td><td>解映射的坐标；TCI 定接收波束</td></tr>
<tr><td>搜索空间（周期/偏移/时长/符号位图/AL/候选数/类型/DCI 格式）</td><td>RRC → UE（SS#0 由 MIB 查表）</td><td>按 UE 数与时延需求分配监测时机（错峰）</td><td>盲检时刻表——何时何格式盲检几次</td></tr>
<tr><td>DCI 字段（资源/MCS/K0/K1/TCI…）</td><td>gNB 动态 → UE</td><td>调度器决策的载体</td><td>解析后执行（收 PDSCH/发 PUSCH）</td></tr>
<tr><td>RNTI 分配（C-RNTI/CS-RNTI/MCS-C-RNTI/SP-CSI-RNTI…）</td><td>RRC → UE</td><td>区分 UE 与功能（每种 RNTI 一类命令）</td><td>CRC 解扰识别"是不是给我的、哪类命令"</td></tr>
<tr><td><b>聚合等级选择/调度决策</b></td><td><b>gNB 内部实现</b></td><td>信道质量差→高 AL；时延敏感→高监测密度</td><td>不感知——按配置全盲检</td></tr>
</table>
'''
anchor = '<h2>第一部分：概念与资源（第 1~2 讲）</h2>'
i = h.find(anchor)
assert i > 0
h = h[:i] + sec + '\n' + h[i:]
open(f, 'w', encoding='utf-8').write(h)
print('PDCCH 深化完成 | 大小:', len(h))
