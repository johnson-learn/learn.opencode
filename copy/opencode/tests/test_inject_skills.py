# -*- coding: utf-8 -*-
# inject_skills.py 自动化测试：default 容器平铺/description 改写/幂等重注入
import os, re, shutil, subprocess, sys, tempfile
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

pass_n, fail_n = 0, 0
def check(name, cond, extra=""):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name + ("  [" + extra + "]" if extra else ""))

INJECT = os.path.join(os.path.expanduser("~"), ".config", "opencode", "tools", "inject_skills.py")
tmp = tempfile.mkdtemp(prefix="inject_test_")
proj = os.path.join(tmp, "proj")
os.makedirs(proj)

# 1. 首次注入
r = subprocess.run([sys.executable, INJECT, proj], capture_output=True, encoding="utf-8", errors="replace", timeout=120)
check("首次注入 rc=0", r.returncode == 0, str(r.returncode))
skills_dir = os.path.join(proj, ".opencode", "skills")
names = sorted(d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d)))
check("注入 6 个 skill", names == ["3gpp_skill", "evolution_skill", "files_skill", "find_skill", "program_skill", "update_skill"], str(names))
check("default 容器平铺（evolution_skill 在项目 skills 根）", "evolution_skill" in names)

# 2. description 改写（仅显式触发 → 默认触发）
c = open(os.path.join(skills_dir, "files_skill", "SKILL.md"), encoding="utf-8").read()
check("description 改写为默认触发（项目级副本标记）", "项目级副本" in c and "默认触发" in c)
check("全局仅显式声明已移除", "仅显式触发，不靠关键词自动调用" not in c)

# 3. 幂等重注入
r2 = subprocess.run([sys.executable, INJECT, proj], capture_output=True, encoding="utf-8", errors="replace", timeout=120)
check("重复注入幂等（rc=0）", r2.returncode == 0)
names2 = sorted(d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d)))
check("重复注入后仍 6 个（无残留目录）", names2 == names, str(names2))

# 4. 覆盖更新同步：项目副本被修改后重注入恢复为全局版
victim = os.path.join(skills_dir, "files_skill", "SKILL.md")
with open(victim, "a", encoding="utf-8") as f:
    f.write("\n<!-- LOCAL_EDITION_MARK -->\n")
r3 = subprocess.run([sys.executable, INJECT, proj], capture_output=True, encoding="utf-8", errors="replace", timeout=120)
c3 = open(victim, encoding="utf-8").read()
check("重注入覆盖项目本地改动（同步全局版）", "LOCAL_EDITION_MARK" not in c3)

shutil.rmtree(tmp, ignore_errors=True)
print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
