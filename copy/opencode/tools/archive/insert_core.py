# -*- coding: utf-8 -*-
# 给 update_skill SKILL.md 插入核心准则
p = r"<opencode配置目录>\skills\update_skill\SKILL.md"
with open(p, encoding="utf-8") as f:
    c = f.read()

anchor = "# update_skill"
addition = """

## 核心准则（一句话，执行时必须全部保证）

> **update_skill 执行时必须保证三点：① 当前电脑的新增修改同步到远端（GitHub）；② 远端内容保持可移植（占位符体系），能移植安装到全新电脑；③ 远端新提交能反向更新到另一台已移植旧版本的电脑上（pull + 版本对齐 + to_local）。**
"""
i = c.find(anchor)
if i >= 0:
    end = c.find("\n", i)
    c = c[:end+1] + addition + c[end+1:]
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(c)
    print("核心准则已插入")
else:
    print("锚点未找到")
