# -*- coding: utf-8 -*-
"""新工具实战：Mermaid 重画图8（按需SI双路径）、matplotlib 重画图2（SSB块图）"""
import subprocess, os

OUT = r'C:\Users\job_p\AppData\Local\Temp\opencode'
os.environ['PUPPETEER_EXECUTABLE_PATH'] = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
MMDC = r'C:\Users\job_p\AppData\Roaming\npm\mmdc.cmd'

# ---------------- 图 8：Mermaid flowchart ----------------
mmd8 = """flowchart TD
    A["UE 需要 si-BroadcastStatus = notBroadcasting 的 SI 消息"] --> B{"SIB1 是否配置了<br/>si-RequestConfig（或 SUL 版）？"}
    B -->|"是（Msg1 方式）"| C1["① 选 SSB（RSRP 超过 rsrp-ThresholdSSB），<br/>发专用前导（ra-PreambleStartIndex + i）"]
    B -->|"否（Msg3 方式）"| D1["① Msg1：公共前导 → RAR<br/>（RAPID + TA + UL grant）"]
    C1 --> C2["② gNB 回 RAR：只含 RAPID 的 MAC subPDU<br/>→ 视为 SI 请求 ACK（38.321 §5.1.4）"]
    C2 --> C3["③ 立即进入该 SI 消息的下一个窗口<br/>盲检 SI-RNTI 接收（§5.2.2.3.2）"]
    D1 --> D2["② Msg3：RRCSystemInfoRequest<br/>（CCCH / SRB0 / TM，requested-SI-List）"]
    D2 --> D3["③ Msg4：冲突解决成功（TC-RNTI）<br/>→ 视为 SI 请求 ACK（38.321 §5.1.5）"]
    D3 --> D4["④ 立即进入窗口接收请求的 SI 消息"]
    C3 --> E["网络在 SI 窗口内临时广播<br/>（至修改周期末）；重选时重置 MAC"]
    D4 --> E
"""
with open(os.path.join(OUT, 'fig8.mmd'), 'w', encoding='utf-8') as f:
    f.write(mmd8)
r = subprocess.run([MMDC, '-i', os.path.join(OUT, 'fig8.mmd'), '-o', os.path.join(OUT, 'fig8-new.svg'), '-b', 'white'],
                   capture_output=True, text=True, timeout=180)
print('mmdc fig8:', r.returncode, (r.stderr or r.stdout).splitlines()[-1] if (r.stderr or r.stdout) else '')
sz = os.path.getsize(os.path.join(OUT, 'fig8-new.svg')) if os.path.exists(os.path.join(OUT, 'fig8-new.svg')) else 0
print('fig8-new.svg 大小:', sz)

# ---------------- 图 2：matplotlib SSB 块图 ----------------
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(11, 4.6), dpi=150)
grid = np.zeros((4, 240), dtype=int)
grid[0, 56:183] = 1      # PSS
grid[2, 56:183] = 2      # SSS
grid[1, :] = 3; grid[3, :] = 3    # PBCH 符号1/3
grid[2, 0:48] = 3; grid[2, 192:240] = 3   # PBCH 符号2 两侧
grid[0, 0:56] = 4; grid[0, 183:240] = 4   # 置0
grid[2, 48:56] = 4; grid[2, 183:192] = 4

from matplotlib.colors import ListedColormap
cmap_main = ListedColormap(['#f4b183', '#9dc3e6', '#a9d08e'])
main = np.ma.masked_where(grid == 4, grid)
ax.pcolormesh(np.arange(241), np.arange(5), main, cmap=cmap_main, vmin=1, vmax=3, shading='flat')
zero = np.ma.masked_where(grid != 4, grid)
ax.pcolormesh(np.arange(241), np.arange(5), zero, cmap=ListedColormap(['#e0e0e0']), vmin=1, vmax=1, shading='flat')

# DM-RS（v = 0 示意）
for sym in (1, 3):
    ks = np.arange(0, 240, 4)
    ax.scatter(ks + 0.5, np.full_like(ks, 3 - sym + 0.5), color='#c00000', s=4, zorder=5)
ks2 = np.concatenate([np.arange(0, 48, 4), np.arange(192, 240, 4)])
ax.scatter(ks2 + 0.5, np.full_like(ks2, 1.5), color='#c00000', s=4, zorder=5)

# 标注
ax.text(119.5, 3.5, 'PSS（127 子载波）', ha='center', va='center', fontsize=11, color='#7a3c00', fontweight='bold')
ax.text(119.5, 1.5, 'SSS（127 子载波）', ha='center', va='center', fontsize=11, color='#1a3e6e', fontweight='bold')
ax.text(240.5, 3.5, 'PBCH', ha='center', va='center', fontsize=10, color='#33511f')
ax.text(240.5, 0.5, 'PBCH', ha='center', va='center', fontsize=10, color='#33511f')
ax.text(24, 1.5, 'PBCH', ha='center', va='center', fontsize=9, color='#33511f')
ax.text(216, 1.5, 'PBCH', ha='center', va='center', fontsize=9, color='#33511f')

ax.set_yticks([0.5, 1.5, 2.5, 3.5])
ax.set_yticklabels(['0', '1', '2', '3'])
ax.set_ylabel('OFDM 符号号')
ax.set_xlabel('子载波号（SSB 块内 0~239）')
ax.set_xticks([0, 48, 56, 182, 192, 239])
ax.set_xlim(0, 240); ax.set_ylim(0, 4)
ax.invert_yaxis()
ax.set_title('SSB 时频结构（4 符号 × 240 子载波；橙 = PSS，蓝 = SSS，绿 = PBCH，红点 = PBCH DM-RS（每 4 子载波 1 个，v = $N_{ID}^{cell}$ mod 4），灰 = 置 0）',
             fontsize=10.5)
for spine in ['top', 'right']:
    ax.spines[spine].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(OUT, 'fig2-new.svg'), format='svg')
print('fig2-new.svg 大小:', os.path.getsize(os.path.join(OUT, 'fig2-new.svg')))
