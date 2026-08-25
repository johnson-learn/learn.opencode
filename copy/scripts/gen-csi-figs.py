# -*- coding: utf-8 -*-
"""CSI 专题配图：Mermaid ×3 + matplotlib ×2"""
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

# 图1：CSI 三层框架
mmd('csifig1', """flowchart TD
    subgraph RC["CSI-MeasConfig（RRC，挂在 ServingCellConfig.csi-MeasConfig）"]
        P1["资源池：NZP-CSI-RS-Resource / CSI-IM-Resource / SSB 集"]
        P2["CSI-ResourceConfig（M 个）：用途 × resourceType × bwp-Id"]
        P3["CSI-ReportConfig（N 个）：reportQuantity × reportConfigType × 频域粒度 × codebookConfig"]
        P4["触发状态列表：AperiodicTriggerStateList / SP-on-PUSCH-TriggerStateList"]
    end
    P2 -->|"resourcesForChannelMeasurement / csi-IM-ResourcesForInterference / nzp-CSI-RS-ResourcesForInterference"| P3
    P4 -->|"DCI CSI request 映射"| P3
    P1 --> P2
    P3 --> R["UE 上报：CQI / PMI / RI / LI / CRI / SSBRI / L1-RSRP"]
    D["DCI 0_1（CSI request 字段）"] -->|"触发/激活"| P4
    M["MAC CE（38.321）"] -->|"SP 上报与 SP 资源激活 / 触发状态子选"| P4
""")

# 图3：三种上报类型触发流程
mmd('csifig3', """flowchart TD
    A{"reportConfigType = ?"} 
    A -->|"periodic"| B1["RRC 配置即激活<br/>PUCCH format 2/3/4，Type I 宽带<br/>周期 ≥ 4 槽（reportSlotConfig）"]
    A -->|"semiPersistentOnPUCCH"| B2["MAC CE 激活（38.321）<br/>n+3N_slot+1 生效；再收 MAC CE 去激活"]
    A -->|"semiPersistentOnPUSCH"| B3["SP-CSI-RNTI DCI 激活<br/>（HARQ 全 0 + RV=00 验证）<br/>释放：MCS 全 1 + RV=00<br/>BWP 切换自动去激活"]
    A -->|"aperiodic"| B4["DCI 0_1 的 CSI request 字段触发<br/>全 0 = 不请求<br/>状态多时先 MAC CE 子选映射<br/>PUSCH 承载（Part 1 + Part 2）"]
    B1 --> E["对应资源：periodic CSI-RS（RRC 静态）"]
    B2 --> F["对应资源：periodic 或 SP CSI-RS"]
    B3 --> F
    B4 --> G["对应资源：periodic / SP / aperiodic 均可"]
""")

# 图5：aperiodic CSI 端到端
mmd('csifig5', """flowchart TD
    S1["① RRC：csi-MeasConfig 配置<br/>（资源 / 资源集 / ResourceConfig / ReportConfig / 触发状态）"] --> S2["② periodic CSI-RS 按周期广播<br/>（(N_slot·n_f+n_s−T_off) mod T = 0）"]
    S2 --> S3["③ DCI 0_1：CSI request 非零码点<br/>→ 映射触发状态（含 TCI 列表）"]
    S3 --> S4["④ aperiodic CSI-RS 发送<br/>（aperiodicTriggeringOffset 0~4/16/24 槽）"]
    S4 --> S5["⑤ UE 测量：NZP CSI-RS 量信道、CSI-IM 量干扰"]
    S5 --> S6["⑥ CSI 计算：CRI→RI→PMI→CQI→LI<br/>（依赖链 + 码本子集限制 + 参考资源假设）"]
    S6 --> S7{"⑦ 时延校验：<br/>PUSCH 起点 ≥ Z_ref 且 ≥ Z′_ref？"}
    S7 -->|"否"| S7a["忽略 DCI（无 TB 复用）<br/>或不更新该上报"]
    S7 -->|"是"| S8["⑧ 编码：Part 1（RI/CRI/CQI1）→ Part 2（PMI/CQI2）<br/>资源不足按优先级省略"]
    S8 --> S9["⑨ gNB：RI 定层、PMI 定预编码、CQI 选 MCS、<br/>L1-RSRP/CRI 做波束管理"]
""")

# 图2：matplotlib CSI-RS 资源映射（Row 4：4 端口 FD-CDM2，密度1）
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(10, 5.2), dpi=150)
# 网格：2 PRB × 14 符号
for r in range(2):
    for s in range(14):
        ax.add_patch(plt.Rectangle((s, r*12), 1, 12, fill=False, ec='#cccccc', lw=0.5))
# Row 4：4 端口 FD-CDM2，位置 (k0,l0) 与 (k0+2,l0)，k0=0 取子载波 0 和 2；l0=5 示例
k0, l0 = 0, 5
xs = [l0, l0]
ys = [k0, k0+2]
ax.scatter([x+0.5 for x in xs], [y+0.5 for y in ys], s=260, color='#1c6ab3', zorder=5, marker='s')
for i, (x, y) in enumerate(zip(xs, ys)):
    ax.text(x+0.5, y+1.1, f'CDM 组 {i}', ha='center', fontsize=9, color='#1c6ab3')
    ax.text(x+0.5, y-0.9, f'(k={k0+2*i}, l={l0})', ha='center', fontsize=8.5, color='#666')
# FD-CDM2 OCC 说明
ax.annotate('同一 CDM 组 2 个端口共用 RE\n端口 3000：w_f=[+1,+1]\n端口 3001：w_f=[+1,−1]',
            xy=(l0+0.5, k0+0.5), xytext=(l0+6, k0+4),
            fontsize=9.5, color='#7a3c00',
            arrowprops=dict(arrowstyle='-', linestyle='--', color='#888'))
# PRB 标注
ax.set_xticks(np.arange(14)+0.5); ax.set_xticklabels([str(i) for i in range(14)], fontsize=8)
ax.set_yticks(np.arange(24)+0.5); ax.set_yticklabels([str(i) for i in range(24)], fontsize=8)
ax.set_xlim(0, 14); ax.set_ylim(0, 24)
ax.set_xlabel('OFDM 符号（l，时隙内）'); ax.set_ylabel('子载波（k，PRB 内）')
ax.set_title('CSI-RS 资源映射示意（Table 7.4.1.5.3-1 Row 4：4 端口、密度 \u03c1=1、FD-CDM2；$k_0$ 由 frequencyDomainAllocation 位图确定，$l_0$ 由 firstOFDMSymbolInTimeDomain 确定；跨每 1/\u03c1 个 PRB 重复）', fontsize=10)
ax.invert_yaxis()
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'csifig2.svg'), format='svg')
print('csifig2', os.path.getsize(os.path.join(OUT, 'csifig2.svg')))

# 图4：matplotlib Z/Z′ 时延时序
fig, ax = plt.subplots(figsize=(10, 3.6), dpi=150)
ax.add_patch(plt.Rectangle((0, 0.55), 3, 0.3, fc='#dce9f5', ec='#0b3d6b'))
ax.text(1.5, 0.7, 'PDCCH（触发 DCI，CSI request 非零）', ha='center', va='center', fontsize=10, color='#0b3d6b')
ax.add_patch(plt.Rectangle((4, 0.55), 3, 0.3, fc='#fde8c8', ec='#7a4a00'))
ax.text(5.5, 0.7, 'aperiodic CSI-RS / CSI-IM（触发偏移后）', ha='center', va='center', fontsize=10, color='#7a4a00')
ax.add_patch(plt.Rectangle((13, 0.55), 4, 0.3, fc='#e3f0e3', ec='#1b5e20'))
ax.text(15, 0.7, 'PUSCH（CSI Part 1 + Part 2）', ha='center', va='center', fontsize=10, color='#1b5e20')
# Z：PDCCH 末 → PUSCH 首
ax.annotate('', xy=(13, 1.5), xytext=(3, 1.5), arrowprops=dict(arrowstyle='<->', color='#c00000', lw=1.6))
ax.text(8, 1.62, 'Z 符号（表 5.4-1/5.4-2，从触发 PDCCH 最后一个符号之后起算）', ha='center', fontsize=10, color='#c00000')
# Z′：CSI-RS 末 → PUSCH 首
ax.annotate('', xy=(13, 2.35), xytext=(7, 2.35), arrowprops=dict(arrowstyle='<->', color='#6b3fa0', lw=1.6))
ax.text(10, 2.47, "Z′ 符号（从最后测量资源末起算）", ha='center', fontsize=10, color='#6b3fa0')
ax.set_xlim(-0.5, 18.5); ax.set_ylim(0.3, 2.9)
ax.axis('off')
ax.set_title('CSI 计算时延 Z / Z′：两个条件必须同时满足（38.214 §5.4）', fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'csifig4.svg'), format='svg')
print('csifig4', os.path.getsize(os.path.join(OUT, 'csifig4.svg')))
