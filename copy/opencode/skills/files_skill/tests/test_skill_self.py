# -*- coding: utf-8 -*-
# files_skill L1 领域自测（2026-09-01 框架进化评审建议落地）：
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
check("name 为 files_skill", re.search(r"^name:\s*files_skill\s*$", fm, re.M) is not None)
dm = re.search(r"^description:\s*(.*)$", fm, re.M)
check("description 含显式触发约定", dm and "files_skill：" in dm.group(1) and "Use ONLY when" in dm.group(1))
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

# 4. 技能特定：scripts 归档 + 文字提取双轨铁律
check("scripts 归档 extract-docx/doc.ps1", all(os.path.isfile(os.path.join(SKILL, "scripts", f)) for f in ["extract-docx.ps1", "extract-doc.ps1"]))
check("文字提取双轨铁律存在（文本+图片识别核实）", "双轨" in c and "p2t" in c)
check("PPTX 渲染双坑铁律存在", "空 cell" in c and "rowSpan" in c)
check("modules 聚合 100+（文件处理资源库）", len(mods) >= 100)

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
