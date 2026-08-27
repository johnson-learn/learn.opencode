# -*- coding: utf-8 -*-
# 修正所有文件中的 tests 路径引用：<项目目录>\tests → <opencode配置目录>\tests（本机 <opencode配置目录>\tests）
import sys, os, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HOME = r"<opencode配置目录>"
files = [
    HOME + r"\tests\test_path_convert.py",
    HOME + r"\tests\README.md",
    HOME + r"\tests\test_plugin.js",
    HOME + r"\instructions.md",
    HOME + r"\evolution.md",
    HOME + r"\plugins\skill-banner.js",
    HOME + r"\tools-manifest.md",
    HOME + r"\skills\update_skill\SKILL.md",
]
for p in files:
    if not os.path.isfile(p):
        print("跳过（不存在）:", p)
        continue
    c = open(p, encoding="utf-8").read()
    orig = c
    c = c.replace(r"<项目目录>\tests", r"<opencode配置目录>\tests")
    c = c.replace(r"<项目目录>\temp\skill_validate.py", r"<opencode配置目录>\tests\skill_validate.py")
    c = c.replace(r"<项目目录>\temp\test_plugin.js", r"<opencode配置目录>\tests\test_plugin.js")
    c = c.replace(r"<项目目录>\temp\path_convert.py", r"<opencode配置目录>\tests\path_convert.py")
    if c != orig:
        open(p, "w", encoding="utf-8", newline="").write(c)
        print("已更新:", os.path.basename(p))
    else:
        print("无变更:", os.path.basename(p))
