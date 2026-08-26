# -*- coding: utf-8 -*-
import re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
p = r"<opencode配置目录>\skills\3gpp_skill\SKILL.md"
c = open(p, encoding="utf-8").read()
titles = re.findall(r"(?m)^## (.+)$", c)
for t in titles:
    print(repr(t[:40]), "| 教学:", "教学输出模板" in t, "| HTML:", "HTML" in t, "| 配图:", "配图" in t)
