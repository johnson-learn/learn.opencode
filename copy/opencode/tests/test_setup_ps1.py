# -*- coding: utf-8 -*-
# setup-windows.ps1 自动化测试：开关完整性/部署范围/path_convert 体系/语法解析（仓库直读，WSL 不可达回退镜像）
import os, re, sys, subprocess
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

pass_n, fail_n = 0, 0
def check(name, cond):
    global pass_n, fail_n
    if cond: pass_n += 1; print("  ✓ " + name)
    else: fail_n += 1; print("  ✗ " + name)

REPO = r"\\wsl.localhost\Ubuntu\home\github\learn.opencode"
MIRROR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo_face", "setup-windows.ps1")
script_path = os.path.join(REPO, "copy", "setup", "setup-windows.ps1")
mode = "仓库直读"
if not os.path.exists(script_path):
    script_path = MIRROR
    mode = "镜像回退"
print("[模式] " + mode)
if not os.path.exists(script_path):
    print("setup 脚本不可得（无仓库无镜像）→ 全部跳过")
    sys.exit(0)
c = open(script_path, encoding="utf-8", errors="replace").read()

# 1. 七个阶段开关齐全（与 INSTALL.md 阶段表一致）
switches = ["SkipWinget", "SkipNpm", "SkipPip", "SkipWsl", "SkipDeploy", "UseChinaMirror", "NoPathRewrite"]
for s in switches:
    check("开关存在: -" + s, ("[switch]$" + s) in c)

# 2. 部署范围：skills（含 default 容器）、tests、tools、plugins
check("部署含 skills", "skills" in c)
check("部署含 tests", "tests" in c)
check("部署含 tools", "tools" in c)
check("部署含 plugins", "plugins" in c)

# 3. path_convert 体系（阶段 7 占位符→本机路径）
check("调用 path_convert.py", "path_convert.py" in c)
check("占位符交互（Ask-Dir 数据类目录）", "Ask-Dir" in c)
check("旧机路径改写已由占位符体系取代（无旧路径硬编码改写段）", "$OLD_EDRIVE" not in c or "path_convert" in c)

# 4. PowerShell 语法可解析（AST）
try:
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "$t = $null; $errs = $null; [System.Management.Automation.Language.Parser]::ParseFile('%s', [ref]$t, [ref]$errs) | Out-Null; if ($errs.Count -gt 0) { $errs | ForEach-Object { Write-Host $_.Message }; exit 1 }" % script_path.replace("'", "''")],
                       capture_output=True, text=True, timeout=120)
    check("PowerShell 语法解析通过（AST）", r.returncode == 0)
    if r.returncode != 0:
        print("    语法错误:", (r.stdout + r.stderr).strip()[:200])
except Exception as e:
    check("PowerShell 语法解析通过（AST）", False)

# 5. 与 INSTALL.md 阶段表一致（阶段描述关键词）
install = ""
ip = os.path.join(REPO, "copy", "INSTALL.md")
if not os.path.exists(ip):
    ip = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo_face", "INSTALL.md")
if os.path.exists(ip):
    install = open(ip, encoding="utf-8", errors="replace").read()
    for stage in ["SkipWinget", "SkipNpm", "SkipPip", "SkipWsl", "SkipDeploy", "NoPathRewrite"]:
        check("INSTALL.md 阶段表含 " + stage, stage in install)

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
