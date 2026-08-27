# -*- coding: utf-8 -*-
"""PDSCH 第 4 讲重写：LDPC 编码链逐步详细解析（原文+翻译+公式+例题+注意点，末尾才提炼）"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
d = r'<3GPP文档库目录>'
f = d + r'\PDSCH-物理下行共享信道全梳理.html'
h = open(f, encoding='utf-8').read()

new4 = '''<h2>4. 第 4 讲　物理层处理链：LDPC 编码（38.212 §7.2 逐环节）</h2>

<div class="q">设问（承接第 3 讲）：第 3 讲算出了 TBS——这个 TB 在物理层要经过哪些处理才变成 RE 上的调制符号？——本讲把 DL-SCH 编码链的七个环节逐环展开：每环先给 38.212 原文，再翻译，再讲公式与设计意图，最后给数值例题；全链走完后再给一张提炼总表。</div>

<h3>4.1 环节一：TB CRC 附加（38.212 §7.2.1）</h3>
<div class="orig"><b>原文（节选，公式对象已按 p2t 识别还原）</b>：Error detection is provided on each transport block through a Cyclic Redundancy Check (CRC). The entire transport block is used to calculate the CRC parity bits. Denote the bits in a transport block delivered to layer 1 by \(a_0,a_1,a_2,a_3,\ldots,a_{A-1}\), and the parity bits by \(p_0,p_1,p_2,p_3,\ldots,p_{L-1}\), where \(A\) is the payload size and \(L\) is the number of parity bits. … The parity bits are computed and attached to the DL-SCH transport block according to Subclause 5.1, by setting \(L\) to 24 bits and using the generator polynomial \(g_{CRC24A}(D)\) if \(A \le 3824\); and by setting \(L\) to 16 bits and using the generator polynomial \(g_{CRC16}(D)\) otherwise. The bits after CRC attachment are denoted by \(b_0,b_1,b_2,b_3,\ldots,b_{B-1}\), where \(B=A+L\).</div>
<p><b>翻译</b>：① 每个传输块通过 CRC 提供错误检测。② 整个传输块用于计算 CRC 校验位；A 为载荷大小、L 为校验位数。③ 校验位按 5.1 节附加：\(A\le3824\) 时 L=24、生成多项式 \(g_{CRC24A}(D)\)；\(A&gt;3824\) 时 L=16、生成多项式 \(g_{CRC16}(D)\)。④ CRC 附加后比特记为 \(b_0..b_{B-1}\)，\(B=A+L\)。</p>
<div class="jiexi"><b>设计意图</b>：CRC 是"接收端验货章"——UE 解完码先算 CRC，对上了才算接收成功（HARQ-ACK 的依据）。<b>为什么大 TB 用 16 bit？</b>大 TB 会被分段（环节三），每段还会再附 24 bit CRC（g_CRC24B），TB 级 CRC 只需"粗验"（段级 CRC 已能定位错误），16 bit 省开销。<b>注意</b>：\(a_0\) 是最低位信息比特、映射到 TB 的最高有效位（与 MAC 层约定一致）。</div>

<h3>4.2 环节二：LDPC 基图选择（38.212 §7.2.2）【公式已核实】</h3>
<div class="orig"><b>原文（节选，公式对象已按 p2t 识别还原）</b>：For initial transmission of a transport block with coding rate \(R\) indicated by the MCS index according to Subclause 5.1.3.1 in [6, TS 38.214] and subsequent re-transmission of the same transport block, each code block of the transport block is encoded with either LDPC base graph 1 or 2 according to the following:<br>
- if \(A \le 292\), or if \(A \le 3824\) and \(R \le 0.67\), or if \(R \le 0.25\), LDPC base graph 2 is used;<br>
- otherwise, LDPC base graph 1 is used,<br>
where \(A\) is the payload size in Subclause 7.2.1.</div>
<p><b>翻译</b>：① 对初传与同一 TB 的重传，每个码块按下述选 BG1 或 BG2（R 为 MCS 索引指示的码率、A 为 TB 载荷大小）：② 若 \(A\le292\)、或 \(A\le3824\) 且 \(R\le0.67\)、或 \(R\le0.25\) → 用 BG2；③ 否则用 BG1。</p>
<div class="jiexi"><b>三个条件的逐个解读</b>（先解析、后提炼）：<br>
① <b>\(A\le292\)</b>：极小 TB（如信令、小包）——BG2 的最小码块（K=10 系统列×Z）支持更短的块长，编码开销小。<br>
② <b>\(A\le3824\) 且 \(R\le0.67\)</b>：中小 TB 且码率不低——BG2 的最大码块 3840（含 CRC），中等块在低复杂度图上编码，译码迭代快。<br>
③ <b>\(R\le0.25\)</b>：极低码率（覆盖极限）——BG2 的低码率扩展区设计更优（度分布适合深覆盖）。<br>
④ 其余（大 TB 或高码率）→ BG1（最大码块 8448，支持大块高速率）。<br>
<b>两基图的差异</b>：BG1 基矩阵 46 行×68 列（22 系统列）、BG2 42 行×52 列（10 系统列）——BG1 面向大吞吐、BG2 面向短码低复杂度。基矩阵中每个非零元素代表一个 \(Z_c\times Z_c\) 的循环移位单位阵（QC-LDPC 结构），元素值 = 移位量。</div>
<div class="example"><b>例题 4.1</b>：三个 TB：① A=200、R=0.8；② A=2000、R=0.5；③ A=2000、R=0.2；④ A=100000、R=0.9。各选哪个基图？<br>
<b>解</b>：① A≤292 → <b>BG2</b>；② A≤3824 且 R≤0.67 → <b>BG2</b>；③ R≤0.25 → <b>BG2</b>；④ A&gt;3824 且 R&gt;0.67 且 R&gt;0.25 → <b>BG1</b>。✓ 提炼：小/中块与低码率走 BG2，大块高码率走 BG1。</div>

<h3>4.3 环节三：码块分段 + CB CRC（38.212 §7.2.3 → 5.2.2）</h3>
<div class="orig"><b>原文（节选）</b>：Code block segmentation and code block CRC attachment are performed according to Subclause 5.2.2. The bits after code block segmentation are denoted by \(c_{r0},c_{r1},\ldots,c_{r(K_r-1)}\), where \(r\) is the code block number and \(K_r\) is the number of bits for code block number \(r\).</div>
<p><b>翻译与流程</b>（5.2.2 原文归纳，标注【解读/归纳】）：① 若 \(B\le K_{cb}\)（K_cb = 基图最大码块 8448/3840）→ 单码块（C=1），跳过附加 CRC；② 否则分段：码块数 \(C=\lceil B/(K_{cb}-24)\rceil\)（每段预留 24 bit 段级 CRC），各段尽量等长（前 C− 段 K_+、其余 K_−，差 8 bit 内）；③ 每段附 24 bit CRC（g_CRC24B）。</p>
<div class="jiexi"><b>设计意图</b>：LDPC 译码复杂度随块长增长——分段把大 TB 切成可并行的码块（还支持 CBG 重传，第 6 讲）；段级 CRC 让 UE 能定位"哪个码块错了"（CBG 反馈的粒度）。</div>
<div class="example"><b>例题 4.2</b>：B=100000（含 TB CRC）、选 BG1（K_cb=8448）。求码块数。<br>
<b>解</b>：C=⌈100000/(8448−24)⌉=⌈100000/8424⌉=12 段。每段约 8333 bit + 24 CRC。</div>

<h3>4.4 环节四：QC-LDPC 编码（38.212 §7.2.4 → 5.3.2）</h3>
<div class="jiexi"><b>编码原理（5.3.2 归纳，标注【解读/归纳】）</b>：① <b>准循环 LDPC</b>：基矩阵（BG1/BG2 的元素 = 循环移位值）按提升因子 \(Z_c\) 提升——每个元素变成 \(Z_c\times Z_c\) 的循环移位单位阵；\(Z_c\) 从 51 个值的集合按码块大小 K 查表（\(Z_c\) 是满足 \(K_b\cdot Z_c\ge K\) 的最小值）。② <b>编码输出</b>：信息位（K 系统比特）+ 校验位（基矩阵行数×\(Z_c\)）→ 编码块长 N。③ <b>提升的意义</b>：同一基矩阵通过 \(Z_c\) 缩放适配不同块长——一套设计覆盖全部 TB 大小，硬件译码器只需处理最大 \(Z_c\)。</div>

<h3>4.5 环节五：速率匹配（38.212 §7.2.5 → 5.4.2）【公式已核实】</h3>
<div class="orig"><b>原文（节选，公式对象已按 p2t 识别还原）</b>：The bit sequence after encoding \(d_0,d_1,d_2,\ldots,d_{N-1}\) is written into a circular buffer of length \(N_{cb}\) for the r-th code block. For the r-th code block, let \(N_{cb}=N\) if \(I_{LBRM}=0\), and \(N_{cb}=\min(N, N_{ref})\) otherwise, where \(N_{ref}\) is determined according to TBS_LBRM assuming \(R_{LBRM}=2/3\). … \(k_0\) is the starting position of the r-th code block … \(E_r\) is the number of rate matched bits for the r-th code block.</div>
<p><b>翻译与流程</b>：① 编码比特 \(d_0..d_{N-1}\) 写入长 N_cb 的循环缓冲（环形缓冲区）。② \(I_{LBRM}=0\) 时 N_cb=N（全部）；=1（有限缓冲速率匹配，LBRM）时 N_cb=min(N, N_ref)——N_ref 按 TBS_LBRM、R_LBRM=2/3 折算，限制 UE 的软合并缓存。③ 速率匹配输出：从起始位置 k0 起，跳过填充比特，顺序取 E_r 比特（E_r = 该码块在 G 总比特中分到的配额）。④ k0 由 RV 确定：RV=0/1/2/3 对应循环缓冲中不同的四个等分起点。</p>
<div class="jiexi"><b>RV 与增量冗余</b>：RV=0 从起点取（自包含最多系统比特）；RV=2/3/1 的起点逐步深入校验区——重传时换 RV，前后两次传输的比特集合不同但同属一个母码，UE 软合并获得增量冗余增益。<b>N_cb 的 LBRM</b>：UE 能力受限时（有限缓冲），只缓存 min(N, N_ref) 比特，重传合并按 N_cb 循环——这是 38.306 定义的 UE 能力 1 的典型行为。</div>
<div class="example"><b>例题 4.3</b>：编码块 N=66×Z_c 比特，G 分配 E_r=2000，RV=0。求速率匹配输出。<br>
<b>解</b>：N_cb=N（无 LBRM）；RV=0 的 k0=0 → 从 d0 起跳过填充位顺序取 2000 比特。若 RV=2，k0 在循环缓冲约 1/2 处 → 取的 2000 比特大部分是校验位（纯增量信息）。</div>

<h3>4.6 环节六/七：码块级联与加扰调制层映射（38.212 §7.2.6 + 38.211 §7.3.1）</h3>
<div class="jiexi"><b>级联</b>：各码块的速率匹配输出 \(f_{r0}..f_{r(E_r-1)}\) 按 r=0..C−1 串接成 g_0..g_{G−1}（G=总码率匹配比特）。<br><b>加扰</b>（38.211 §7.3.1.1）：\(c_{init}=n_{RNTI}\cdot2^{15}+q\cdot2^{14}+n_{ID}\)——RNTI 参与初始化：不同 UE 的数据互相"看不懂"，即使资源重叠也能靠解扰失败丢弃。<br><b>调制</b>（§7.3.1.2）：QPSK/16QAM/64QAM/256QAM（Qm=2/4/6/8）。<br><b>层映射</b>（§7.3.1.3）：调制符号按层数 v 轮流分配到各层（v≤8）。<br><b>预编码与 RE 映射</b>（§7.3.1.5/7.3.1.6）：预编码对 UE 透明（含在 DM-RS 里）；映射先频域后时域，绕开 DM-RS/CSI-RS/PT-RS/SSB/速率匹配图案；VRB→PRB 可交织（单元 2/4）。</div>

<h3>4.7 提炼总表与例题（先详细解析，此处才提炼）</h3>
<table>
<tr><th>环节</th><th>输入</th><th>输出</th><th>关键点（一句提炼）</th></tr>
<tr><td>1. TB CRC</td><td>TB（A bit）</td><td>B=A+L（L=24/16）</td><td>整块验收章：≤3824 用 24bit、否则 16bit</td></tr>
<tr><td>2. 基图选择</td><td>A、R</td><td>BG1/BG2</td><td>A≤292 / A≤3824 且 R≤0.67 / R≤0.25 → BG2</td></tr>
<tr><td>3. 分段+CB CRC</td><td>B</td><td>C 段（每段+24 CRC）</td><td>K_cb=8448(BG1)/3840(BG2)</td></tr>
<tr><td>4. QC-LDPC</td><td>K 信息位</td><td>N 编码位</td><td>基矩阵×提升因子 Z_c</td></tr>
<tr><td>5. 速率匹配</td><td>N</td><td>E_r</td><td>循环缓冲 + RV 起点 k0</td></tr>
<tr><td>6. 级联</td><td>E_r×C</td><td>G</td><td>按码块序串接</td></tr>
<tr><td>7. 加扰/调制/层映射/映射</td><td>G</td><td>RE 符号</td><td>c_init 含 RNTI；先频后时映射</td></tr>
</table>
<div class="example"><b>例题 4.4（全链账目）</b>：TBS=8424 的 TB、码率 0.5、Qm=4、层数 2。走一遍处理链。<br>
<b>解</b>：① CRC：8424≤3824？否 → L=16 → B=8440。② 基图：A=8424&gt;3824、R=0.5 → 不满足任何 BG2 条件 → BG1。③ 分段：B=8440 ≤ K_cb=8448 → C=1 单码块（无段级 CRC）。④ 编码：K=8440 系统位 → N=66×Z_c（Z_c 按 K_b=22 取最小满足 22Z≥8440 → Z=384 → N=25344）。⑤ 速率匹配：G = TBS/Qm/层数反推的可用比特（按 432 RE×4×2≈3456）→ E_0=3456。⑥ 级联 G=3456。⑦ 调制 16QAM → 1728 符号 → 2 层各 864 → 映射。✓</div>

'''
# 用 h2 边界替换第 4 讲
i4 = h.index('<h2>4. 第 4 讲　物理层处理链：LDPC 编码（38.212 §7.2）</h2>')
i5 = h.index('<h2>5. 第 5 讲')
assert i4 > 0 and i5 > i4
h = h[:i4] + new4 + '\n' + h[i5:]

open(f, 'w', encoding='utf-8').write(h)
print('PDSCH 第 4 讲重写完成 | 大小:', len(h))
print('例题数:', len(re.findall(r'例题 4\.', h)), '| 提炼总表:', h.count('4.7 提炼总表'))
