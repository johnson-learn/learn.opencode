# -*- coding: utf-8 -*-
# 仓库门面一致性测试：门面文件与框架现状对照（检查 WSL 仓库工作树；不存在则跳过）
import os, re, sys, subprocess
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

REPO = r"\\wsl.localhost\Ubuntu\home\github\learn.opencode"
if not os.path.exists(REPO):
    print("仓库工作树不可达（WSL 未运行）→ 跳过门面核查")
    sys.exit(0)

def rd(p):
    fp = os.path.join(REPO, p.replace("/", "\\"))
    if not os.path.exists(fp):
        return ""
    return open(fp, encoding="utf-8", errors="replace").read()

# 1. 门面文件存在
for f in ["README.md", "copy\\README.md", "copy\\INSTALL.md", "copy\\REQUIREMENTS.md"]:
    check("门面文件存在: " + f, os.path.exists(os.path.join(REPO, f)))

# 2. copy/README 技能清单与框架一致
r = rd("copy\\README.md")
check("copy/README 含 6 个 skill 说明", all(s in r for s in ["3gpp_skill", "files_skill", "find_skill", "program_skill", "update_skill", "evolution_skill"]))
check("copy/README 含 default 容器结构", "default" in r and "evolution_skill" in r)
check("copy/README 含进化门禁说明", "门禁" in r or "evolution_gate" in r)
check("copy/README 含无权限机器说明", "无权限机器" in r or "不需要执行 update_skill" in r)

# 3. INSTALL 关键步骤
i = rd("copy\\INSTALL.md")
check("INSTALL 含部署 tests/tools/plugins", all(x in i for x in ["tests", "tools", "plugins"]))
check("INSTALL 含 WEASYPRINT 环境变量", "WEASYPRINT_DLL_DIRECTORIES" in i)
check("INSTALL 含门禁验证", "evolution_gate" in i or "plugin-evolution.log" in i)

# 4. REQUIREMENTS 权威引用 + 新工具
q = rd("copy\\REQUIREMENTS.md")
check("REQUIREMENTS 指向 tools-manifest 权威", "tools-manifest.md" in q)
check("REQUIREMENTS 含 7 高价值工具关键词", all(x in q for x in ["playwright", "weasyprint", "ocrmypdf", "docxtpl"]))

# 5. 根 README 入口
root = rd("README.md")
check("根 README 含 6 个 skill 表述", "6 个 skill" in root or "6 个全局" in root)

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
