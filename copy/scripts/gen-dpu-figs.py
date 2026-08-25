# -*- coding: utf-8 -*-
"""PDSCH/PUSCH 配图：Mermaid 处理链 ×2 + matplotlib 跳频/分配 ×2"""
import os, subprocess

OUT = r'<用户临时目录>\opencode'
os.environ['PUPPETEER_EXECUTABLE_PATH'] = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
MMDC = r'<用户AppData目录>\npm\mmdc.cmd'

def mmd(name, src):
    p = os.path.join(OUT, name + '.mmd')
    open(p, 'w', encoding='utf-8').write(src)
    r = subprocess.run([MMDC, '-i', p, '-o', os.path.join(OUT, name + '.svg'), '-b', 'white'],
                       capture_output=True, text=True, timeout=180)
    print(name, r.returncode, os.path.getsize(os.path.join(OUT, name + '.svg')))

mmd('dfig1', """flowchart LR
    A["TB（来自 MAC）"] --> B["① TB CRC 24 bit（§7.2.1）"]
    B --> C["② LDPC 基图选择：BG1 / BG2（§7.2.2）"]
    C --> D["③ 码块分段 + CB CRC（§7.2.3）<br/>BG1 最大 8448 / BG2 最大 3840"]
    D --> E["④ QC-LDPC 编码（§7.2.4 / §5.3.2）"]
    E --> F["⑤ 速率匹配（§7.2.5）<br/>按 RV（0→2→3→1）从循环缓冲取 E_r 比特"]
    F --> G["⑥ 码块级联（§7.2.6）"]
    G --> H["⑦ 加扰：c_init = n_RNTI·2^15 + q·2^14 + n_ID"]
    H --> I["⑧ 调制：QPSK / 16QAM / 64QAM / 256QAM"]
    I --> J["⑨ 层映射（≤8 层）→ 预编码 → RE 映射"]
    J --> K["PDSCH RE（绕开 DM-RS / CSI-RS / SSB / 速率匹配图案）"]
""")

mmd('ufig1', """flowchart LR
    A["TB（来自 MAC）"] --> B["① TB CRC 24 bit"]
    B --> C["② BG1 / BG2 选择"]
    C --> D["③ 分段 + CB CRC"]
    D --> E["④ QC-LDPC 编码"]
    E --> F["⑤ RV 速率匹配"]
    F --> G["⑥ 码块级联"]
    G --> H["⑦ 数据与控制（UCI）复用（上行独有）<br/>HARQ-ACK ＞ CSI Part1 ＞ CSI Part2（按 β_offset）"]
    H --> I["⑧ 加扰：c_init = n_RNTI·2^15 + n_ID"]
    I --> J["⑨ 调制（变换预编码时 ≤64QAM / 可 π/2-BPSK）"]
    J --> J1{"变换预编码？"}
    J1 -->|"enabled"| J2["DFT 扩频（DFT-s-OFDM 低峰均比）"]
    J1 -->|"disabled"| J3["CP-OFDM"]
    J2 --> K["⑩ 层映射（≤4 层）→ 预编码 → RE 映射"]
    J3 --> K
    K --> L["PUSCH RE"]
""")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# PDSCH 时域分配示意（默认表 A 行 1：Type A，K0=0，S=2，L=12）
fig, ax = plt.subplots(figsize=(10, 3.2), dpi=150)
ax.add_patch(plt.Rectangle((0, 0.6), 14, 0.35, fc='#f0f0f0', ec='#999'))
ax.add_patch(plt.Rectangle((0, 0.6), 2, 0.35, fc='#b9c9da', ec='#666'))
ax.add_patch(plt.Rectangle((2, 0.6), 2, 0.35, fc='#dce9f5', ec='#0b3d6b'))
ax.add_patch(plt.Rectangle((4, 0.6), 10, 0.35, fc='#a9d08e', ec='#33511f'))
ax.text(1, 0.775, 'PDCCH', ha='center', va='center', fontsize=9, color='#333')
ax.text(3, 0.775, 'DMRS', ha='center', va='center', fontsize=9, color='#0b3d6b')
ax.text(9, 0.775, 'PDSCH（L = 12，S = 2，Type A，K0 = 0）', ha='center', va='center', fontsize=10, color='#33511f')
ax.annotate('', xy=(4, 1.25), xytext=(2, 1.25), arrowprops=dict(arrowstyle='<->', color='#c00000', lw=1.4))
ax.text(3, 1.33, '前载 DM-RS 在符号 2（dmrs-TypeA-Position=pos2）', ha='center', fontsize=9.5, color='#c00000')
ax.set_xlim(0, 14); ax.set_ylim(0.4, 1.7)
ax.set_xticks(np.arange(14) + 0.5)
ax.set_xticklabels([str(i) for i in range(14)], fontsize=8)
ax.set_xlabel('时隙内符号')
ax.axis('off')
ax.set_title('PDSCH 映射类型 A 示意（默认表 A 行 1：K0=0、S=2、L=12；前载 DM-RS 固定在时隙级符号）', fontsize=10.5)
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'dfig2.svg'), format='svg')
print('dfig2', os.path.getsize(os.path.join(OUT, 'dfig2.svg')))

# PUSCH 跳频示意（intraSlot：14 符号两跳）
fig, ax = plt.subplots(figsize=(10, 3.4), dpi=150)
for rb in range(40):
    ax.add_patch(plt.Rectangle((0, rb), 14, 1, fill=False, ec='#eeeeee', lw=0.4))
ax.add_patch(plt.Rectangle((0, 0), 7, 20, fc='#a9d08e', alpha=0.55))
ax.add_patch(plt.Rectangle((7, 20), 7, 20, fc='#9dc3e6', alpha=0.55))
ax.text(3.5, 10, '第一跳\n（N/2 向下取整个 PRB）', ha='center', va='center', fontsize=10, color='#33511f')
ax.text(10.5, 30, '第二跳\n（N−N/2 个 PRB，偏移 RB_offset）', ha='center', va='center', fontsize=10, color='#1a3e6e')
ax.axvline(7, color='#c00000', ls='--', lw=1.3)
ax.text(7, 42.5, '跳频点（intraSlot：前半符号 / 后半符号）', ha='center', fontsize=9.5, color='#c00000')
ax.set_xlim(0, 14); ax.set_ylim(0, 44)
ax.set_xlabel('OFDM 符号')
ax.set_ylabel('RB')
ax.invert_yaxis()
ax.set_title('PUSCH intraSlot 跳频示意：同一时隙内前半符号在第 1 跳、后半符号在第 2 跳（interSlot 则按时隙跳）', fontsize=10.5)
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'ufig2.svg'), format='svg')
print('ufig2', os.path.getsize(os.path.join(OUT, 'ufig2.svg')))
