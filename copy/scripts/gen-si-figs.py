# -*- coding: utf-8 -*-
"""生成系统消息专题 SVG 示意图（9 张，v2：错位修复 + tspan 上下标 + 字号适配）"""
import os

OUT = r"<用户临时目录>\opencode\si-figs"
os.makedirs(OUT, exist_ok=True)

def txt(x, y, s, size=13, color="#1a1a1a", anchor="start", bold=False, rot=None):
    w = ' font-weight="bold"' if bold else ''
    r = f' transform="rotate({rot} {x} {y})"' if rot else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}"{w}{r}>{s}</text>'

def rect(x, y, w, h, fill, stroke="#444", sw=1.2, rx=4):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}"/>'

def line(x1, y1, x2, y2, color="#444", sw=1.2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{d}/>'

def arrow(x1, y1, x2, y2, color="#1b5e20", sw=1.6):
    import math
    m = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"/>'
    a = math.atan2(y2-y1, x2-x1)
    L = 9
    x3 = x2 - L*math.cos(a-0.42); y3 = y2 - L*math.sin(a-0.42)
    x4 = x2 - L*math.cos(a+0.42); y4 = y2 - L*math.sin(a+0.42)
    h = f'<polygon points="{x2},{y2} {x3:.1f},{y3:.1f} {x4:.1f},{y4:.1f}" fill="{color}"/>'
    return m + h

def fig_wrap(figid, caption, svg, w, h):
    return (f'<figure style="margin:18px 0; text-align:center;">\n'
            f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="max-width:100%; height:auto; background:#fff; border:1px solid #bbb;">{svg}</svg>\n'
            f'<figcaption style="font-size:13px; color:#555; margin-top:6px;"><b>{figid}</b> {caption}</figcaption>\n</figure>\n')

frags = {}

# ---------------- 图 1：三级递进流程 ----------------
W, H = 800, 300
s = ''
s += rect(20, 70, 170, 92, '#fde8c8')
s += txt(105, 92, 'SSB（同步信号块）', 15, '#7a4a00', 'middle', True)
s += txt(105, 114, 'PSS/SSS：PCI、帧边界', 12)
s += txt(105, 132, 'PBCH DM-RS：SSB 索引低位', 12)
s += txt(105, 150, 'PBCH：MIB', 12)
s += rect(250, 70, 170, 92, '#dce9f5')
s += txt(335, 92, 'MIB', 15, '#0b3d6b', 'middle', True)
s += txt(335, 114, 'pdcch-ConfigSIB1 查表', 12)
s += txt(335, 132, 'k<tspan baseline-shift="sub">SSB</tspan>、SCS、DM-RS 位置', 12)
s += txt(335, 150, 'cellBarred', 12)
s += rect(480, 70, 170, 92, '#e3f0e3')
s += txt(565, 92, 'SIB1', 15, '#1b5e20', 'middle', True)
s += txt(565, 114, 'servingCellConfigCommon', 12)
s += txt(565, 132, 'si-SchedulingInfo', 12)
s += txt(565, 150, '驻留、接入参数', 12)
s += rect(300, 224, 200, 62, '#f0f0f0')
s += txt(400, 248, 'SI 消息', 15, '#333', 'middle', True)
s += txt(400, 268, 'SIB2~SIB9（同周期打包）', 12)
s += txt(400, 286, 'SI-RNTI 调度', 12)
s += arrow(190, 116, 250, 116)
s += arrow(420, 116, 480, 116)
s += line(565, 162, 565, 194, '#1b5e20', 1.6)
s += line(565, 194, 400, 194, '#1b5e20', 1.6)
s += arrow(400, 194, 400, 224, '#1b5e20')
# 顶部注释（错行）
s += txt(335, 44, 'CORESET#0/SS#0 查表（38.213 Table 13-x）', 12, '#666', 'middle')
s += line(335, 50, 335, 70, '#888', 1, '3,3')
s += txt(565, 30, 'si-SchedulingInfo 配置每个', 12, '#666', 'middle')
s += txt(565, 46, 'SI 消息的窗口与周期', 12, '#666', 'middle')
s += line(565, 52, 565, 70, '#888', 1, '3,3')
frags['fig1'] = fig_wrap('图 1', '系统消息逐级递进：SSB → MIB → SIB1 → SI 消息（全部经 BCCH 广播，但调度信息层层递进）', s, W, H)

# ---------------- 图 2：SSB 时频结构块图 ----------------
W, H = 800, 450
px = 90
sc = 2.4
sy0 = 70
sh = 62
gx = lambda k: px + k*sc
s = ''
s += line(px, sy0, px, sy0+4*sh, '#333', 1.6)
s += line(gx(240), sy0, gx(240), sy0+4*sh, '#333', 1.6)
s += line(px, sy0, gx(240), sy0, '#333', 1.6)
s += line(px, sy0+4*sh, gx(240), sy0+4*sh, '#333', 1.6)
for sym in range(4):
    y = sy0 + sym*sh
    s += line(px, y+sh, gx(240), y+sh, '#999', 0.7)
    if sym == 0:
        s += rect(gx(56), y, gx(182)-gx(56), sh, '#f4b183')
        s += rect(px, y, gx(56)-px, sh, '#e0e0e0')
        s += rect(gx(183), y, gx(240)-gx(183), sh, '#e0e0e0')
        s += txt(gx(56)+(gx(182)-gx(56))/2, y+sh/2+4, 'PSS（127 子载波）', 12, '#7a3c00', 'middle', True)
    elif sym == 2:
        s += rect(px, y, gx(48)-px, sh, '#a9d08e')
        s += rect(gx(48), y, gx(56)-gx(48), sh, '#e0e0e0')
        s += rect(gx(56), y, gx(182)-gx(56), sh, '#9dc3e6')
        s += rect(gx(183), y, gx(192)-gx(183), sh, '#e0e0e0')
        s += rect(gx(192), y, gx(240)-gx(192), sh, '#a9d08e')
        s += txt(gx(56)+(gx(182)-gx(56))/2, y+sh/2+4, 'SSS（127 子载波）', 12, '#1a3e6e', 'middle', True)
        s += txt(gx(24), y+sh/2+4, 'PBCH', 11, '#33511f', 'middle')
        s += txt(gx(216), y+sh/2+4, 'PBCH', 11, '#33511f', 'middle')
        for k in list(range(0, 48, 4)) + list(range(192, 240, 4)):
            s += rect(gx(k)+0.8*sc, y+3, sc*0.9, sh-6, '#c00000', None, 0)
    else:
        s += rect(px, y, gx(240)-px, sh, '#a9d08e')
        s += txt(px+6, y+sh/2+4, 'PBCH', 11, '#33511f', 'middle')
        for k in range(0, 240, 4):
            s += rect(gx(k)+0.8*sc, y+3, sc*0.9, sh-6, '#c00000', None, 0)
    s += txt(px-10, y+sh/2+4, str(sym), 13, '#333', 'end', True)
s += txt(px-22, sy0-12, '符号', 12, '#333', 'end')
marks = [(0,0),(48,1),(56,0),(182,1),(192,0),(239,1)]
for k, lv in marks:
    x = gx(k)
    s += line(x, sy0, x, sy0-8, '#555', 1)
    s += txt(x, sy0-14-lv*14, str(k), 12, '#333', 'middle')
s += line(gx(0), sy0-40, gx(240), sy0-40, '#555', 1)
s += line(gx(0), sy0-46, gx(0), sy0-34, '#555', 1); s += line(gx(240), sy0-46, gx(240), sy0-34, '#555', 1)
s += txt((gx(0)+gx(240))/2, sy0-46, '240 个子载波（20 个 RB）', 12, '#333', 'middle')
s += line(px-34, sy0, px-34, sy0+4*sh, '#555', 1)
s += line(px-40, sy0, px-28, sy0, '#555', 1); s += line(px-40, sy0+4*sh, px-28, sy0+4*sh, '#555', 1)
s += txt(px-44, sy0+2*sh+4, '4 个 OFDM 符号', 12, '#333', 'middle', True, -90)
# 图例（两行）
ly1 = sy0+4*sh+32
s += rect(px, ly1, 16, 12, '#f4b183'); s += txt(px+22, ly1+10, 'PSS', 12)
s += rect(px+80, ly1, 16, 12, '#9dc3e6'); s += txt(px+102, ly1+10, 'SSS', 12)
s += rect(px+160, ly1, 16, 12, '#a9d08e'); s += txt(px+182, ly1+10, 'PBCH', 12)
s += rect(px+240, ly1, 16, 12, '#c00000'); s += txt(px+262, ly1+10, 'PBCH DM-RS（每 4 子载波 1 个）', 12)
s += rect(px+560, ly1, 16, 12, '#e0e0e0'); s += txt(px+582, ly1+10, '置 0', 12)
ly2 = ly1 + 26
s += txt(px, ly2+2, 'v = N<tspan baseline-shift="sub">ID</tspan><tspan baseline-shift="super">cell</tspan> mod 4（DM-RS 频移）。符号 1/3 的 PBCH 为全带宽；符号 2 的 PBCH 分居 SSS 两侧（0~47 与 192~239）。', 11.5, '#555')
s += txt(px, ly2+18, 'DM-RS 共 144 RE → PBCH 数据 RE = 576 − 144 = 432（QPSK → 864 bit）', 11.5, '#555')
frags['fig2'] = fig_wrap('图 2', 'SSB 时频结构块图（Table 7.4.3.1-1 的可视化：4 符号 × 240 子载波，PSS/SSS 各占符号 0/2 的中间 127 子载波，\(v=N_{ID}^{cell}\bmod 4\)）', s, W, H)

# ---------------- 图 3：Point A / k_SSB 频域关系 ----------------
W, H = 800, 470
s = ''
s += txt(30, 26, '公共资源块网格（信道栅格）', 13, '#333', 'start', True)
s += line(30, 70, 770, 70, '#0b3d6b', 2)
s += txt(36, 90, 'Point A（公共资源块 0 的子载波 0）', 13, '#0b3d6b', 'start', True)
xpa = 120
rbw = 84
s += line(xpa, 52, xpa, 88, '#888', 1)
xcrb = 414
s += line(xcrb, 52, xcrb, 88, '#888', 1)
s += line(xpa, 44, xcrb, 44, '#555', 1.3)
s += line(xpa, 38, xpa, 50, '#555', 1.3); s += line(xcrb, 38, xcrb, 50, '#555', 1.3)
s += txt((xpa+xcrb)/2, 62, 'offsetToPointA（高层参数，单位 RB，按 15 kHz SCS 计）', 11.5, '#555', 'middle')
for i, lab in enumerate(['CRB N−1', 'CRB N', 'CRB N+1']):
    x = xcrb - rbw + i*rbw
    s += rect(x, 104, rbw, 70, '#f5f8fc')
    s += line(x, 104, x+rbw, 174, '#c9d6e5', 0.8)
    s += txt(x+rbw/2, 124, lab, 11.5, '#333', 'middle', True)
    for k in range(1, 12):
        s += line(x + k*rbw/12, 116, x + k*rbw/12, 162, '#c9d6e5', 0.5)
s += txt(xcrb, 190, 'SSB 起点所在 CRB（其子载波 0 即 k<tspan baseline-shift="sub">SSB</tspan> 的参考点，N = N<tspan baseline-shift="sub">CRB</tspan><tspan baseline-shift="super">SSB</tspan>）', 11, '#666', 'middle')
kssb = 14
scpx = 7.0
xs = xcrb + kssb*scpx
s += line(xcrb, 174, xcrb, 208, '#888', 1, '4,4')
s += line(xs, 208, xs, 220, '#888', 1, '4,4')
s += line(xcrb, 208, xs, 208, '#c00000', 1.3)
s += line(xcrb, 202, xcrb, 214, '#c00000', 1.3); s += line(xs, 202, xs, 214, '#c00000', 1.3)
s += txt((xcrb+xs)/2, 224, 'k<tspan baseline-shift="sub">SSB</tspan> = 14', 11.5, '#c00000', 'middle', True)
y_ssb = 250
ssbw = 250
s += rect(xs, y_ssb, ssbw, 78, '#fff3d6', '#7a4a00', 1.6)
s += rect(xs, y_ssb+14, ssbw*0.35, 50, '#f4b183'); s += txt(xs+ssbw*0.175, y_ssb+42, 'PSS', 12, '#7a3c00', 'middle', True)
s += rect(xs+ssbw*0.35, y_ssb+14, ssbw*0.3, 50, '#9dc3e6'); s += txt(xs+ssbw*0.5, y_ssb+42, 'SSS', 12, '#1a3e6e', 'middle', True)
s += rect(xs+ssbw*0.65, y_ssb+14, ssbw*0.35, 50, '#a9d08e'); s += txt(xs+ssbw*0.825, y_ssb+42, 'PBCH', 12, '#33511f', 'middle', True)
s += txt(xs+ssbw/2, y_ssb-10, 'SSB（20 RB = 240 子载波，非比例示意）', 11.5, '#333', 'middle', True)
s += txt(556, 352, 'SSB 中心落在同步栅格（GSCN）上', 12, '#555')
s += txt(556, 372, '与 RB 栅格错位 k<tspan baseline-shift="sub">SSB</tspan> 个子载波', 12, '#555')
s += line(610, 262, 552, 348, '#888', 1, '3,3')
s += txt(60, 392, 'k<tspan baseline-shift="sub">SSB</tspan> 低 4 bit：MIB 的 ssb-SubcarrierOffset（0~15）', 11.5, '#c00000')
s += txt(60, 410, 'k<tspan baseline-shift="sub">SSB</tspan> 最高位（type A）：PBCH 载荷 a<tspan baseline-shift="sub">Ā+5</tspan>（38.212 §7.1.1）', 11.5, '#c00000')
s += txt(60, 428, '未提供 ssb-SubcarrierOffset 时：由 SSB 与 Point A 的频率差推导', 11.5, '#666')
s += txt(60, 452, '判断：FR1 k<tspan baseline-shift="sub">SSB</tspan> ≤ 23 → 有 SIB1/CORESET#0；= 31 → 无 SIB1（pdcch-ConfigSIB1 改作频率位置/范围指示）', 11.5, '#b22222')
s += txt(60, 466, 'FR2：k<tspan baseline-shift="sub">SSB</tspan> ≤ 11 → 有；= 15 → 无（38.213 §4.1）', 11.5, '#b22222')
frags['fig3'] = fig_wrap('图 3', 'Point A / offsetToPointA / \(N_{CRB}^{SSB}\) / \(k_{SSB}\) / SSB 频域关系图（38.211 §7.4.3.1：SSB 子载波 0 相对 CRB \(N_{CRB}^{SSB}\) 子载波 0 偏移 \(k_{SSB}\) 个子载波）', s, W, H)

# ---------------- 图 4：Case A beam sweep ----------------
W, H = 800, 330
px = 70; sy = 10; sc = 9.4; y1 = 90; y2 = 200; bh = 46
s = ''
for k in range(0, 71, 7):
    x = px + k*sc
    s += line(x, y1+bh+8, x, y1+bh+16, '#555', 1)
    s += txt(x, y1+bh+32, str(k), 11, '#555', 'middle')
s += line(px, y1+bh+8, px+70*sc, y1+bh+8, '#555', 1.2)
s += txt(px+70*sc/2, y1+bh+50, '时间（符号索引，0 = 半帧内第 1 个时隙的第 1 个符号）', 12, '#555', 'middle')
s += txt(px-14, y1+bh/2-14, '≤ 3 GHz', 12, '#333', 'end', True)
s += txt(px-14, y1+bh/2+6, 'L<tspan baseline-shift="sub">max</tspan> = 4', 12, '#333', 'end')
s += txt(px-14, y2+bh/2-14, '3~6 GHz', 12, '#333', 'end', True)
s += txt(px-14, y2+bh/2+6, 'L<tspan baseline-shift="sub">max</tspan> = 8', 12, '#333', 'end')
sets1 = [2, 8, 16, 22]
for i, k0 in enumerate(sets1):
    x = px + k0*sc
    s += rect(x, y1, 4*sc, bh, '#9dc3e6')
    s += txt(x+2*sc, y1+bh/2+4, f'#{i}', 12, '#1a3e6e', 'middle', True)
sets2 = [2, 8, 16, 22, 30, 36, 44, 50]
for i, k0 in enumerate(sets2):
    x = px + k0*sc
    s += rect(x, y2, 4*sc, bh, '#9dc3e6')
    s += txt(x+2*sc, y2+bh/2+4, f'#{i}', 12, '#1a3e6e', 'middle', True)
s += txt(px+50, y1-20, 'Case A（15 kHz SCS）：起始符号 {2, 8} + 14·n', 13, '#0b3d6b', 'middle', True)
s += txt(560, 262, 'SSB 周期：半帧 5 ms 内扫描，', 11.5, '#666')
s += txt(560, 278, '周期 20 ms（初始小区选择假定）', 11.5, '#666')
s += line(540, 258, 552, 258, '#888', 1.1, '4,4')
s += txt(px, 302, '每块 = 1 个 SSB（4 符号）；实际发射的块由 SIB1 的 ssb-PositionsInBurst 指示；Case B/C/D/E 同理（见表格）', 11, '#666')
frags['fig4'] = fig_wrap('图 4', 'Case A（15 kHz）半帧内 SSB 候选位置与波束扫描（38.213 §4.1：{2,8}+14n）', s, W, H)

# ---------------- 图 5：PBCH 处理链 ----------------
W, H = 800, 330
s = ''
s += rect(30, 40, 190, 54, '#fde8c8')
s += txt(125, 58, 'SFN（10 bit）拆分', 12, '#7a4a00', 'middle', True)
s += txt(125, 76, '高 6 bit：MIB systemFrameNumber', 11, '#333', 'middle')
s += txt(125, 90, '低 4 bit：PBCH 载荷 a_24~a_27', 11, '#333', 'middle')
s += arrow(125, 94, 125, 128, '#7a4a00', 1.4)
y = 130
s += rect(20, y, 130, 52, '#dce9f5')
s += txt(85, y+22, 'MIB', 13, '#0b3d6b', 'middle', True)
s += txt(85, y+40, '24 bit（RRC 编码）', 11, '#333', 'middle')
s += rect(170, y, 150, 52, '#e3f0e3')
s += txt(245, y+22, '＋定时载荷 8 bit', 13, '#1b5e20', 'middle', True)
s += txt(245, y+40, 'SFN 低 4 位/半帧/k<tspan baseline-shift="sub">SSB</tspan> 高位', 11, '#333', 'middle')
s += rect(340, y, 130, 52, '#f0f0f0')
s += txt(405, y+22, '交织 G(j)', 13, '#333', 'middle', True)
s += txt(405, y+40, 'Table 7.1.1-1', 11, '#555', 'middle')
s += rect(490, y, 150, 52, '#f0f0f0')
s += txt(565, y+22, '加扰', 13, '#333', 'middle', True)
s += txt(565, y+40, 'c<tspan baseline-shift="sub">init</tspan> = N<tspan baseline-shift="sub">ID</tspan><tspan baseline-shift="super">cell</tspan>', 11, '#555', 'middle')
s += rect(660, y, 110, 52, '#f0f0f0')
s += txt(715, y+22, 'CRC 24', 13, '#333', 'middle', True)
s += txt(715, y+40, '56 bit TB', 11, '#555', 'middle')
s += arrow(150, y+26, 170, y+26)
s += arrow(320, y+26, 340, y+26)
s += arrow(470, y+26, 490, y+26)
s += arrow(640, y+26, 660, y+26)
s += line(715, y+52, 715, 250, '#1b5e20', 1.5)
s += arrow(715, 250, 715, 270, '#1b5e20')
y2 = 270
s += rect(620, y2, 110, 50, '#f0f0f0')
s += txt(675, y2+20, 'Polar 编码', 13, '#333', 'middle', True)
s += txt(675, y2+38, '512 bit 母码', 11, '#555', 'middle')
s += rect(470, y2, 130, 50, '#f0f0f0')
s += txt(535, y2+20, '速率匹配', 13, '#333', 'middle', True)
s += txt(535, y2+38, '子块交织', 11, '#555', 'middle')
s += rect(340, y2, 110, 50, '#fde8c8')
s += txt(395, y2+20, '864 bit', 13, '#7a4a00', 'middle', True)
s += txt(395, y2+38, 'QPSK', 11, '#555', 'middle')
s += rect(200, y2, 120, 50, '#e3f0e3')
s += txt(260, y2+20, '432 个 RE', 13, '#1b5e20', 'middle', True)
s += txt(260, y2+38, '576 − 144 DM-RS', 11, '#555', 'middle')
s += arrow(620, y2+25, 600, y2+25)
s += arrow(470, y2+25, 450, y2+25)
s += arrow(340, y2+25, 320, y2+25)
s += txt(565, 240, '承载定时信息的比特不参与扰码', 11, '#b22222', 'middle')
s += line(565, 244, 565, 182, '#b22222', 0.9, '3,3')
frags['fig5'] = fig_wrap('图 5', 'PBCH 处理链：MIB → 交织 → 加扰 → CRC → Polar → 864 bit → 432 RE（38.212 §7.1；加扰时定时比特不扰码）', s, W, H)

# ---------------- 图 6：SI 窗口排布 ----------------
W, H = 800, 380
px = 90; sc = 1.9; y0 = 96; rh = 74
s = ''
s += txt(px, 30, '例：w = 20 槽，T = 16 帧（rf16），N = 10 槽/帧（15 kHz SCS）', 13, '#0b3d6b', 'start', True)
for f in range(0, 33, 4):
    x = px + f*10*sc
    s += line(x, y0-8, x, y0+3*rh+8, '#eee', 1)
    s += line(x, y0-12, x, y0-8, '#555', 1)
    s += txt(x, y0-18, f'SFN {f}', 11, '#555', 'middle')
s += line(px, y0-12, px+320*sc, y0-12, '#555', 1.2)
for n in (1, 2, 3):
    y = y0 + (n-1)*rh
    s += txt(px-8, y+rh/2+4, f'SI#{n}', 12, '#333', 'end', True)
    xx = (n-1)*20
    wins = []
    while xx < 320:
        wins.append(xx)
        xx += 16*10
    for wst in wins:
        x0 = px + wst*sc
        s += rect(x0, y, 20*sc, rh-8, '#a9d08e')
        s += txt(x0+20*sc/2, y-6, '20 槽', 10, '#33511f', 'middle')
        s += txt(x0+20*sc/2, y+rh-4, f'n={n}', 10, '#33511f', 'middle')
s += txt(px, 326, '窗口起点：x=(n−1)·w → SI#1 从 SFN mod 16 = 0 时隙 0 起；SI#2 从 SFN mod 16 = 2 时隙 0 起；SI#3 从 SFN mod 16 = 4 时隙 0 起', 11.5, '#555')
s += txt(px, 344, '（时隙 a = x mod N）。每 T 帧重复一次；窗口内 UE 从起点盲检 SI-RNTI 直至收到或窗口结束。', 11.5, '#555')
frags['fig6'] = fig_wrap('图 6', 'SI 窗口在时间轴上的排布（\(x=(n-1)\cdot w\) 可视化：各 SI 消息窗口错开 w 个时隙、按周期 T 循环）', s, W, H)

# ---------------- 图 7：修改周期 ----------------
W, H = 800, 300
s = ''
s += line(60, 140, 740, 140, '#555', 1.4)
s += txt(60, 128, '修改周期 m', 13, '#333', 'middle', True)
s += txt(400, 128, '修改周期 m+1', 13, '#333', 'middle', True)
s += line(400, 140, 400, 200, '#b22222', 2.2)
s += txt(400, 214, '边界：SFN mod m = 0', 12, '#b22222', 'middle', True)
s += rect(60, 156, 340, 44, '#dce9f5')
s += txt(230, 174, 'SI 版本 V1 持续广播', 13, '#0b3d6b', 'middle', True)
s += txt(230, 190, '（周期 m 内内容不变）', 11, '#555', 'middle')
s += rect(400, 156, 340, 44, '#e3f0e3')
s += txt(570, 174, 'SI 版本 V2 生效（更新后的 SI）', 13, '#1b5e20', 'middle', True)
s += txt(570, 190, 'UE 从本周期起点按 §5.2.2.3 重新获取', 11, '#555', 'middle')
s += rect(100, 226, 210, 34, '#fde8c8')
s += txt(205, 240, 'Short Message（P-RNTI）：', 11, '#7a4a00', 'middle', True)
s += txt(205, 254, 'systemInfoModification = 1（可重复）', 11, '#7a4a00', 'middle')
s += line(205, 226, 205, 200, '#7a4a00', 1.3, '4,4')
s += txt(470, 244, 'ETWS/CMAS 例外：etwsAndCmasIndication = 1 →', 11.5, '#b22222')
s += txt(470, 262, '立即重读 SIB1 与 SIB6/7/8（不等修改周期）', 11.5, '#b22222')
frags['fig7'] = fig_wrap('图 7', '修改周期机制：前一周期预告（Short Message）、后一周期生效（38.331 §5.2.2.2.2）', s, W, H)

# ---------------- 图 8：按需 SI 双路径 ----------------
W, H = 800, 430
s = ''
s += rect(200, 30, 400, 52, '#dce9f5')
s += txt(400, 46, 'UE 需要 si-BroadcastStatus = notBroadcasting 的 SI 消息', 11.5, '#0b3d6b', 'middle', True)
s += txt(400, 64, 'SIB1 的 si-SchedulingInfo 是否配了 si-RequestConfig（或 SUL 版）？', 11.5, '#0b3d6b', 'middle')
s += line(320, 82, 320, 98, '#555', 1.4)
s += line(480, 82, 480, 98, '#555', 1.4)
s += txt(290, 94, '是（Msg1 方式）', 12, '#1b5e20', 'middle', True)
s += txt(555, 94, '否（Msg3 方式）', 12, '#7a4a00', 'middle', True)
s += line(290, 98, 210, 112, '#1b5e20', 1.4)
s += rect(90, 114, 240, 40, '#e3f0e3')
s += txt(210, 130, '① 选 SSB（RSRP > rsrp-ThresholdSSB），', 12, '#1b5e20', 'middle')
s += txt(210, 146, '发专用前导（ra-PreambleStartIndex + i）', 12, '#1b5e20', 'middle')
s += arrow(210, 154, 210, 172, '#1b5e20')
s += rect(90, 174, 240, 40, '#e3f0e3')
s += txt(210, 190, '② gNB 回 RAR：只含 RAPID 的', 12, '#1b5e20', 'middle')
s += txt(210, 206, 'MAC subPDU → 视为 SI 请求 ACK', 12, '#1b5e20', 'middle')
s += arrow(210, 214, 210, 232, '#1b5e20')
s += rect(90, 234, 240, 40, '#e3f0e3')
s += txt(210, 250, '③ 立即进入该 SI 消息的下一个窗口', 12, '#1b5e20', 'middle')
s += txt(210, 266, '盲检 SI-RNTI 接收（§5.2.2.3.2）', 12, '#1b5e20', 'middle')
s += txt(210, 292, '（38.321 §5.1.4：RAR 只含 RAPID →', 10.5, '#666', 'middle')
s += txt(210, 304, 'SI 请求确认）', 10.5, '#666', 'middle')
s += line(555, 98, 610, 112, '#7a4a00', 1.4)
s += rect(470, 114, 280, 40, '#fde8c8')
s += txt(610, 130, '① Msg1：公共前导 → RAR', 12, '#7a4a00', 'middle')
s += txt(610, 146, '（RAPID + TA + UL grant）', 12, '#7a4a00', 'middle')
s += arrow(610, 154, 610, 172, '#7a4a00')
s += rect(470, 174, 280, 40, '#fde8c8')
s += txt(610, 190, '② Msg3：RRCSystemInfoRequest', 12, '#7a4a00', 'middle')
s += txt(610, 206, '（CCCH/SRB0/TM，requested-SI-List）', 12, '#7a4a00', 'middle')
s += arrow(610, 214, 610, 232, '#7a4a00')
s += rect(470, 234, 280, 40, '#fde8c8')
s += txt(610, 250, '③ Msg4：冲突解决成功（TC-RNTI）', 12, '#7a4a00', 'middle')
s += txt(610, 266, '→ 视为 SI 请求 ACK（38.321 §5.1.5）', 12, '#7a4a00', 'middle')
s += arrow(610, 274, 610, 292, '#7a4a00')
s += rect(470, 294, 280, 40, '#fde8c8')
s += txt(610, 310, '④ 立即进入窗口接收请求的 SI 消息', 12, '#7a4a00', 'middle')
s += txt(610, 326, '（ACK 后 immediately 获取）', 11, '#7a4a00', 'middle')
s += rect(250, 356, 300, 44, '#f0f0f0')
s += txt(400, 372, '网络在 SI 窗口内临时广播（至修改周期末）', 12, '#333', 'middle', True)
s += txt(400, 390, '等待期间发生小区重选：重置 MAC；Msg3 方式另须释放 SRB0 的 RLC', 11, '#666', 'middle')
s += line(210, 308, 210, 356, '#555', 1.2)
s += line(610, 334, 610, 356, '#555', 1.2)
s += arrow(210, 356, 330, 356, '#555')
s += arrow(610, 356, 470, 356, '#555')
frags['fig8'] = fig_wrap('图 8', '按需 SI 双路径流程：Msg1 专用前导（左）与 Msg3 RRCSystemInfoRequest（右）（38.331 §5.2.2.3.3/§5.2.2.3.4 + 38.321 §5.1.4/§5.1.5）', s, W, H)

# ---------------- 图 9：端到端全流程 ----------------
W, H = 800, 640
s = ''
steps = [
    ('①', '频点扫描', '同步栅格（GSCN）上找能量峰', '#f5f8fc'),
    ('②', 'SSB 检测', 'PSS → N<tspan baseline-shift="sub">ID</tspan><tspan baseline-shift="super">(2)</tspan> + 半帧；SSS → N<tspan baseline-shift="sub">ID</tspan><tspan baseline-shift="super">(1)</tspan>，PCI 定帧；DM-RS→索引低位', '#fde8c8'),
    ('③', 'MIB 解码', 'PBCH Polar 解码：SFN/k<tspan baseline-shift="sub">SSB</tspan>/SCS/pdcch-ConfigSIB1/cellBarred', '#dce9f5'),
    ('④', 'CORESET#0 查表', 'pdcch-ConfigSIB1 高4位 Table 13-1~13-10、低4位 Table 13-11~13-15', '#dce9f5'),
    ('⑤', 'SIB1 接收', 'Type0 CSS 盲检 SI-RNTI；PLMN/驻留/公共配置/si-SchedulingInfo', '#e3f0e3'),
    ('⑥', 'OSI 接收', 'SI 窗口公式逐个收 SIB2/3/4（+5）；SIB6/7/8 等 Short Message 触发', '#e3f0e3'),
    ('⑦', '随机接入', 'SIB1 的 RACH 配置 + SSB-RO 关联；Msg2/4 SCS 用 subCarrierSpacingCommon', '#f0f0f0'),
    ('⑧', '驻留维护', '每 DRX 在 PO 查 Short Message：systemInfoModification / etwsAndCmasIndication', '#fdeeee'),
    ('⑨', '按需 SI', 'notBroadcasting 的 SI：Msg1 专用前导 或 Msg3 RRCSystemInfoRequest', '#fdeeee'),
]
y = 30
for num, t1, t2, c in steps:
    s += f'<circle cx="55" cy="{y+24}" r="14" fill="{c}" stroke="#444"/>'
    s += txt(55, y+29, num, 13, '#333', 'middle', True)
    s += rect(84, y+4, 640, 40, c)
    s += txt(100, y+20, t1, 13, '#1a1a1a', 'start', True)
    s += txt(100, y+36, t2, 11, '#444')
    if y > 30:
        s += arrow(55, y-8, 55, y+2, '#555')
    y += 62
s += txt(84, y+8, '主线：SSB → MIB → CORESET#0 → SIB1 → OSI → 驻留/接入；支线：Short Message 变更与按需 SI 随时插入。', 12, '#555')
frags['fig9'] = fig_wrap('图 9', '端到端全流程（系统消息视角）：开机 → SSB → MIB → SIB1 → OSI → 接入与驻留维护', s, W, H)

for k, v in frags.items():
    with open(os.path.join(OUT, k + '.html'), 'w', encoding='utf-8') as f:
        f.write(v)
print('figs v2:', list(frags.keys()))
