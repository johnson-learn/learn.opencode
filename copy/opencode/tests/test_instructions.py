# -*- coding: utf-8 -*-
# instructions.md 规则一致性测试：章节完整 / 与 AGENTS.md 铁律互查 / 引用文件存在 / 技能清单与目录一致 / 各 skill 遵守编写规范
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CFG = os.path.join(os.path.expanduser("~"), ".config", "opencode")
pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

ins = open(os.path.join(CFG, "instructions.md"), encoding="utf-8").read()
agents = open(os.path.join(CFG, "AGENTS.md"), encoding="utf-8").read()

# 1. 章节完整性
for sec in ["智能进化协议", "全局通用回答规则", "全局 skill 编写规范", "本机全局技能清单", "项目 skill"]:
    check("章节存在: " + sec, sec in ins)

# 2. AGENTS.md 铁律 0~8 共 9 条
nums = re.findall(r"^## (\d)\. ", agents, re.M)
check("AGENTS.md 铁律 0~8 共 9 条", sorted(nums) == [str(i) for i in range(9)])

# 3. instructions.md 引用的铁律编号不超过 8 且指向正确条款
refs = re.findall(r"铁律第\s*(\d)\s*条", ins)
check("instructions 引用铁律编号合法", all(int(n) <= 8 for n in refs))
# 第 2 条=复盘进化 的对照
m2 = re.search(r"^## 2\. (.*)$", agents, re.M)
check("AGENTS.md 第 2 条为复盘进化", m2 and "复盘进化" in m2.group(1))
check("instructions 引用了铁律第 2 条（复盘进化执行）", "2" in refs)

# 4. 引用文件存在性（占位符解析）
files = ["tools-manifest.md", "regedit.md", "skills\\evolution_skill\\evolution.md", "tests\\skill_validate.py",
         "tools\\inject_skills.py"]
for f in files:
    check("引用文件存在: " + f, os.path.exists(os.path.join(CFG, f)))
check("instructions 引用 regedit.md 机制", "regedit.md" in ins)
check("instructions 引用 tools-manifest 权威", "tools-manifest.md" in ins)
check("instructions 引用 evolution_skill 执行器", "evolution_skill" in ins)

# 5. 技能清单表与 skills 目录一致（双向）
skill_dirs = set(d for d in os.listdir(os.path.join(CFG, "skills"))
                 if os.path.isdir(os.path.join(CFG, "skills", d)))
table_skills = set(re.findall(r"\| `(\w+_skill)` \|", ins))
check("技能清单表覆盖全部 %d 个 skill" % len(skill_dirs), skill_dirs <= table_skills)
check("技能清单表无多余条目", table_skills <= skill_dirs)
check("技能清单表含 evolution_skill", "evolution_skill" in table_skills)

# 6. 各 skill 遵守编写规范（工具依赖清单或 references 指向）
for d in sorted(skill_dirs):
    p = os.path.join(CFG, "skills", d, "SKILL.md")
    if not os.path.exists(p):
        check(d + " 有 SKILL.md", False)
        continue
    c = open(p, encoding="utf-8").read()
    ok = ("工具依赖清单" in c) or ("references" in c)
    check(d + " 遵守编写规范（工具清单/references）", ok)

# 7. 五步进化流程关键要素
for kw in ["归纳", "归属", "evolution_log.txt", "校验与自测", "行为自测"]:
    check("五步流程要素: " + kw, kw in ins)

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
