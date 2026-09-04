# -*- coding: utf-8 -*-
# evolution_skill L1 领域自测（2026-09-01 框架进化评审建议落地）：
# 入口规范 / 模块引用无悬空 / references 无悬空 / 技能特定断言
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

SKILL_MD = os.path.join(SKILL, "SKILL.md")
c = open(SKILL_MD, encoding="utf-8", errors="replace").read()

# 1. 入口规范
m = re.search(r"^---\n(.*?)\n---", c, re.S)
check("frontmatter 存在", bool(m))
fm = m.group(1) if m else ""
check("name 为 evolution_skill", re.search(r"^name:\s*evolution_skill\s*$", fm, re.M) is not None)
dm = re.search(r"^description:\s*(.*)$", fm, re.M)
check("description 为默认触发型（进化执行器，非显式前缀）", dm and "默认触发" in dm.group(1) and "进化" in dm.group(1))
check("description ≤1024 字符", dm and len(dm.group(1)) <= 1024)

# 2. 模块引用无悬空（SKILL.md 反引号中的 modules/<dir> 引用必须实际存在）
mods = set(d for d in os.listdir(os.path.join(SKILL, "modules"))
           if os.path.isdir(os.path.join(SKILL, "modules", d))) if os.path.isdir(os.path.join(SKILL, "modules")) else set()
refs = set(re.findall(r"modules/([\w\-]+)", c))
dangling = sorted(r for r in refs if r not in mods)
check("模块引用无悬空（缺失: %s）" % ",".join(dangling) if dangling else "模块引用无悬空（引用 %d 个 / 实际 %d 个）" % (len(refs), len(mods)), len(dangling) == 0)

# 3. references 无悬空
ref_dir = os.path.join(SKILL, "references")
ref_files = set(re.findall(r"`references/([\w\-]+\.md)`", c))
have = set(os.listdir(ref_dir)) if os.path.isdir(ref_dir) else set()
missing = sorted(f for f in ref_files if f not in have)
check("references 索引无悬空（缺失: %s）" % ",".join(missing) if missing else "references 索引无悬空", len(missing) == 0)

# 4. 技能特定：六步固化 + 新增文件适配 + templates
check("六步固化流程存在", "第一步" in c and "第六步" in c and "判定四条件" in c and "第三步·确认" in c)
check("新增文件四问适配流程存在", "四问" in c)
tpl_dir = os.path.join(SKILL, "templates")
check("templates 两个固化模板", os.path.isdir(tpl_dir) and all(os.path.isfile(os.path.join(tpl_dir, f)) for f in ["six-step-template.md", "new-file-adapt-template.md"]))
check("无 modules（本 skill 非聚合型）", len(mods) == 0)

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
