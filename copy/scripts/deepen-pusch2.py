# -*- coding: utf-8 -*-
"""PUSCH 深化：① 变换预编码 DFT 公式展开 ② UCI 复用 RE 公式展开"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
d = r'C:\Users\job_p\Desktop\NR-f40'
f = d + r'\PUSCH-物理上行共享信道全梳理.html'
h = open(f, encoding='utf-8').read()

# ① 3.1 节后插入 DFT 公式展开
anchor = '<h3>3.2 MCS/TBS（38.214 §6.1.4）</h3>'
exp31 = '''<div class="orig"><b>38.211 V15.4.0 §6.3.1.4 Transform precoding（原文，节选；公式对象已按 p2t 识别还原）</b>：For each layer \(\lambda=0,\ldots,v-1\) the block of complex-valued symbols \(x^{(\lambda)}(0),\ldots,x^{(\lambda)}(M_{symb}^{layer}-1)\) shall be divided into \(M_{symb}^{layer}/M_{sc}^{PUSCH}\) sets, each corresponding to one OFDM symbol. Transform precoding shall be applied according to
\\[z(l\\cdot M_{sc}^{PUSCH}+k) = \\frac{1}{\\sqrt{M_{sc}^{PUSCH}}}\\sum_{i=0}^{M_{sc}^{PUSCH}-1}\\tilde{x}^{(0)}(l\\cdot M_{sc}^{PUSCH}+i)\\,e^{-j\\frac{2\\pi ik}{M_{sc}^{PUSCH}}}\\]
resulting in a block of complex-valued symbols \(z(0),\ldots,z(M_{symb}^{layer}-1)\).</div>
<p><b>翻译</b>：① 每层每 OFDM 符号的 \(M_{sc}^{PUSCH}\) 个调制符号做一次 \(M_{sc}^{PUSCH}\) 点 DFT；② 变换预编码公式：\(z(lM_{sc}+k)=\\frac{1}{\\sqrt{M_{sc}}}\\sum_{i}\\tilde{x}(lM_{sc}+i)e^{-j2\\pi ik/M_{sc}}\)——即"频域"符号 \(\tilde{x}\) 经 DFT 转回"时域"样点 z；③ 输出 z 再按常规 OFDM 做 IFFT 上子载波。</p>
<div class="jiexi"><b>逐符号解析（先解析后提炼）</b>：① \(\tilde{x}^{(0)}(lM_{sc}+i)\)：第 l 个 OFDM 符号的第 i 个调制符号（变换预编码只在单层 v=1 时使用——多层的空分复用强制 CP-OFDM）。② \(e^{-j2\\pi ik/M_{sc}}\)：DFT 核。③ 物理含义：DFT 把"频域星座点"摊平成"时域单载波样点"——每个样点是全部星座点的加权和，波形近似单载波 → 峰均比低；DFT + IFFT 级联 = 等效单载波频域均衡（SC-FDE），这就是"DFT-s-OFDM"名字的来历。④ <b>提炼</b>：变换预编码 = 每符号一次 DFT 扩频，代价是只能单层、最高 64QAM，收益是低峰均比（功放效率/覆盖）。</div>
<div class="example"><b>例题 3.0</b>：变换预编码启用、\(M_{sc}^{PUSCH}=12\)、π/2-BPSK。求第 1 个 OFDM 符号的 z(0)。<br>
<b>解</b>：z(0) = (1/√12)Σ_{i=0}^{11} x̃(i)·e^{−j·2π·i·0/12} = (1/√12)Σ x̃(i)——z(0) 是 12 个调制符号的均值（DC 分量）。<b>要点</b>：每个 z(k) 都是全部 12 个符号的加权和——这正是"单载波样点"的本质（时域样点间不再有星座结构，峰均比因此降低）。</div>

'''
i = h.find(anchor)
assert i > 0
h = h[:i] + exp31 + h[i:]

# ② 4.2 UCI 复用展开 RE 公式
anchor2 = '<div class="jiexi"><b>复用规则</b>（38.212 §6.3.2.4 归纳，标注【解读/归纳】）'
i = h.find(anchor2)
assert i > 0
exp42 = '''<div class="jiexi"><b>各类 UCI 的 RE 数计算（38.212 §6.3.2.4 归纳，标注【解读/归纳】；标准形式公式）</b>：<br>
① HARQ-ACK 占用的调制符号数（复用进 UL-SCH 时）：
\\[Q'_{ACK} = \\min\\left\\{\\left\\lceil\\frac{(O_{ACK}+L_{ACK})\\cdot\\beta^{PUSCH}_{offset}\\cdot\\sum_{l=0}^{N_{symb,all}^{PUSCH}-1}M_{sc}^{\\Phi}(l)}{\\sum_{r=0}^{C_{UL-SCH}-1}K_r}\\right\\rceil,\\ \\left\\lceil\\alpha\\cdot\\sum_{l=l_0}^{N_{symb,all}^{PUSCH}-1}M_{sc}^{\\Phi}(l)\\right\\rceil\\right\\}\\]
② CSI Part 1 / Part 2 同构公式（分子换 \\(O_{CSI-1}+L_{CSI-1}\\) 等）。<br>
<b>逐符号解析</b>：\\(O_{ACK}\\)=HARQ-ACK 比特数、\\(L_{ACK}\\)=CRC、\\(\\beta^{PUSCH}_{offset}\\)=β_offset 折算的"UCI 每比特相对数据每比特的信噪比保障"、\\(\\sum K_r\\)=UL-SCH 码块总比特（把 UCI 比特"换算成"等效数据比特）、\\(M_{sc}^{\\Phi}(l)\\)=符号 l 内可放 UCI 的子载波数、\\(\\alpha\\)=uci-OnPUSCH 的 scaling 上限。物理含义：β_offset 越大 UCI 占的 RE 越多（越可靠）；上限项防止 UCI 挤光数据。<b>提炼</b>：先按 β_offset 算需求、再按 α 封顶，HARQ-ACK&gt;CSI1&gt;CSI2 逐级插。'''
h = h[:i] + exp42 + h[i + len(anchor2):]

open(f, 'w', encoding='utf-8').write(h)
print('PUSCH 深化完成 | 大小:', len(h))
print('DFT 公式:', h.count('Transform precoding（原文'), '| UCI RE 公式:', h.count('Q\\' + "'" + '_'))
