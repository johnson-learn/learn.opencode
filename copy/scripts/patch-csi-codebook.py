# -*- coding: utf-8 -*-
"""插入 Type I 多天线码本补充节（5.2 补）"""

f = r'<3GPP文档库目录>\CSI-信道状态信息全梳理.html'
h = open(f, encoding='utf-8').read()

sec = '''<h3>5.2+ 深入：Type I 单面板多天线码本（i1/i2 两级结构与波束向量）</h3>
<div class="orig"><b>38.214 V15.4.0 §5.2.2.2.1（原文，节选）</b>：For 4 antenna ports {3000, 3001, 3002, 3003}, 8 antenna ports {3000, 3001, …, 3007}, 12 antenna ports …, 16 antenna ports …, 24 antenna ports …, and 32 antenna ports {3000, 3001, …, 3031}, and the UE configured with higher layer parameter codebookType set to 'typeI-SinglePanel', except when the number of layers \\(\\nu\\in\\{2,3,4\\}\\) (where \\(\\nu\\) is the associated RI value), each PMI value corresponds to three codebook indices \\(i_{1,1}, i_{1,2}, i_2\\). When the number of layers \\(\\nu\\in\\{2,3,4\\}\\), each PMI value corresponds to four codebook indices \\(i_{1,1}, i_{1,2}, i_{1,3}, i_2\\). … The quantities \\(\\phi_n, \\theta_p, u_m, v_{l,m}\\), and \\(\\tilde{v}_{l,m}\\) are given by 【公式已核实】<br>
\\[\\phi_n = e^{j\\pi n/2}, \\qquad \\theta_p = e^{j\\pi p/4}\\]
\\[u_m = \\begin{cases} \\left[1\\ e^{j2\\pi m/O_2N_2}\\ \\dots\\ e^{j2\\pi m(N_2-1)/O_2N_2}\\right]^T & N_2 &gt; 1 \\\\ 1 & N_2 = 1 \\end{cases}\\]
\\[v_{l,m} = \\left[u_m\\ \\ e^{j2\\pi l/O_1N_1}u_m\\ \\ \\dots\\ \\ e^{j2\\pi l(N_1-1)/O_1N_1}u_m\\right]^T\\]
\\[\\tilde{v}_{l,m} = \\left[u_m\\ \\ e^{j\\pi l}u_m\\ \\ \\dots\\ \\ e^{j\\pi l(N_1/2-1)}u_m\\ -u_m\\ -e^{j\\pi l}u_m\\ \\dots\\ -e^{j\\pi l(N_1/2-1)}u_m\\right]^T\\]
- The values of \\(N_1\\) and \\(N_2\\) are configured with the higher layer parameter n1-n2, respectively. The supported configurations of \\((N_1,N_2)\\) for a given number of CSI-RS ports and the corresponding values of \\((O_1,O_2)\\) are given in Table 5.2.2.2.1-2. … UE shall only use \\(i_{1,2}=0\\) and shall not report \\(i_{1,2}\\) if the value of \\(N_2\\) is 1.</div>
<p><b>翻译</b>：① 4/8/12/16/24/32 端口 + typeI-SinglePanel 时，除层数 \\(\\nu\\in\\{2,3,4\\}\\) 外，每个 PMI 值对应三个码本索引 \\(i_{1,1}, i_{1,2}, i_2\\)；层数 2/3/4 时对应四个索引 \\(i_{1,1}, i_{1,2}, i_{1,3}, i_2\\)。② 基础量 \\(\\phi_n\\)（QPSK 同相合并）、\\(\\theta_p\\)（8PSK）、\\(u_m\\)（垂直维 DFT 波束）、\\(v_{l,m}\\)（二维波束：水平 l × 垂直 m）、\\(\\tilde{v}_{l,m}\\)（\\(N_1&gt;1\\) 时的交替反转变体）按上式定义。③ \\(N_1,N_2\\) 由 n1-n2 配置，\\((N_1,N_2)\\) 与 \\((O_1,O_2)\\) 的允许组合查表 5.2.2.2.1-2。④ \\(N_2=1\\) 时 \\(i_{1,2}=0\\) 且不上报。</p>
<table>
<tr><th>端口数 \\(P_{CSI-RS}\\)</th><th>\\((N_1,N_2)\\)</th><th>\\((O_1,O_2)\\)</th></tr>
<tr><td>4</td><td>(2,1)</td><td>(4,1)</td></tr>
<tr><td>8</td><td>(2,2) / (4,1)</td><td>(4,4) / (4,1)</td></tr>
<tr><td>12</td><td>(3,2) / (6,1)</td><td>(4,4) / (4,1)</td></tr>
<tr><td>16</td><td>(4,2) / (8,1)</td><td>(4,4) / (4,1)</td></tr>
<tr><td>24</td><td>(4,3) / (6,2) / (12,1)</td><td>(4,4) / (4,4) / (4,1)</td></tr>
<tr><td>32</td><td>(4,4) / (8,2) / (16,1)</td><td>(4,4) / (4,4) / (4,1)</td></tr>
</table>
<p class="src">（Table 5.2.2.2.1-2，38.214 V15.4.0 原文数值。）</p>
<div class="jiexi"><b>两级码本结构 W = W₁W₂（主线视角：为什么分两级）</b>：<br>
① <b>W₁ 是宽带的"波束组选择"</b>：由 \\(i_{1,1}\\)（水平波束索引 l）、\\(i_{1,2}\\)（垂直波束索引 m，N₂=1 时省略）在过采样波束网格（\\(N_1O_1\\times N_2O_2\\) 个 2D-DFT 波束）里选一个波束方向 \\(v_{l,m}\\)；\\(i_{1,3}\\)（仅 2/3/4 层）再从 \\(v_{l,m}\\) 附近选第二个正交波束 \\(v_{l',m'}\\)（映射表 5.2.2.2.1-3/4 给出 k₁/k₂）。<br>
② <b>W₂ 是子带的"波束合并"</b>：由 \\(i_2\\) 在两个极化之间选同相合并相位 \\(\\phi_n\\in\\{1,j,-1,-j\\}\\)（QPSK），并做波束选择。以 1 层 codebookMode=1 为例【公式已核实】：
\\[W^{(1)}_{l,m,n} = \\frac{1}{\\sqrt{P_{CSI-RS}}}\\begin{bmatrix} v_{l,m} \\\\ \\phi_n v_{l,m} \\end{bmatrix}\\]
即同一波束分别用于 +45°/−45° 两个极化，相位差 \\(\\phi_n\\) 对齐后叠加。<br>
③ <b>为什么拆宽带/子带</b>：波束方向（l,m）随大尺度信道慢变，宽带上报一次即可；同相合并相位随频选快变，需要每子带上报——这是 i1 宽带 + i2 子带的根本原因，与第 4 讲"子带 PMI = 宽带 i1 + 子带 i2"完全对应。<br>
④ <b>码本子集限制位图</b>：n1-n2 位图共 \\(A_c=N_1O_1N_2O_2\\) 位，每位对应一个 \\(v_{l,m}\\)（秩 3/4 且 16/24/32 端口时每 3 位一组对应 \\(\\tilde{v}_{l,m}\\) 系）；typeI-SinglePanel-ri-Restriction 8 bit 按秩禁报；typeI-SinglePanel-codebookSubsetRestriction-i2 16 bit 按 i2 禁报（cri-RI-i1-CQI 用）。</div>
<div class="example"><b>例题 5.2</b>：8 端口 CSI-RS，n1-n2=(4,1)、\\((O_1,O_2)=(4,1)\\)，\\(i_{1,1}=2\\)、\\(i_2\\) 指示 \\(\\phi_n=j\\)（n=1）。写出 1 层预编码矩阵 W 的构造。<br>
<b>解</b>：N₂=1 → \\(u_m=1\\)、\\(i_{1,2}\\) 不报。\\(v_{l,m}=v_{2,0}=[1\\ e^{j2\\pi\\cdot2/16}\\ e^{j2\\pi\\cdot4/16}\\ e^{j2\\pi\\cdot6/16}]^T=[1\\ e^{j\\pi/4}\\ e^{j\\pi/2}\\ e^{j3\\pi/4}]^T\\)（\\(N_1O_1=16\\) 个水平波束中第 2 个）。<br>
\\[W^{(1)}_{2,0,1} = \\frac{1}{\\sqrt{8}}\\begin{bmatrix} 1 \\\\ e^{j\\pi/4} \\\\ e^{j\\pi/2} \\\\ e^{j3\\pi/4} \\\\ j \\\\ je^{j\\pi/4} \\\\ je^{j\\pi/2} \\\\ je^{j3\\pi/4} \\end{bmatrix}\\]
（上 4 行为 +45° 极化、下 4 行为 −45° 极化乘 \\(\\phi_1=j\\)；\\(1/\\sqrt{P_{CSI-RS}}=1/\\sqrt{8}\\) 归一化）。<b>要点</b>：\\(e^{j2\\pi l/O_1N_1}\\) 的相位步进 = 2π/16——16 个过采样水平波束覆盖 0~2π。</div>

'''
anchor = '<h3>5.3 计算基准：CSI 参考资源（38.214 §5.2.2.5）</h3>'
i = h.find(anchor)
assert i > 0, '锚点缺失'
h = h[:i] + sec + '\n' + h[i:]
open(f, 'w', encoding='utf-8').write(h)
print('插入完成 | 大小:', len(h))
