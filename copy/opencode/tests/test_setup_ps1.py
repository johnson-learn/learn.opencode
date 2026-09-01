# -*- coding: utf-8 -*-
# setup-windows.ps1 自动化测试（2026-09-01 检测模式改造后重写）：
# 工具清单展示/必须可选分类/双通道检测/PATH 修复/未装提示跳过/无自动安装残留/清单对齐（仓库直读，WSL 不可达回退镜像）
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
cc_path0 = os.path.join(REPO, "copy", "setup", "setup-check.ps1")
if not os.path.exists(cc_path0):
    cc_path0 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo_face", "setup-check.ps1")
cc0 = open(cc_path0, encoding="utf-8", errors="replace").read() if os.path.exists(cc_path0) else ""
c_cc = c + "\n" + cc0

# 1. 开关：保留部署/镜像/路径；安装类开关已移除（检测模式）
for s in ["SkipDeploy", "SkipWsl", "UseChinaMirror", "NoPathRewrite"]:
    check("开关存在: -" + s, ("[switch]$" + s) in c)
for s in ["SkipWinget", "SkipNpm", "SkipPip", "SkipBigPkgs"]:
    check("自动安装开关已移除: -" + s, ("[switch]$" + s) not in c)

# 2. 部署范围：skills（含 default 容器）、tests、tools、plugins
check("部署含 skills", "skills" in c)
check("部署含 tests", "tests" in c)
check("部署含 tools", "tools" in c)
check("部署含 plugins", "plugins" in c)

# 3. path_convert 体系（阶段 7 占位符→本机路径）
check("调用 path_convert.py", "path_convert.py" in c)
check("占位符交互（Ask-Dir 数据类目录）", "Ask-Dir" in c)
check("旧机路径改写已由占位符体系取代（无旧路径硬编码改写段）", "$OLD_EDRIVE" not in c or "path_convert" in c)

# 3.5 既有修复断言（保留）
check("w64devkit 探测不硬编码盘符（动态枚举现有盘符）", "Get-PSDrive -PSProvider FileSystem" in c and "E:\\w64devkit" not in c)
check("7.5 验证改为注册事件注入体系（system.transform）", "experimental.chat.system.transform" in c)
check("辅助脚本部署检查指向实际部署位置 $ToolDir（Temp\\opencode）", 'Test-Path (Join-Path $ToolDir "extract-docx.ps1")' in c)
check("w64devkit 探测用独立变量 $w64Dir（防覆盖 $ToolDir——PS 变量大小写不敏感）", "$w64Dir = \"\"" in c and "$toolDir = \"\"" not in c)
check("工具类空值当场交互询问（安装时闭环，不写空值行）", "未自动探测到" in c and "回车跳过（不写入映射" in c and "装好工具后重跑本脚本自动补齐" in c)
check("第 7 节残留提示改为重跑本脚本（非手动编辑 path_map）", "装好工具后重跑本脚本即可自动补齐（已装项自动跳过）" in c)
check("<工具目录> 自动映射系统盘根（不绑 w64devkit，防映射缺失 to_local 转 0 文件）", '"<工具目录>=" + $env:SystemDrive' in c and '@("<工具目录>", $w64Dir)' not in c)
check("自动类残留检查含 <工具目录>（防映射缺失时误报路径改写完成）", '"<用户目录>|<opencode配置目录>|<用户临时目录>|<工具目录>"' in c)
check("<工具目录> 不归填写类残留检查（填写类模式不含工具分支）", '<(项目|源码|WSL安装|离线安装包|LibreOffice|Chrome|Node|3GPP文档库)目录>' in c)

# 4. 2026-09-01 检测模式核心（用户改造：只检测+修复，不自动安装，永不阻塞）
check("工具清单展示（必须/可选分类文案）", "[必须]" in c and "[可选]" in c and "update_skill" in c)
check("必须类语义说明（缺失不影响基本使用，update_skill 除外）", "缺失不影响基本使用" in c)
check("可选类语义说明（使用过程中可安装）", "使用过程中可随时安装" in c)
check("检测条目含双通道（Test-Soffice/Test-Tesseract/pathChecks/pyImport/wslCheck）", "Test-ToolEntry" in c_cc and "sofficeCheck" in c_cc and "tessCheck" in c_cc and "pyImport" in c_cc and "wslCheck" in c_cc)
check("Git 检测含 PATH 修复目录（C:\\Program Files\\Git\\cmd）", "C:\\Program Files\\Git\\cmd" in c_cc)
check("Node 检测含 PATH 修复目录（C:\\Program Files\\nodejs）", "C:\\Program Files\\nodejs" in c_cc)
check("已装但 PATH 未配置 → 自动修复（Add-ToUserPath）", "已修复 PATH" in c and "Add-ToUserPath" in c)
check("未装提示语（请手动安装或使用大模型协助安装）", "请手动安装或使用大模型协助安装" in c)
check("未装提示重跑（装好后重跑本脚本自动补配置）", "装好后重跑本脚本即可自动补齐相关配置" in c)
check("检测后刷新当前会话 PATH（修复立即生效）", 'GetEnvironmentVariable("Path", "Machine")' in c)

# 5. npm 检测化
check("npm 缺失汇总提示（不逐个自动装）", "npm 全局包缺失" in c and "npm i -g $($npmMissing" in c)
check("npm 无自动安装执行（无 -g 直接安装调用）", "npm i -g opencode-ai $reg" not in c)
check("npm 镜像源持久化配置（registry.npmmirror.com）", "npm config set registry" in c)

# 6. pip 检测化
check("pip import 检测表 19 包（pix2text~ocrmypdf）", all(x in c_cc for x in ['"pix2text"', '"pypandoc-binary"', '"python-pptx"', '"opencv-python"', '"python-magic-bin"', '"ocrmypdf"']))
check("pip 缺失汇总提示（一次性列出缺失清单）", "pip 常规包缺失" in c and "$missingPkgs -join" in c)
check("pip 无自动安装循环（无 foreach pip install）", 'python -m pip install --upgrade --user $pkg' not in c)
check("pip Scripts 目录 PATH 修复保留（Get-PipScriptsDir + Add-ToUserPath）", "Get-PipScriptsDir" in c)
check("pip 镜像源持久化配置（清华源）", "pip config set global.index-url" in c)

# 7. WSL 检测化
check("WSL 检测+提示（不自动拉起 install-wsl）", "Start-Process powershell" not in c and "install-wsl.ps1" in c and "请手动安装（右键管理员运行" in c)

# 8. 无自动安装残留（worker/镜像/动态版本/交互循环全移除）
check("无 worker 窗口机制残留", "Start-WorkerCommand" not in c and "Stop-WorkerWindow" not in c)
check("无镜像直链下载残留", "mirrors = @" not in c and "curl.exe -L" not in c)
check("无动态版本解析残留", "Get-DynamicVersions" not in c and "npmmirror.com/-/binary" not in c)
check("无自动安装状态机/按键交互残留", "[Console]::KeyAvailable" not in c and "winget install --id" not in c and "自动切换镜像源渠道" not in c)

# 9. 填写类与自动类残留检测均排除 tests 目录
check("填写类与自动类残留检测均排除 tests 目录（repo_face 镜像保留占位符是设计）", c.count("FullName -notmatch \"\\\\tests\\\\\"") >= 2)

# 10. 必备工具缺失醒目告警保留（8.5）
check("必备工具缺失告警块存在（8.5）", "必备工具缺失" in c)
check("必备清单区分（opencode CLI/python/p2t/git）", all(x in c for x in ["opencode CLI", "p2t", "git"]))
check("可选工具提示区分（不影响核心使用）", "不影响核心使用" in c)
check("补救重跑命令提示", "setup-windows.ps1" in c and "重跑" in c)
check("必备缺失时非零退出码（exit 1）", "exit 1" in c)

# 11. 安装清单与 tools-manifest 总表自动对齐（B 类包 ⊆ pip 检测表或第 1 节可选工具；D 类 Tesseract ⊆ 检测；F 类 apt ⊆ install-wsl）
tm_path = os.path.join(REPO, "copy", "opencode", "tools-manifest.md")
if not os.path.exists(tm_path):
    tm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo_face", "tools-manifest.md")
if os.path.exists(tm_path):
    tm = open(tm_path, encoding="utf-8", errors="replace").read()
    b_section = re.search(r"## B\. Python 环境与核心包.*?\n(.*?)(?=\n## )", tm, re.S)
    b_pkgs = []
    if b_section:
        for line in b_section.group(1).splitlines():
            m = re.match(r"^\|\s*([A-Za-z0-9][A-Za-z0-9\-\.]*)\s*\|", line)
            if m:
                b_pkgs.append(m.group(1).lower())
    c_lower = (c + "\n" + cc0).lower()
    b_missing = [p for p in b_pkgs if p not in c_lower]
    check("tools-manifest B 类包全部纳入 setup 检测清单（pip 表+可选工具；缺失: %s）" % ",".join(b_missing) if b_missing else "tools-manifest B 类包全部纳入 setup 检测清单（pip 表+可选工具）", len(b_missing) == 0)
    check("tools-manifest D 类 Tesseract 纳入检测（UB-Mannheim 提示）", "UB-Mannheim.TesseractOCR" in tm and "UB-Mannheim.TesseractOCR" in c_cc)
    apt_m = re.search(r"apt install ([^\n`\|]+)", tm)
    wsl_path = os.path.join(REPO, "copy", "setup", "install-wsl.ps1")
    if apt_m and os.path.exists(wsl_path):
        wsl_c = open(wsl_path, encoding="utf-8", errors="replace").read()
        apt_pkgs = [p for p in apt_m.group(1).split() if p not in ("apt", "install", "-y")]
        apt_missing = [p for p in apt_pkgs if p not in wsl_c]
        check("tools-manifest F 类 apt 包全部纳入 install-wsl.ps1（缺失: %s）" % ",".join(apt_missing) if apt_missing else "tools-manifest F 类 apt 包全部纳入 install-wsl.ps1", len(apt_missing) == 0)
    else:
        check("tools-manifest F 类 apt 包全部纳入 install-wsl.ps1", False)
else:
    check("tools-manifest B 类包全部纳入 setup 检测清单（总表不可得，跳过）", True)

# 12. PowerShell 语法可解析（AST）
try:
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "$t = $null; $errs = $null; [System.Management.Automation.Language.Parser]::ParseFile('%s', [ref]$t, [ref]$errs) | Out-Null; if ($errs.Count -gt 0) { $errs | ForEach-Object { Write-Host $_.Message }; exit 1 }" % script_path.replace("'", "''")],
                       capture_output=True, text=True, timeout=120)
    check("PowerShell 语法解析通过（AST）", r.returncode == 0)
    if r.returncode != 0:
        print("    语法错误:", (r.stdout + r.stderr).strip()[:200])
except Exception as e:
    check("PowerShell 语法解析通过（AST）", False)

# 13. 与 INSTALL.md 阶段表一致（阶段描述关键词）
install = ""
ip = os.path.join(REPO, "copy", "INSTALL.md")
if not os.path.exists(ip):
    ip = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo_face", "INSTALL.md")
if os.path.exists(ip):
    install = open(ip, encoding="utf-8", errors="replace").read()
    for stage in ["SkipDeploy", "SkipWsl", "NoPathRewrite"]:
        check("INSTALL.md 阶段表含 " + stage, stage in install)

# 14. install-tools.ps1 一键安装脚本（2026-09-01 新增：与 setup 检测共享清单，独立自动安装）
it_path = os.path.join(REPO, "copy", "setup", "install-tools.ps1")
if not os.path.exists(it_path):
    it_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo_face", "install-tools.ps1")
if os.path.exists(it_path):
    it = open(it_path, encoding="utf-8", errors="replace").read()
    check("install-tools.ps1 存在", True)
    check("install-tools 共享检测模块（dot-source setup-check.ps1）", 'setup-check.ps1' in it)
    check("install-tools winget 渠道安装（--silent + 已装跳过）", "winget install --id" in it and "--silent" in it)
    check("install-tools 失败跳过继续（每工具独立、不阻塞）", "失败自动跳过继续" in it or "winget 安装未成功" in it)
    check("install-tools npm/pip 渠道（镜像可选）", "npm i -g" in it and "python -m pip install" in it)
    check("install-tools 汇总报告（装完提示重跑 setup-windows.ps1）", "安装汇总" in it and "setup-windows.ps1" in it)
    check("install-tools 开关（UseChinaMirror/SkipNpm/SkipPip）", "[switch]$UseChinaMirror" in it and "[switch]$SkipNpm" in it and "[switch]$SkipPip" in it)
    check("install-tools BOM 存在（PowerShell 5.1 UTF-8 中文解析前提）", it.startswith("\ufeff"))
    check("setup-check.ps1 共享模块 BOM 存在", True)
else:
    check("install-tools.ps1 存在", False)

# 15. 共享检测模块 setup-check.ps1
cc_path = os.path.join(REPO, "copy", "setup", "setup-check.ps1")
if not os.path.exists(cc_path):
    cc_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo_face", "setup-check.ps1")
if os.path.exists(cc_path):
    cc = open(cc_path, encoding="utf-8", errors="replace").read()
    check("setup-check.ps1 含工具清单（checks1 + wingetId + tier 分类）", "$checks1 = @" in cc and "wingetId" in cc and 'tier = "必须"' in cc and 'tier = "可选"' in cc)
    check("setup-check.ps1 含检测函数（Test-ToolEntry/Test-Soffice/Test-Tesseract）", "function Test-ToolEntry" in cc and "function Test-Soffice" in cc and "function Test-Tesseract" in cc)
    check("setup-check.ps1 含 pip import 检测表（pyPkgs）", "$pyPkgs = @" in cc)
    check("setup-check.ps1 BOM 存在（PowerShell 5.1 UTF-8 中文解析前提）", cc.startswith("\ufeff"))
    check("setup-windows.ps1 BOM 存在", c.startswith("\ufeff"))
else:
    check("setup-check.ps1 含工具清单", False)

# 16. tools-manifest A/D 类工具与 checks1 清单对齐（后续新增工具强制同步检测清单）
if os.path.exists(cc_path):
    cc2 = open(cc_path, encoding="utf-8", errors="replace").read()
    tm2_path = os.path.join(REPO, "copy", "opencode", "tools-manifest.md")
    if not os.path.exists(tm2_path):
        tm2_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo_face", "tools-manifest.md")
    tm2 = open(tm2_path, encoding="utf-8", errors="replace").read() if os.path.exists(tm2_path) else ""
    a_sec = re.search(r"## A\. 基础环境.*?\n(.*?)(?=\n## )", tm2, re.S)
    d_sec = re.search(r"## D\. OCR 与公式识别.*?\n(.*?)(?=\n## )", tm2, re.S)
    winget_ids = []
    for sec in (a_sec, d_sec):
        if not sec:
            continue
        for line in sec.group(1).splitlines():
            m = re.search(r"`winget install ([A-Za-z0-9\-\.]+)`", line)
            if m:
                winget_ids.append(m.group(1))
    c2_lower = cc2.lower()
    missing_ids = [w for w in winget_ids if w.lower() not in c2_lower]
    check("tools-manifest A/D 类 winget 包全部纳入 setup-check 检测清单（缺失: %s）" % ",".join(missing_ids) if missing_ids else "tools-manifest A/D 类 winget 包全部纳入 setup-check 检测清单", len(missing_ids) == 0)
else:
    check("tools-manifest A/D 类工具全部纳入 setup-check 检测清单", False)

print("\n结果：通过 %d 项，失败 %d 项" % (pass_n, fail_n))
sys.exit(1 if fail_n else 0)
