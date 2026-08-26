# -*- coding: utf-8 -*-
# docs-sync 映射表完整性测试：表结构 / 引用的校验测试文件存在 / 映射表被 regedit 与 AGENTS 引用
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CFG = os.path.join(os.path.expanduser("~"), ".config", "opencode")
pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

ds = open(os.path.join(CFG, "docs-sync.md"), encoding="utf-8").read()
reg = open(os.path.join(CFG, "regedit.md"), encoding="utf-8").read()
agents = open(os.path.join(CFG, "AGENTS.md"), encoding="utf-8").read()

# 1. 映射表结构与关键行
for sec in ["skill 新增", "测试用例新增", "工具新增", "流程/机制变更", "规则变更", "目录/结构变更", "插件变更"]:
    check("映射表含变更类型: " + sec, sec in ds)
check("映射表含校验方式列", "校验方式" in ds)

# 2. 映射表引用的校验测试文件实际存在
for t in ["test_instructions.py", "test_regedit.py", "test_tools_manifest.py",
          "test_evolution_consistency.py", "test_update_skill.py", "test_plugin.js"]:
    check("校验测试存在: " + t, os.path.exists(os.path.join(CFG, "tests", t)))

# 3. 映射表被 regedit.md 与 AGENTS.md 引用
check("regedit.md 登记 docs-sync.md", "docs-sync.md" in reg)
check("AGENTS.md 铁律引用 docs-sync.md", "docs-sync.md" in agents)

# 4. 映射表自身存在的文件引用抽查
check("映射表引用 instructions.md", "instructions.md" in ds)
check("映射表引用 evolution.md（规则变更行）", "evolution.md" in ds)
check("映射表引用 evolution_log.txt", "evolution_log.txt" in ds)

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
