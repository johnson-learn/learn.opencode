# -*- coding: utf-8 -*-
# session_compress_skill L1 领域自测：入口规范 / 模块引用无悬空 / references 无悬空 / 技能特定断言
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
check("name 为 session_compress_skill", re.search(r"^name:\s*session_compress_skill\s*$", fm, re.M) is not None)
dm = re.search(r"^description:\s*(.*)$", fm, re.M)
check("description 为显式触发型（仅显式触发）", dm and "仅显式触发" in dm.group(1) and "session_compress_skill：" in dm.group(1) and "Use ONLY when" in dm.group(1))
check("description ≤1024 字符", dm and len(dm.group(1)) <= 1024)

# 2. 模块引用无悬空（本 skill 非聚合型，应无 modules）
mod_dir = os.path.join(SKILL, "modules")
mods = set(os.listdir(mod_dir)) if os.path.isdir(mod_dir) else set()
check("无 modules（非聚合型）", len(mods) == 0)

# 3. references 无悬空
ref_dir = os.path.join(SKILL, "references")
ref_files = set(re.findall(r"`references/([\w\-]+\.md)`", c))
have = set(os.listdir(ref_dir)) if os.path.isdir(ref_dir) else set()
missing = sorted(f for f in ref_files if f not in have)
check("references 索引无悬空（缺失: %s）" % ",".join(missing) if missing else "references 索引无悬空（引用 %d 个）" % len(ref_files), len(missing) == 0)

# 4. 技能特定断言：会话压缩流程要素
check("引用权威模板 references/config-template.md", "references/config-template.md" in c)
check("含处理流程（读模板 → 收集上下文 → 生成 session.md → 自检）", ("处理流程" in c) and ("session.md" in c) and ("references/config-template.md" in c))
check("含只写业务类", "只写业务类" in c or "业务类" in c)
check("含上下文不包括框架 skill", "框架 skill" in c and "一律不写入" in c or ("框架 skill" in c and "不写入" in c))
check("含不写下一步", "不写\"下一步\"" in c)
check("含文件名固定 session.md", "文件名固定" in c and "session.md" in c)
check("含 E 只列非内置业务工具/opencode 内置不写", "opencode 内置工具不写" in c)
check("含工具依赖清单章节", "工具依赖清单" in c)
check("含本 skill 经验索引", "经验索引" in c)

# 5. 模板文件 config-template.md 自身结构校验（A/B/C/D/E）
ref_file = os.path.join(ref_dir, "config-template.md")
if os.path.isfile(ref_file):
    rc = open(ref_file, encoding="utf-8", errors="replace").read()
    check("模板含 A. 历史会话主题", "A. 历史会话主题" in rc)
    check("模板含 B. 历史会话目录", "B. 历史会话目录" in rc)
    check("模板含 C. 历史会话要点", "C. 历史会话要点" in rc)
    check("模板含 D. 历史会话修改/输出文件", "D. 历史会话修改/输出文件" in rc)
    check("模板含 E. 历史会话使用工具", "E. 历史会话使用工具" in rc)
    check("模板含使用规则（业务类/框架不进/不写下一步/内置工具不写）", "使用规则" in rc and "业务类" in rc and "框架 skill" in rc and "内置工具不写" in rc)
else:
    check("模板 config-template.md 存在", False)

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
