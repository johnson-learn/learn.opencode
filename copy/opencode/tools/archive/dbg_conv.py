# -*- coding: utf-8 -*-
# 诊断 path_convert 为什么 0 转换
import sys, os
PC = "/mnt/e/openCodeDefault/temp/path_convert.py"
import importlib.util
spec = importlib.util.spec_from_file_location("pc", PC)
pc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pc)

print("HOME:", repr(pc.HOME))
pairs = pc.build_portable_map()
print("映射对数量:", len(pairs))
for r, ph in pairs[:12]:
    print("  ", repr(r), "->", ph)

root = "/home/github/learn.opencode/copy/opencode"
cnt = 0
total = 0
for dirpath, dirnames, filenames in os.walk(root):
    if ".git" in dirpath.split(os.sep):
        continue
    for fn in filenames:
        if not fn.lower().endswith((".md", ".jsonc", ".json", ".txt", ".ps1", ".py", ".bat", ".sh")):
            continue
        total += 1
        p = os.path.join(dirpath, fn)
        try:
            with open(p, encoding="utf-8") as f:
                c = f.read()
        except Exception:
            continue
        if ("<工具目录>\Users" in c) or ("E:\\" in c):
            cnt += 1
            if cnt <= 5:
                print("含路径文件:", p)
print("扫描文件总数:", total, "含绝对路径文件数:", cnt)
