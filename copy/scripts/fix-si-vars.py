# -*- coding: utf-8 -*-
"""正文变量统一 MathJax；SVG 内变量 tspan 上下标；修复替换残留"""
import re

# ---------- 1) gen-si-figs.py 内 SVG 文字 tspan 化 ----------
gp = r'C:\Users\job_p\AppData\Local\Temp\opencode\gen-si-figs.py'
g = open(gp, encoding='utf-8').read()
SUB = lambda w: f'<tspan baseline-shift="sub">{w}</tspan>'
SUP = lambda w: f'<tspan baseline-shift="super">{w}</tspan>'
n_crb = f'N{SUB("CRB")}{SUP("SSB")}'
n_id = f'N{SUB("ID")}{SUP("cell")}'
n_id1 = f'N{SUB("ID")}{SUP("(1)")}'
n_id2 = f'N{SUB("ID")}{SUP("(2)")}'
k_ssb = f'k{SUB("SSB")}'
l_max = f'L{SUB("max")}'
c_init = f'c{SUB("init")}'
a_hf = f'a{SUB("HRF")}'

reps = [
    ('k_SSB、SCS、DM-RS 位置', f'{k_ssb}、SCS、DM-RS 位置'),
    ('v = N_ID^cell mod 4（DM-RS 频移）', f'v = {n_id} mod 4（DM-RS 频移）'),
    ('SSB 起点所在 CRB（其子载波 0 即 k_SSB 的参考点，N = N_CRB^SSB）', f'SSB 起点所在 CRB（其子载波 0 即 {k_ssb} 的参考点，N = {n_crb}）'),
    ('k_SSB = 14', f'{k_ssb} = 14'),
    ('与 RB 栅格错位 k_SSB 个子载波', f'与 RB 栅格错位 {k_ssb} 个子载波'),
    ('k_SSB 低 4 bit：MIB 的 ssb-SubcarrierOffset（0~15）', f'{k_ssb} 低 4 bit：MIB 的 ssb-SubcarrierOffset（0~15）'),
    ('k_SSB 最高位（type A）：PBCH 载荷 a_Ā+5（38.212 §7.1.1）', f'{k_ssb} 最高位（type A）：PBCH 载荷 a{SUB("Ā+5")}（38.212 §7.1.1）'),
    ('判断：FR1 k_SSB ≤ 23 → 有 SIB1/CORESET#0；= 31 → 无 SIB1（pdcch-ConfigSIB1 改作频率位置/范围指示）', f'判断：FR1 {k_ssb} ≤ 23 → 有 SIB1/CORESET#0；= 31 → 无 SIB1（pdcch-ConfigSIB1 改作频率位置/范围指示）'),
    ('FR2：k_SSB ≤ 11 → 有；= 15 → 无（38.213 §4.1）', f'FR2：{k_ssb} ≤ 11 → 有；= 15 → 无（38.213 §4.1）'),
    ('L_max = 4', f'{l_max} = 4'),
    ('L_max = 8', f'{l_max} = 8'),
    ('c_init=N_ID^cell', f'{c_init} = {n_id}'),
    ('SFN低4位/半帧/k_SSB高位', f'SFN 低 4 位/半帧/{k_ssb} 高位'),
    ('PSS→N_ID^(2)+半帧；SSS→N_ID^(1)，PCI 定帧', f'PSS → {n_id2} + 半帧；SSS → {n_id1}，PCI 定帧'),
    ('SFN/k_SSB/SCS/pdcch-ConfigSIB1/cellBarred', f'SFN/{k_ssb}/SCS/pdcch-ConfigSIB1/cellBarred'),
]
for a, b in reps:
    n = g.count(a)
    g = g.replace(a, b)
    print(f'SVG 替换 {n} 处: {a[:36]}')
open(gp, 'w', encoding='utf-8').write(g)

# ---------- 2) HTML 正文变量 MathJax 化（跳过 svg） ----------
hf = r'C:\Users\job_p\Desktop\NR-f40\系统消息-01-SSB-MIB-SIB1与OSI.html'
h = open(hf, encoding='utf-8').read()
parts = re.split(r'(<svg\b[\s\S]*?</svg>)', h)
body_reps = [
    ('k_SSB', r'\(k_{SSB}\)'),
    ('L_max', r'\(L_{max}\)'),
    ('i_SSB', r'\(i_{SSB}\)'),
    ('n_hf', r'\(n_{hf}\)'),
    ('a_HRF', r'\(a_{HRF}\)'),
    ('c_init', r'\(c_{init}\)'),
    ('a_Ā+5', r'\(a_{\bar{A}+5}\)'),
    ('N_ID^cell', r'\(N_{ID}^{cell}\)'),
    ('MIB 是MIB（CORESET#0 查表', 'MIB 提供初始 PDCCH 配置（CORESET#0 查表'),
    ('SSB 是同步信号块（PSS/SSS 定 ID', 'SSB 提供同步与广播信道（PSS/SSS 确定 PCI'),
]
for i in range(0, len(parts), 2):
    for a, b in body_reps:
        parts[i] = parts[i].replace(a, b)
h2 = ''.join(parts)
open(hf, 'w', encoding='utf-8').write(h2)
print('正文变量 MathJax 化完成')

# 校验残留
h3 = open(hf, encoding='utf-8').read()
body3 = re.sub(r'<svg\b[\s\S]*?</svg>', '', h3)
for w in ['k_SSB', 'L_max', 'i_SSB', 'n_hf', 'a_HRF', 'c_init', 'a_Ā', 'N_ID^']:
    ms = re.findall('.{22}' + re.escape(w) + '.{18}', body3)
    if ms:
        print(f'残留 {w}: {len(ms)}')
        for m in ms[:4]:
            print('   ', m)
print('校验完毕')
