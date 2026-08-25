# -*- coding: utf-8 -*-
"""SVG text 重叠检测（保守版）"""
import re, glob, sys

def text_wh(s, size):
    w = 0
    for ch in s:
        w += size if ord(ch) > 0x2E80 else size * 0.58
    return w, size * 1.25

def main():
    files = glob.glob(r"C:\Users\job_p\Desktop\NR-f40\系统消息*.html")
    total = 0
    for f in files:
        html = open(f, encoding='utf-8').read()
        svgs = re.findall(r'<svg\b.*?</svg>', html, re.S)
        print(f'== {f} : {len(svgs)} 个 SVG ==')
        for si, svg in enumerate(svgs):
            texts = re.findall(r'(<text\b[^>]*>)([\s\S]*?)</text>', svg)
            boxes = []
            for tag, content in texts:
                m = re.search(r'x="([\d.]+)"', tag)
                n = re.search(r'y="([\d.]+)"', tag)
                fs = re.search(r'font-size="([\d.]+)"', tag)
                an = re.search(r'text-anchor="(\w+)"', tag)
                rot = re.search(r'transform="rotate', tag)
                if not (m and n and fs):
                    continue
                if rot:
                    continue
                x = float(m.group(1)); y = float(n.group(1)); sz = float(fs.group(1))
                content = re.sub(r'<[^>]+>', '', content)
                anchor = an.group(1) if an else 'start'
                w, h = text_wh(content, sz)
                if anchor == 'middle':
                    x -= w/2
                elif anchor == 'end':
                    x -= w
                boxes.append((x, y-h, x+w, y+3, content[:30], sz))
            pairs = 0
            for i in range(len(boxes)):
                for j in range(i+1, len(boxes)):
                    a, b = boxes[i], boxes[j]
                    if a[0] < b[2]-0.5 and b[0] < a[2]-0.5 and a[1] < b[3]-0.5 and b[1] < a[3]-0.5:
                        ovh = min(a[3], b[3]) - max(a[1], b[1])
                        if ovh > 0.55 * min(a[5], b[5]):
                            pairs += 1
                            if pairs <= 14:
                                print(f'  SVG#{si+1} [{a[4]}] <<>> [{b[4]}] (y {a[1]:.0f}~{a[3]:.0f} vs {b[1]:.0f}~{b[3]:.0f})')
            total += pairs
            if pairs:
                print(f'  SVG#{si+1} 重叠对数: {pairs}')
        print()
    print('总重叠对数:', total)
    sys.exit(1 if total else 0)

main()
