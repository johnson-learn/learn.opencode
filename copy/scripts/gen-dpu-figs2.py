# -*- coding: utf-8 -*-
"""补充配图：PDSCH ×4 + PUSCH ×4"""
import os, subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

OUT = r'C:\Users\job_p\AppData\Local\Temp\opencode'
os.environ['PUPPETEER_EXECUTABLE_PATH'] = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
MMDC = r'C:\Users\job_p\AppData\Roaming\npm\mmdc.cmd'

def mmd(name, src):
    p = os.path.join(OUT, name + '.mmd')
    open(p, 'w', encoding='utf-8').write(src)
    r = subprocess.run([MMDC, '-i', p, '-o', os.path.join(OUT, name + '.svg'), '-b', 'white'],
                       capture_output=True, text=True, timeout=180)
    print(name, r.returncode, os.path.getsize(os.path.join(OUT, name + '.svg')))

# ---- PDSCH ----
mmd('dfig4', """flowchart TD
    A["输入：n_PRB、L、Qm、R、v、N_DMRS、xOverhead"] --> B["① 每 PRB 可用 RE<br/>N'_RE = 12·L − N_DMRS − N_oh"]
    B --> C["② 总 RE 与中间比特<br/>N_RE = N'_RE·n_PRB；N_info = N_RE·R·Qm·v"]
    C --> D{"N_info ≤ 3824？"}
    D -->|"是"| E["③ 量化：n=max(3,⌊log2 N_info⌋−6)<br/>N'_info=max(24, 2^n·⌊N_info/2^n⌋)<br/>查表 5.1.3.2-1 取不小于的最近值"]
    D -->|"否"| F["④ 量化：n=⌊log2(N_info−24)⌋−5<br/>N'_info=max(3840, 2^n·round((N_info−24)/2^n))"]
    F --> G{"R ≤ 1/4？"}
    G -->|"是"| H["TBS = 8C·⌈(N'_info+24)/8C⌉−24<br/>C=⌈(N'_info+24)/3816⌉"]
    G -->|"否"| I{"N'_info > 8424？"}
    I -->|"是"| J["TBS = 8C·⌈(N'_info+24)/8C⌉−24<br/>C=⌈(N'_info+24)/8424⌉"]
    I -->|"否"| K["TBS = 8·⌈(N'_info+24)/8⌉−24"]
    E --> L["TBS"]
    H --> L
    J --> L
    K --> L
""")

# MCS 谱效阶梯走势
fig, ax = plt.subplots(figsize=(10, 4.0), dpi=150)
t1 = [(0,0.2344),(4,0.6016),(8,1.1758),(10,1.3281),(12,1.6953),(16,2.5703),(17,2.5664),(20,3.3223),(24,4.5234),(28,5.5547)]
t2 = [(0,0.2344),(4,1.1758),(8,2.1602),(12,3.0293),(16,4.2129),(20,5.3320),(24,6.5703),(27,7.4063)]
t3 = [(0,0.0586),(4,0.1523),(8,0.3770),(12,0.8770),(16,1.4766),(20,2.4063),(24,3.3223),(28,4.5234)]
ax.plot([x for x,y in t1], [y for x,y in t1], 'o-', color='#1c6ab3', label='表 1（64QAM 上限）')
ax.plot([x for x,y in t2], [y for x,y in t2], 's-', color='#c55a11', label='表 2（256QAM）')
ax.plot([x for x,y in t3], [y for x,y in t3], '^-', color='#2e7d32', label='表 3（低谱效）')
ax.set_xlabel('I_MCS'); ax.set_ylabel('谱效 [bit/s/Hz]')
ax.set_title('PDSCH MCS 三表谱效阶梯对比（表 2 覆盖 256QAM 高谱效区、表 3 面向低谱效 URLLC）', fontsize=11)
ax.legend(); ax.grid(alpha=0.3)
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'dfig5.svg'), format='svg')
print('dfig5', os.path.getsize(os.path.join(OUT, 'dfig5.svg')))

# DM-RS Type1 vs Type2 图案
fig, axs = plt.subplots(1, 2, figsize=(10, 3.6), dpi=150)
for ax, title in zip(axs, ['Type 1（梳状 2，最多 8 端口）', 'Type 2（2×2 块，最多 12 端口）']):
    for s in range(14):
        for k in range(12):
            ax.add_patch(plt.Rectangle((s, k), 1, 1, fill=False, ec='#eeeeee', lw=0.4))
    ax.set_title(title, fontsize=10.5)
    ax.set_xticks(np.arange(14)+0.5); ax.set_xticklabels([str(i) for i in range(14)], fontsize=7)
    ax.set_yticks(np.arange(12)+0.5); ax.set_yticklabels([str(i) for i in range(12)], fontsize=7)
    ax.set_xlabel('符号'); ax.set_ylabel('子载波')
    ax.invert_yaxis()
    ax.set_xlim(0, 14); ax.set_ylim(0, 12)
    for sp in ['top', 'right']:
        ax.spines[sp].set_visible(False)
for k in [0, 1, 6, 7]:
    axs[0].scatter(2.5, k+0.5, s=150, color='#1c6ab3', zorder=5, marker='s')
for k in [0, 1, 6, 7]:
    axs[1].scatter(2.5, k+0.5, s=110, color='#1c6ab3', zorder=5, marker='s')
for k in [2, 3, 8, 9]:
    axs[1].scatter(2.5, k+0.5, s=110, color='#2e7d32', zorder=5, marker='s')
for k in [4, 5, 10, 11]:
    axs[1].scatter(2.5, k+0.5, s=110, color='#c55a11', zorder=5, marker='s')
axs[0].text(7, -1.6, 'CDM 组 0：子载波 0/1（+频域 OCC）', ha='center', fontsize=9, color='#1c6ab3')
axs[1].text(7, -1.6, '组 0：0/1　组 1：2/3　组 2：4/5（每 6 子载波一簇）', ha='center', fontsize=9, color='#555')
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'dfig6.svg'), format='svg')
print('dfig6', os.path.getsize(os.path.join(OUT, 'dfig6.svg')))

# RA type 0/1 示意
fig, ax = plt.subplots(figsize=(10, 3.0), dpi=150)
for i in range(20):
    c = '#a9d08e' if i < 8 else ('#a9d08e' if i >= 12 else '#f0f0f0')
    ax.add_patch(plt.Rectangle((i*0.45, 0.6), 0.4, 0.4, fc=c, ec='#888'))
for i in range(20):
    c = '#9dc3e6' if 4 <= i < 14 else '#f0f0f0'
    ax.add_patch(plt.Rectangle((i*0.45, 0.0), 0.4, 0.4, fc=c, ec='#888'))
ax.text(9*0.45-1, 0.95, 'type 0：RBG 位图（P=4：RBG0~3 分配 → 位图 111100…）', ha='center', fontsize=10, color='#33511f')
ax.text(9*0.45-1, 0.35, 'type 1：RIV（起点 4、长度 10 → 连续分配）', ha='center', fontsize=10, color='#1a3e6e')
ax.set_xlim(-0.3, 9.3); ax.set_ylim(-0.25, 1.5)
ax.axis('off')
ax.set_title('频域分配 type 0（位图）与 type 1（RIV 连续）对比示意', fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'dfig3.svg'), format='svg')
print('dfig3', os.path.getsize(os.path.join(OUT, 'dfig3.svg')))

# ---- PUSCH ----
mmd('ufig3', """flowchart TD
    A["调制符号序列"] --> B{"transformPrecoder？"}
    B -->|"disabled"| C["CP-OFDM：直接做 IFFT（多载波）<br/>谱效高（可 256QAM）、峰均比高"]
    B -->|"enabled"| D["DFT 扩频（DFT-s-OFDM）<br/>先把符号 DFT → 再 IFFT（等效单载波）<br/>峰均比低、省电；最高 64QAM；可 π/2-BPSK"]
    C --> E["RE 映射（频域平坦信道估计友好）"]
    D --> E
""")

mmd('ufig5', """flowchart LR
    A["PUSCH RE 总量（按 UL grant 分配）"] --> B["UL-SCH 数据占剩余 RE（TBS 计算时先扣 UCI 占位）"]
    A --> C["HARQ-ACK：最高优先级<br/>按 β_offset_HARQ-ACK 折算 RE 数，先插"]
    A --> D["CSI Part 1：次优先级<br/>按 β_offset_CSI-1 折算 RE"]
    A --> E["CSI Part 2：最低优先级<br/>按 β_offset_CSI-2 折算 RE；资源不足时从它开始砍"]
    C --> F["UCI 编码后按 38.212 §6.3.2.4 复用进 PUSCH（打孔或速率匹配）"]
    D --> F
    E --> F
""")

# P_PUSCH 功率分解
fig, ax = plt.subplots(figsize=(10, 3.6), dpi=150)
terms = ['P_O 目标功率\n（标称+UE 级）', '10log10(2^µ·M_RB)\n带宽项', 'α·PL\n路损补偿', 'Δ_TF\nMCS 偏移', 'f 闭环\n（TPC）', 'min{·}\n功率上限']
vals = [-76, 16.99, 72, 1.5, 2, 23]
colors = ['#1c6ab3', '#2e7d32', '#c55a11', '#6b3fa0', '#b22222', '#555']
x = np.arange(len(terms))
ax.bar(x, vals, color=colors, width=0.55)
for i, v in enumerate(vals):
    ax.text(i, v + 2.2, f'{v:+g}' if v != 23 else '23', ha='center', fontsize=10)
ax.set_xticks(x); ax.set_xticklabels(terms, fontsize=9)
ax.set_ylabel('dBm / dB')
ax.set_title('P_PUSCH 公式分解示意（例题 6.1：开环各贡献叠加后受 P_CMAX=23 dBm 上限约束）', fontsize=11)
ax.axhline(23, color='#555', ls='--', lw=1.2)
ax.text(5.35, 25, 'P_CMAX', fontsize=10, color='#555')
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'ufig4.svg'), format='svg')
print('ufig4', os.path.getsize(os.path.join(OUT, 'ufig4.svg')))
