# -*- coding: utf-8 -*-
"""SRS 配图：Mermaid 四大用途 + 触发流程；matplotlib 梳齿映射"""
import os, subprocess

OUT = r'<用户临时目录>\opencode'
os.environ['PUPPETEER_EXECUTABLE_PATH'] = r'<Chrome目录>\chrome.exe'
MMDC = r'<用户AppData目录>\npm\mmdc.cmd'

def mmd(name, src):
    p = os.path.join(OUT, name + '.mmd')
    open(p, 'w', encoding='utf-8').write(src)
    r = subprocess.run([MMDC, '-i', p, '-o', os.path.join(OUT, name + '.svg'), '-b', 'white'],
                       capture_output=True, text=True, timeout=180)
    print(name, r.returncode, os.path.getsize(os.path.join(OUT, name + '.svg')))

mmd('srsfig1', """flowchart TD
    S["SRS（Sounding Reference Signal）<br/>UE 发给 gNB 的上行探测信号"] --> U{"usage = ?（资源集级）"}
    U -->|"beamManagement"| B["上行波束管理<br/>UE 多波束轮发 → gNB 选最优上行波束<br/>（TDD 互易性推导下行波束）"]
    U -->|"codebook"| C["码本上行预编码<br/>gNB 测上行信道 → 选 TPMI/RI<br/>（DCI 0_1 指示，SRI 选资源）"]
    U -->|"nonCodebook"| N["非码本上行预编码<br/>UE 按关联 CSI-RS 自算预编码<br/>（SRI 选层组合，≤4 资源）"]
    U -->|"antennaSwitching"| A["天线切换探测（1T2R/2T4R/1T4R…）<br/>少发射链探测全接收天线<br/>→ 下行 CSI 获取（互易性）+ Y 保护期"]
    B --> G["gNB 应用：链路自适应 / 预编码 / 波束管理"]
    C --> G
    N --> G
    A --> G
""")

mmd('srsfig3', """flowchart TD
    A{"resourceType = ?（资源级）"}
    A -->|"periodic"| P1["RRC 配置即周期发送<br/>periodicityAndOffset-p（sl1~sl2560）<br/>spatialRelationInfo 静态给出"]
    A -->|"semi-persistent"| P2["MAC CE 激活（38.321 §6.1.3.17）<br/>n+3N_slot+1 生效<br/>激活命令可覆盖空间关系"]
    A -->|"aperiodic"| P3["DCI SRS request 字段触发<br/>（0_1/1_1/2_3 的 2 bit）<br/>码点 → aperiodicSRS-ResourceTrigger 1/2/3<br/>slotOffset 定发送时隙<br/>codebook/antennaSwitching：N2<br/>其他：N2+14"]
    P1 --> E["UE 按配置周期/触发发送 SRS"]
    P2 --> E
    P3 --> E
""")

# matplotlib：SRS 梳齿与 CS 复用示意
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(10, 5.0), dpi=150)
# 网格：24 子载波（2 PRB）× 14 符号
for s in range(14):
    for k in range(24):
        ax.add_patch(plt.Rectangle((s, k), 1, 1, fill=False, ec='#eeeeee', lw=0.4))
# comb-2 UE A：offset 0（子载波 0,2,4,...），符号 13
for k in range(0, 24, 2):
    ax.scatter(13.5, k + 0.5, s=110, color='#1c6ab3', zorder=5, marker='s')
# comb-2 UE B：offset 1（子载波 1,3,5,...），符号 13
for k in range(1, 24, 2):
    ax.scatter(13.5, k + 0.5, s=110, color='#2e7d32', zorder=5, marker='o')
# comb-4 UE C：offset 2（子载波 2,6,10,...），符号 12
for k in range(2, 24, 4):
    ax.scatter(12.5, k + 0.5, s=110, color='#c55a11', zorder=5, marker='^')
# 图例与标注
ax.text(13.5, 25.2, 'UE A：comb-2，offset 0，CS 组 8 个', ha='center', fontsize=10, color='#1c6ab3')
ax.text(13.5, 24.4, 'UE B：comb-2，offset 1（与 A 频域正交）', ha='center', fontsize=10, color='#2e7d32')
ax.text(12.5, 24.4 - 0.8, 'UE C：comb-4，offset 2（CS 组 12 个）', ha='center', fontsize=10, color='#c55a11')
ax.annotate('同一梳齿内：不同 UE/端口用循环移位区分（comb-2 可 8 个、comb-4 可 12 个）',
            xy=(13.5, 0.5), xytext=(3, 26.4), fontsize=10.5, color='#555',
            arrowprops=dict(arrowstyle='-', linestyle='--', color='#888'))
ax.annotate('SRS 仅在时隙最后 6 个符号（startPosition 0~5）',
            xy=(13.5, 12), xytext=(7.5, 27.2), fontsize=10.5, color='#555',
            arrowprops=dict(arrowstyle='-', linestyle='--', color='#888'))
ax.set_xticks(np.arange(14) + 0.5)
ax.set_xticklabels([str(i) for i in range(14)], fontsize=8)
ax.set_yticks(np.arange(24) + 0.5)
ax.set_yticklabels([str(i) for i in range(24)], fontsize=8)
ax.set_xlim(0, 14)
ax.set_ylim(0, 28)
ax.invert_yaxis()
ax.set_xlabel('OFDM 符号（时隙内，右端 = 时隙末尾）')
ax.set_ylabel('子载波（PRB 内）')
ax.set_title('SRS 梳齿复用示意（2 个 PRB 局部）：comb 决定频域隔点位置、CS 决定同梳齿内的码域区分', fontsize=10.5)
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'srsfig2.svg'), format='svg')
print('srsfig2', os.path.getsize(os.path.join(OUT, 'srsfig2.svg')))
