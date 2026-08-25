# -*- coding: utf-8 -*-
"""PUSCH 消除"同构"带过：展开 SLIV/RIV/RBG/MCS/TBS/处理链各步"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
d = r'<用户桌面目录>\NR-f40'
f = d + r'\PUSCH-物理上行共享信道全梳理.html'
h = open(f, encoding='utf-8').read()

# 1) 第 2 讲设问
h = h.replace(
    '<div class="q">设问（承接第 1 讲）：上行资源的时频定位与下行同构（K2/SLIV/RIV），但多了频率跳频（intraSlot/interSlot）——本讲讲上行分配与跳频。</div>',
    '<div class="q">设问（承接第 1 讲）：上行数据放在哪些时频资源上？——时域靠 K2 时隙偏移 + SLIV 联合编码（S/L 编进一个数）、频域靠 type 0 位图或 type 1 的 RIV 联合编码（起点+长度编进一个数）；上行还多了下行没有的频率跳频（intraSlot/interSlot）。本讲把这些定位机制全部展开。</div>')

# 2) 2.1 节：展开 SLIV
h = h.replace(
    '<div class="jiexi"><b>与 PDSCH 的差异</b>：① 时隙偏移叫 <b>K2</b>（DCI 时隙到 PUSCH 时隙）；② 合法 S/L 组合（表 6.1.2.1-1）：Type A：S=0、L∈{4..14}；Type B：S∈{0..13}、L∈{1..14}；③ 未配 pusch-TimeDomainAllocationList 时用默认表 A（16 行：j+1 行 → K2=j、Type A、S=0、L=14 等）。<b>SLIV 编解码公式与 PDSCH 完全相同</b>【公式已核实（同 38.214 §5.1.2.1）】。</div>',
    '<div class="orig"><b>38.214 V15.4.0 §6.1.2.1（原文，节选；公式对象已按 p2t 识别还原）</b>：The slot allocated for the PUSCH is \\(\\left\\lfloor n\\cdot\\dfrac{2^{\\mu_{PUSCH}}}{2^{\\mu_{PDCCH}}}\\right\\rfloor + K_2\\), where n is the slot with the scheduling DCI, and K2 is based on the numerology of PUSCH … The starting symbol S relative to the start of the slot, and the number of consecutive symbols L counting from the symbol S allocated for the PUSCH are determined from the start and length indicator SLIV:<br>\nif \\((L-1)\\le 7\\) then \\(SLIV = 14\\cdot(L-1) + S\\)<br>\nelse \\(SLIV = 14\\cdot(14-L+1) + (14-1-S)\\)<br>\nwhere \\(0 &lt; L \\le 14-S\\)</div>\n<div class="jiexi"><b>逐项展开</b>：① 时隙偏移叫 <b>K2</b>（DCI 时隙到 PUSCH 时隙），跨 numerology 按 \\(\\lfloor n\\cdot2^{\\mu_{PUSCH}-\\mu_{PDCCH}}\\rfloor+K_2\\) 换算。② SLIV 把 S/L 联合编进一个数：\\((L-1)\\le7\\) 时 \\(SLIV=14(L-1)+S\\)；\\((L-1)&gt;7\\) 时 \\(SLIV=14(14-L+1)+(13-S)\\)；解码：SLIV&lt;98 时 \\(L=SLIV\\div14+1\\)、\\(S=SLIV\\bmod14\\)，否则 \\(L=14-(SLIV\\div14)+1\\)、\\(S=13-(SLIV\\bmod14)\\)。③ 合法 S/L 组合（表 6.1.2.1-1）：Type A：S=0、L∈{4..14}；Type B：S∈{0..13}、L∈{1..14}（上行 Type A 的 S 只能是 0——固定从时隙头开始）。④ 未配 pusch-TimeDomainAllocationList 时用默认表 A（j+1 行：K2=j、Type A、S=0、L=14，j=0..15）。</div>')

# 3) 2.2 节：展开 type 0/1
h = h.replace(
    '<h3>2.2 频域分配（38.214 §6.1.2.2，与 PDSCH 同构）</h3>\n<div class="jiexi">type 0（RBG 位图：BWP≤36→2/4 等）与 type 1（RIV，含上行交织说明）与 PDSCH 规则相同；DCI 0_0 固定 type 1；dynamicSwitch 配在 resourceAllocation。<b>上行特色：RBG 交织</b>（38.211 §6.3.1.6）：VRB→PRB 交织（交织单元 2/4）在上行用于对抗窄带干扰。</div>',
    '<h3>2.2 频域分配 type 0 / type 1（38.214 §6.1.2.2 展开）</h3>\n<div class="orig"><b>38.214 V15.4.0 §6.1.2.2（原文，节选）</b>：Two uplink resource allocation schemes, type 0 and type 1, are supported. … The resource indication value is defined by [RIV 公式：if \\((L_{RBs}-1)\\le\\lfloor N_{BWP}^{size}/2\\rfloor\\) then \\(RIV=N_{BWP}^{size}(L_{RBs}-1)+RB_{start}\\) else \\(RIV=N_{BWP}^{size}(N_{BWP}^{size}-L_{RBs}+1)+(N_{BWP}^{size}-1-RB_{start})\\)]</div>\n<div class="jiexi"><b>逐项展开</b>：① 两种方案 type 0（RBG 位图）与 type 1（连续 RIV）。② DCI 0_0 固定 type 1；DCI 0_1 按 resourceAllocation（type0/type1/dynamicSwitch，dynamicSwitch 时 DCI 最高位选类型）。③ type 0：RBG 大小查表（BWP 1~36RB→2/4、37~72→4/8、73~144→8/16、145~275→16/16，config1/config2）；位图每 RBG 1 bit，MSB 对应最低频 RBG。④ type 1：RIV 联合编码起点与长度【公式已核实】——\\((L_{RBs}-1)\\le\\lfloor N/2\\rfloor\\) 用第一分支、否则第二分支；解码同 SLIV 思路。⑤ <b>上行特色：RBG 交织</b>（38.211 §6.3.1.6）：VRB→PRB 交织（交织单元 2/4）用于对抗上行窄带干扰。</div>')

# 4) 3.2 节：展开 MCS/TBS
h = h.replace(
    '<div class="jiexi"><b>同构</b>：MCS 5 bit 查表（PUSCH 也有三表：5.1.3.1-1/2/3 同构版，表 6.1.4.1-1/2/3）；TBS 四步相同（N\'_RE→N_RE→N_info→量化）。<b>差异</b>：① PUSCH 的 N\'_RE 扣除 DM-RS 时"包含 \\(\\alpha\\) 的 UCI 缩放"由 betaOffsets 决定（第 4 讲）；② 双码字仅上行不支持（PUSCH 单码字，最多 4 层）；③ 变换预编码时 Qm≤4。</div>',
    '<div class="jiexi"><b>MCS 查表</b>：DCI 0_0/0_1 的 MCS 5 bit 查表（表 6.1.4.1-1/2/3）：表 1 默认（QPSK~64QAM，I_MCS 0~28 有效、29~31 为重传 reserved）；表 2 含 256QAM（mcs-Table=qam256 时，仅 CP-OFDM）；表 3 低谱效（qam64LowSE）。<b>节选数值</b>（表 1）：I_MCS=0→QPSK 120/1024、8→QPSK 602、10→16QAM 340、16→16QAM 658、17→64QAM 438、20→64QAM 567、27→64QAM 910、28→64QAM 948。<br><b>TBS 四步（与 38.214 §5.1.3.2 同源公式，逐步列出）</b>：① 每 PRB 可用 RE：\\(N\'_{RE}=N_{sc}^{RB}\\cdot N_{symb}^{sh}-N_{DMRS}^{PRB}-N_{oh}^{PRB}\\)（12×符号数−DMRS−开销；PUSCH 无 xOverhead 参数，N_oh=0）；② 总 RE 与中间比特：\\(N_{RE}=N\'_{RE}\\cdot n_{PRB}\\)、\\(N_{info}=N_{RE}\\cdot R\\cdot Q_m\\cdot v\\)；③ \\(N_{info}\\le3824\\)：量化 \\(N\'_{info}=\\max(24,2^n\\lfloor N_{info}/2^n\\rfloor)\\)（\\(n=\\max(3,\\lfloor\\log_2 N_{info}\\rfloor-6)\\)）后查表 5.1.3.2-1 取不小于的最近值；④ \\(N_{info}&gt;3824\\)：\\(N\'_{info}=\\max(3840,2^n\\cdot\\text{round}((N_{info}-24)/2^n))\\)（\\(n=\\lfloor\\log_2(N_{info}-24)\\rfloor-5\\)），再按 R≤1/4、N\'&gt;8424 三分支做字节/码块对齐。<br><b>与 PDSCH 的实质差异</b>：① PUSCH 的可用 RE 计算要额外扣 UCI 占用的 RE（β_offset 决定，第 4 讲）；② 上行单码字（无第二 TB）；③ 变换预编码时 Qm≤4（无 256QAM）。</div>')

# 5) 4.1 表格"同"列展开
h = h.replace('<tr><td>1. TB CRC</td><td>24 bit（&gt;3824 时 16 bit 分到段）</td><td>同</td></tr>',
              '<tr><td>1. TB CRC</td><td>TB 附 24 bit CRC（A=信息+24；A&gt;3824 时 16 bit 附到每个分段）</td><td>与 DL-SCH 同源规则（§6.2.1）</td></tr>')
h = h.replace('<tr><td>2. 基图选择</td><td>BG1/BG2 同条件</td><td>同</td></tr>',
              '<tr><td>2. 基图选择</td><td>A≤292、或 A≤3824 且 R≤0.67、或 R≤0.25 → BG2；否则 BG1（§6.2.2）</td><td>条件与 DL 相同</td></tr>')
h = h.replace('<tr><td>3. 分段 + CB CRC</td><td>BG1 8448 / BG2 3840</td><td>同</td></tr>',
              '<tr><td>3. 分段 + CB CRC</td><td>按基图最大码块（BG1: K=8448、BG2: K=3840）分段，每段附 24 bit CRC（§6.2.3）</td><td>同 DL 规则</td></tr>')
h = h.replace('<tr><td>4. LDPC 编码 / 5. 速率匹配 / 6. 级联</td><td>QC-LDPC、RV 循环缓冲</td><td>同</td></tr>',
              '<tr><td>4. LDPC 编码</td><td>按 §5.3.2 基矩阵与提升因子 Z_c 做 QC-LDPC 编码（§6.2.4）</td><td>同 DL 规则</td></tr>\n<tr><td>5. 速率匹配</td><td>按 RV（0→2→3→1）从循环缓冲取 E_r 比特（§6.2.5）</td><td>同 DL 规则</td></tr>\n<tr><td>6. 码块级联</td><td>各码块速率匹配输出串接（§6.2.6）</td><td>同 DL 规则</td></tr>')

# 6) 设问/小结/图注措辞
h = h.replace('设问（承接第 3 讲）：上行 TB 的处理链与下行几乎同构，但多了一个关键环节——<b>UCI 与数据的复用</b>（HARQ-ACK/CSI 挤进 PUSCH 一起发）。本讲讲 UL-SCH 编码链与 UCI 复用。',
              '设问（承接第 3 讲）：上行 TB 在物理层要经过哪些处理？——UL-SCH 的编码链逐环节展开（CRC→基图→分段→LDPC→速率匹配→级联），其中上行独有一个关键环节：<b>UCI 与数据的复用</b>（HARQ-ACK/CSI 挤进 PUSCH 一起发）。')
h = h.replace('<b>小结</b>：上行时频分配与下行同构（K2/SLIV/type0/type1），另有 intraSlot/interSlot 跳频（偏移列表配置）。',
              '<b>小结</b>：时域 = K2 + SLIV（联合编码，上行 Type A 固定 S=0）；频域 = type 0 位图 / type 1 RIV；上行另有 intraSlot/interSlot 跳频（偏移列表配置）。')
h = h.replace('<b>小结</b>：MCS/TBS 与 PDSCH 同构；上行特色 = 变换预编码（DFT-s-OFDM/π/2-BPSK，低峰均比）+ 单码字 + 双 MCS 表。',
              '<b>小结</b>：MCS 查表（默认/256QAM/低谱效三表）+ TBS 四步（N\'_RE→N_RE→N_info→量化）；上行特色 = 变换预编码（DFT-s-OFDM/π/2-BPSK，低峰均比）+ 单码字 + 双 MCS 表 + UCI 扣 RE。')
h = h.replace('<b>小结</b>：UL-SCH 链与 DL 同构 + UCI 复用（HARQ-ACK&gt;CSI1&gt;CSI2 按 β_offset 插 RE）+ 可选变换预编码 + 最多 4 层。',
              '<b>小结</b>：UL-SCH 链 = CRC→BG→分段→LDPC→速率匹配→级联（各步如上表）→ UCI 复用（HARQ-ACK&gt;CSI1&gt;CSI2 按 β_offset 插 RE）→ 加扰/调制 → 可选变换预编码 → 最多 4 层。')
h = h.replace('PUSCH 处理链（第 4 讲）：与 PDSCH 同构 + 上行独有的 UCI 复用与可选变换预编码',
              'PUSCH 处理链（第 4 讲）：CRC → 基图选择 → 分段 → LDPC → 速率匹配 → 级联 → UCI 复用（上行独有）→ 加扰 → 调制 →（可选）变换预编码 → 层映射')
h = h.replace('① 上行资源的时频定位与下行同构', '① 上行资源的时频定位（K2/SLIV/RIV，见本讲展开）')

open(f, 'w', encoding='utf-8').write(h)
body_after = __import__('re').sub(r'<svg\b[\s\S]*?</svg>', '', h)
n = len(__import__('re').findall(r'同构|完全相同|几乎同构', body_after))
print('PUSCH 残留同构:', n)
