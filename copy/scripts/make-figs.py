# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

# ---------- 图1：PUCCH 五种格式时频结构 ----------
fig, axes = plt.subplots(1, 5, figsize=(15.5, 4.6), sharey=False)
titles = ["format 0\n≤2 bit · 1~2 符号\nCS 序列选择", "format 1\n≤2 bit · 4~14 符号\nBPSK/QPSK + 时域 OCC",
          "format 2\n>2 bit · 1~2 符号\nQPSK + DM-RS", "format 3\n>2 bit · 4~14 符号\n多 PRB 无 OCC",
          "format 4\n>2 bit · 4~14 符号\n1 PRB + 时域 OCC"]
syms = [2, 14, 2, 14, 14]
prbs = [1, 1, 8, 4, 1]
for ax, ti, ns, nr in zip(axes, titles, syms, prbs):
    grid = np.zeros((nr * 3, ns + 1))
    # 频域 PRB 行
    for b in range(nr):
        for s in range(ns):
            col = s % 4
            if col == 0:
                v = 0.55
            elif col == 1:
                v = 0.85
            elif col == 2:
                v = 1.0
            else:
                v = 0.7
            grid[b * 3:(b + 1) * 3, s] = v
    grid[:, -1] = 0.3
    cm = plt.get_cmap("YlOrBr")
    ax.imshow(grid, aspect="auto", cmap=cm, vmin=0, vmax=1.2)
    ax.set_title(ti, fontsize=10.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("时域符号 →", fontsize=9)
fig.suptitle("PUCCH 五种格式的时频资源示意（色块=RE，深色=DM-RS 位置、浅色=UCI）", fontsize=12.5, y=1.02)
fig.tight_layout()
fig.savefig(r"<用户临时目录>\opencode\pucch-formats.svg", bbox_inches="tight")
plt.close(fig)

# ---------- 图2：ZC 根序列循环移位滚出多个前导 ----------
fig, ax = plt.subplots(figsize=(12.5, 4.2))
L = 32
i = np.arange(L)
root = np.exp(-1j * np.pi * 3 * i * (i + 1) / L)
for v in range(4):
    shift = v * 5
    sig = np.roll(root, shift)
    ax.plot(i + 0.05 * v, sig.real + 0.35 * v, lw=1.6, label=f"前导 v={v}（C_v={shift}）")
ax.plot(i, np.roll(root, 0).real - 0.5, lw=1.2, color="gray", ls="--", label="根序列 x_u(i)")
ax.set_xlabel("样点索引 n（同轴展示，v 越大曲线越靠上）")
ax.set_ylabel("序列实部（上移区分）")
ax.set_title("ZC 根序列经循环移位 C_v = v·N_CS 生成多个前导（示意 N_CS=5）", fontsize=12.5)
ax.legend(fontsize=9.5, loc="upper right")
ax.set_ylim(-0.85, 1.8)
fig.tight_layout()
fig.savefig(r"<用户临时目录>\opencode\ra-zc.svg", bbox_inches="tight")
plt.close(fig)

# ---------- 图3：SSB → RO → 前导 映射网格 ----------
fig, ax = plt.subplots(figsize=(12.5, 4.8))
# 4 个 RO × 频域 2（示例：每 SSB 16 前导、8 SSB、每 RO 64 前导）
ssbs = 8
for s in range(ssbs):
    ro_col = (s % 4)
    ro_row = (s // 4) % 2
    x = 1.6 * ro_col
    y = 2.0 * ro_row
    ax.add_patch(plt.Rectangle((x, y), 1.4, 0.95, fill=True, facecolor=plt.cm.Set3(s / 8), edgecolor="k", lw=1.2))
    ax.text(x + 0.7, y + 0.62, f"SSB#{s}", ha="center", va="center", fontsize=10.5, fontweight="bold")
    ax.text(x + 0.7, y + 0.3, f"前导 {16*s}~{16*s+15}", ha="center", va="center", fontsize=9)
ax.text(1.55, -1.15, "RO#0（频域 f_id=0）", ha="center", fontsize=10)
ax.text(3.15, -1.15, "RO#1（f_id=0）", ha="center", fontsize=10)
ax.text(4.75, -1.15, "RO#2（f_id=1）", ha="center", fontsize=10)
ax.text(6.35, -1.15, "RO#3（f_id=1）", ha="center", fontsize=10)
ax.text(-0.1, 2.5, "t_id 递增", rotation=0, fontsize=10)
ax.set_xlim(-0.6, 7.0)
ax.set_ylim(-1.6, 3.6)
ax.axis("off")
ax.set_title("SSB 到 PRACH 时机（RO）与前导段的映射示意：ssb-perRO=oneFourth、每 SSB 16 个 CB 前导、msg1-FDM=2", fontsize=12.5)
fig.tight_layout()
fig.savefig(r"<用户临时目录>\opencode\ra-map.svg", bbox_inches="tight")
plt.close(fig)

print("3 matplotlib SVGs done")
