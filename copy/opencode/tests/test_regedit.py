# -*- coding: utf-8 -*-
# 注册表一致性测试：regedit.md 与实际文件系统、AGENTS.md 引用互查（隔离，不碰仓库）
import os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CFG = r"<opencode配置目录>"
pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

# 1. 注册表文件存在
check("regedit.md 存在", os.path.exists(os.path.join(CFG, "regedit.md")))

# 2. AGENTS.md 引用 regedit.md（铁律第 0 条）
agents = open(os.path.join(CFG, "AGENTS.md"), encoding="utf-8").read()
check("AGENTS.md 含铁律第 0 条「注册表必读」", "注册表必读" in agents and "regedit.md" in agents)
check("AGENTS.md 引用 test_regedit.py", "test_regedit.py" in agents)

# 3. 注册表登记的路径必须实际存在
reg = open(os.path.join(CFG, "regedit.md"), encoding="utf-8").read()
import re
for item in ["tools\\inject_skills.py", "tools\\path_convert.py", "tools\\slim_skills.py",
             "tools\\fetch_skills.py", "tools\\cross_move.py", "tools\\generalize.py",
             "tests\\skill_validate.py", "tests\\test_plugin.js", "tests\\test_path_convert.py",
             "tests\\test_update_skill.py", "tests\\test_regedit.py", "tests\\README.md",
             "plugins\\skill-banner.js", "instructions.md", "evolution.md", "tools-manifest.md"]:
    key = item.split("\\")[-1].split(".")[0]
    check("注册表条目存在: " + item, item in reg)

# 4. 实际存在的关键组件必须在注册表有登记（反查）
def registered(name):
    return name in reg
for name in ["3gpp_skill", "files_skill", "find_skill", "program_skill", "update_skill",
             "skill-banner.js", "inject_skills.py", "path_convert.py", "slim_skills.py",
             "fetch_skills.py", "cross_move.py", "generalize.py", "skill_validate.py",
             "test_plugin.js", "test_path_convert.py", "test_update_skill.py", "test_regedit.py",
             "tools-manifest.md", "path_map.txt", "sync_target.txt", "evolution_trace.jsonl",
             "plugin-evolution.log", "instructions.md", "evolution.md"]:
    check("组件已登记: " + name, registered(name))

# 5. 生效方式代号合法性（A~H）
bad = set(re.findall(r"^\| \*\*([A-Z]) ", reg, flags=re.M)) - set("ABCDEFGH")
check("生效方式代号均在 A~H", len(bad) == 0)

# 6. 注册表登记的文件实际存在（文件系统反查）
fs_checks = [
    ("skills/3gpp_skill/SKILL.md", "3gpp_skill"),
    ("skills/files_skill/SKILL.md", "files_skill"),
    ("skills/find_skill/SKILL.md", "find_skill"),
    ("skills/program_skill/SKILL.md", "program_skill"),
    ("skills/update_skill/SKILL.md", "update_skill"),
    ("plugins/skill-banner.js", "skill-banner.js"),
    ("tools/inject_skills.py", "inject_skills.py"),
    ("tools/path_convert.py", "path_convert.py"),
    ("tests/skill_validate.py", "skill_validate.py"),
    ("tests/test_plugin.js", "test_plugin.js"),
    ("tests/test_path_convert.py", "test_path_convert.py"),
    ("tests/test_update_skill.py", "test_update_skill.py"),
    ("AGENTS.md", "AGENTS.md"),
    ("instructions.md", "instructions.md"),
    ("evolution.md", "evolution.md"),
    ("tools-manifest.md", "tools-manifest.md"),
    ("regedit.md", "regedit.md"),
]
missing = [f for f, _ in fs_checks if not os.path.exists(os.path.join(CFG, f.replace("/", "\\")))]
check("注册表登记的 17 个文件实际存在", len(missing) == 0)
if missing: print("    缺失:", missing)

# 7. skills 目录实际 6 个全局 skill 与注册表一致
skill_dirs = [d for d in os.listdir(os.path.join(CFG, "skills"))
              if os.path.isdir(os.path.join(CFG, "skills", d))]
check("skills 目录 6 个与注册表一致", sorted(skill_dirs) == sorted(["3gpp_skill", "files_skill", "find_skill", "program_skill", "update_skill", "evolution_skill"]))
check("evolution_skill 已登记", registered("evolution_skill"))

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
