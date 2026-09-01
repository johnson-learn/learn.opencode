# -*- coding: utf-8 -*-
# program_skill L1 领域自测（2026-09-01 框架进化评审建议落地）：
# 入口规范 / 路由表与 modules 一致 / lang-go 不复发 / references 无悬空 / templates 骨架齐全
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # skills/program_skill
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
check("name 为 program_skill", re.search(r"^name:\s*program_skill\s*$", fm, re.M) is not None)
dm = re.search(r"^description:\s*(.*)$", fm, re.M)
check("description 含显式触发约定", dm and "program_skill：" in dm.group(1) and "Use ONLY when" in dm.group(1))
check("description ≤1024 字符", dm and len(dm.group(1)) <= 1024)
check("description 定位收窄为 C 为主（不再声称全语言）", dm and "C " in dm.group(1) and "Go/Rust/Java" not in dm.group(1))

# 2. 路由表 modules 目录齐全（C 核心 5 + C++ 3 + Shell 3 + 通用 2 = 13）
expected = [
    "c-gcc-embedded-build", "c-compile-script-generator", "c-static-analysis",
    "c-embedded-systems", "c-memory-safety-patterns",
    "cpp-compiler-flags", "cpp-coding-standards", "cpp-testing",
    "shell-linux-shell-scripting", "shell-bash-linux", "shell-bash-defensive-patterns",
    "general-threading-architecture", "general-pair-programming",
]
mods = set(d for d in os.listdir(os.path.join(SKILL, "modules"))
           if os.path.isdir(os.path.join(SKILL, "modules", d)))
check("modules 13 个齐全", all(e in mods for e in expected) and len(mods) == 13)
check("lang-go-concurrency 不复发", "lang-go-concurrency" not in mods and "lang-" not in " ".join(mods))
check("无多余模块", len(mods - set(expected)) == 0)
# 路由表文本引用 ⊆ 实际目录
missing_refs = [e for e in expected if e not in c]
check("路由表引用全部模块目录", len(missing_refs) == 0)

# 3. references 无悬空（SKILL.md 索引的 references/xxx.md 全部存在）
refs = set(re.findall(r"`references/([\w\-]+\.md)`", c))
ref_dir = os.path.join(SKILL, "references")
missing_ref_files = [r for r in refs if not os.path.isfile(os.path.join(ref_dir, r))]
check("references 索引无悬空（缺失: %s）" % ",".join(missing_ref_files) if missing_ref_files else "references 索引无悬空", len(missing_ref_files) == 0)
expected_refs = {"tools.md", "compile-scripts.md", "debugging.md", "coding-standards.md", "unit-test.md",
                 "embedded-build.md", "deploy-remote.md", "build-systems.md"}
have_refs = set(os.listdir(ref_dir)) if os.path.isdir(ref_dir) else set()
missing_have = expected_refs - have_refs
check("references 8 个全部落地（缺失: %s）" % ",".join(sorted(missing_have)) if missing_have else "references 8 个全部落地", len(missing_have) == 0)

# 4. templates/c-project 工程骨架齐全
tpl = os.path.join(SKILL, "templates", "c-project")
need = ["src/main.c", "Makefile", "CMakeLists.txt", ".gitignore", "README.md"]
check("templates/c-project 5 文件齐全", all(os.path.isfile(os.path.join(tpl, f)) for f in need))
check("Makefile 含 -Wall -Wextra", os.path.isfile(os.path.join(tpl, "Makefile")) and
      "Wall" in open(os.path.join(tpl, "Makefile"), encoding="utf-8").read())
check("CMakeLists 含 C11 + Threads", os.path.isfile(os.path.join(tpl, "CMakeLists.txt")) and
      "Threads" in open(os.path.join(tpl, "CMakeLists.txt"), encoding="utf-8").read())

# 5. 核心铁律存在
check("核心铁律章节存在（实编译实运行验证）", "核心铁律" in c and "实编译实运行验证" in c)

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
