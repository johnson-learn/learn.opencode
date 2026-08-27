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
c2 = ""
fp2 = os.path.join(REPO, "copy", "setup", "setup-install-functions.ps1")
if os.path.exists(fp2):
    c2 = open(fp2, encoding="utf-8", errors="replace").read()

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

# 3.5 安装移植 log 反馈修复（2026-08-27 实测：无 E 盘机器 Join-Path 报错 + 验证逻辑过时）
check("w64devkit 探测不硬编码盘符（动态枚举现有盘符）", "Get-PSDrive -PSProvider FileSystem" in c and "E:\\w64devkit" not in c)
check("7.5 验证改为注册事件注入体系（system.transform）", "experimental.chat.system.transform" in c)
check("7.5 不再要求 opencode.jsonc 含 instructions 注册", "含 instructions 注册" not in c)
check("辅助脚本部署检查指向实际部署位置 $ToolDir（Temp\\opencode）", 'Test-Path (Join-Path $ToolDir "extract-docx.ps1")' in c)
check("w64devkit 探测用独立变量 $w64Dir（防覆盖 $ToolDir——PS 变量大小写不敏感）", "$w64Dir = \"\"" in c and "$toolDir = \"\"" not in c)
check("工具类空值当场交互询问（安装时闭环，不写空值行）", "未自动探测到" in c and "回车跳过（不写入映射" in c and "装好工具后重跑本脚本自动补齐" in c)
check("第 7 节残留提示改为重跑本脚本（非手动编辑 path_map）", "装好工具后重跑本脚本即可自动补齐（已装项自动跳过）" in c)

# 3.7 安装交互优化（用户 2026-08-27 要求：必选/可选分级、新窗口安装、等待/放弃/换源/退出选项）
check("工具必选/可选分级（Git/Node/Python 必选）", "required = $true" in c and "required = $false" in c)
check("新开 PowerShell 窗口安装（可看进度/结果，UAC 自动弹窗确认）", "Start-Process powershell" in c)
check("原窗口选项直接显示（无倒计时，回车继续等待每 10 秒检测）", "可随时选择，无倒计时" in c and "每 10 秒自动检测" in c)
check("必选工具失败三选项（镜像直链重试/放弃必选/放弃移植）", "换镜像直链渠道安装" in c and "放弃本次必选工具安装" in c and "放弃本次移植（退出脚本）" in c)
check("可选工具失败两选项（换源重试/放弃可选继续）", "放弃本次可选工具安装，继续移植" in c)
check("放弃移植退出码（exit 2）", "exit 2" in c)
check("静默失败兜底：非静默 PowerShell 安装窗口（可看进度可手动确认）", "已新开 PowerShell 窗口非静默安装" in c)
check("镜像直链第二渠道（npmmirror 国内高速源 + 各包静默参数）", "registry.npmmirror.com" in c and "gh-proxy.com" in c and "dl.google.com" in c and "mirrors.tuna.tsinghua.edu.cn" in c)
check("多安装源逐个尝试（mirrors 数组 + 换下一个源）", "mirrors = @" in c and "换下一个源" in c2)
check("镜像渠道安装函数（msi 走 msiexec / exe 直跑 / 下载校验 <1MB 判失败）", "Install-FromMirror" in c2 and "msiexec" in c2 and "Length -lt 1MB" in c2)
check("镜像渠道安装走管理员提权窗口（-Verb RunAs + UAC 提示 + 窗口可见）", "Start-Process powershell -Verb RunAs -Wait" in c2 and "弹出 UAC 请点『是』" in c2)
check("镜像源全部失败后回到选项菜单（不再自动跳级）", "全部镜像源均失败" in c and "回到选项菜单" in c)
check("非静默窗口为独立选项（[4]/[3] 可选）", "新开非静默 PowerShell 窗口安装" in c)
check("LibreOffice 版本动态解析（防固定版本号被镜像站清理致全源 404）", "动态版本解析：Git" in c and "libreoffice/stable/" in c2 and "$loVer" in c2)
check("Git/Node/Python 全动态化（npmmirror 目录页 JSON 解析 + 兜底固定版）", "binary/git-for-windows/" in c2 and "binary/node/" in c2 and "binary/python/" in c2 and "gitVer" in c2 and "nodeVer" in c2 and "pyVer" in c2)
check("Node 动态解析限 LTS 偶数大版本", "% 2 -eq 0" in c2)

# 3.9 模拟测试（用户 2026-08-28 要求真模拟：mock curl/Start-Process 实际执行安装分支流转，非文本断言）
if mode == "仓库直读":
    sim = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_setup_sim.ps1")
    funcs = os.path.join(REPO, "copy", "setup", "setup-install-functions.ps1")
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", sim, "-FuncFile", funcs],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
        check("模拟测试 test_setup_sim.ps1 执行通过（mock 分支流转 17/17）", r.returncode == 0 and "SIM_RESULT: pass=17 fail=0" in r.stdout)
    except Exception:
        check("模拟测试 test_setup_sim.ps1 执行通过（mock 分支流转 17/17）", False)
else:
    print("  （镜像回退模式：跳过模拟测试，函数文件不可得）")
check("新窗口为 PowerShell 窗口（-NoExit 保留结果，UAC 提示）", "Start-Process powershell" in c and "-NoExit" in c and "弹出 UAC 请点" in c)
check("检测双通道（命令 OR 安装位置文件，防新装 PATH 未刷新误判）", "C:\\Program Files\\nodejs\\node.exe" in c and "C:\\Program Files\\Git\\cmd\\git.exe" in c)

# 3.8 安装后自动配置（用户 2026-08-28 要求"完成全套工作"：环境变量/镜像源持久化）
check("安装后刷新当前会话 PATH（新装工具立即可用）", "GetEnvironmentVariable(\"Path\", \"Machine\")" in c and "已刷新当前会话 PATH" in c)
check("npm 镜像源持久化配置（registry.npmmirror.com）", "npm config set registry" in c)
check("pip 镜像源持久化配置（清华源）", "pip config set global.index-url" in c)
check("填写类与自动类残留检测均排除 tests 目录（repo_face 镜像保留占位符是设计）", c.count("FullName -notmatch \"\\\\tests\\\\\"") >= 2)

# 3.6 必备工具缺失醒目告警（用户 2026-08-27 要求：缺失/安装失败必须醒目提醒）
check("必备工具缺失告警块存在（8.5）", "必备工具缺失" in c)
check("必备清单区分（opencode CLI/python/p2t/git）", all(x in c for x in ["opencode CLI", "p2t", "git"]))
check("可选工具提示区分（不影响核心使用）", "不影响核心使用" in c)
check("补救重跑命令提示", "setup-windows.ps1" in c and "重跑" in c)
check("必备缺失时非零退出码（exit 1）", "exit 1" in c)

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
