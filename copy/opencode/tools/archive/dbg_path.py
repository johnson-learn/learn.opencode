# -*- coding: utf-8 -*-
import os
h = r"<用户目录>"
t = r"本机 <opencode配置目录> 测试"
print(t.replace(h, "<用户目录>"))
p = "/home/github/learn.opencode/opencode/skills/update_skill/SKILL.md"
with open(p, encoding="utf-8") as f:
    c = f.read()
print("文件含 <工具目录>\Users 次数:", c.count(r"<工具目录>Users"))
print("前 150 字:", c[:150])
