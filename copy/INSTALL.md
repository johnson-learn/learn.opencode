# INSTALL.md — 新电脑安装指南

适用：Windows 10/11 办公电脑（x64），从零复现本工作环境。

## 方式 A：一键脚本（推荐）

```powershell
# 克隆仓库（或解压 zip）
git clone <仓库地址> copy
cd copy

# 一键安装：软件 + npm/pip 包 + WSL + 部署 skill/配置/脚本 + 路径自动改写
powershell -NoProfile -ExecutionPolicy Bypass -File setup\setup-windows.ps1 -UseChinaMirror
```

脚本各阶段说明（均可单独跳过）：

| 阶段 | 开关 | 内容 |
|---|---|---|
| 1 基础软件 | `-SkipWinget` | Git / Node.js LTS / Python 3.12 / Chrome / LibreOffice（winget 静默安装，已装的自动跳过） |
| 2 npm 包 | `-SkipNpm` | opencode-ai、@mermaid-js/mermaid-cli（`-UseChinaMirror` 走 npmmirror） |
| 3 pip 包 | `-SkipPip` | pix2text、matplotlib、PyMuPDF、pillow（`-UseChinaMirror` 走清华源） |
| 4 WSL | `-SkipWsl` | 调起 `install-wsl.ps1`（管理员窗口；可能需要重启一次） |
| 5~6 部署 | `-SkipDeploy` | 复制 skill/配置到 `~\.config\opencode\`；辅助脚本到 `%LOCALAPPDATA%\Temp\opencode\` |
| 7 路径改写 | `-NoPathRewrite` | 把 skill 文本中旧机路径（`C:\Users\job_p\...`、`E:\openCodeDefault\temp`）替换为新机实际路径 |

安装完成后：
1. 重启终端 / opencode；
2. 首次使用 p2t 会下载模型（约 1~2 GB），慢网先设 `$env:HF_ENDPOINT = "https://hf-mirror.com"`；
3. mmdc 渲染前设 `$env:PUPPETEER_EXECUTABLE_PATH` 指向系统 Chrome（skill 中有记载）。

## 方式 B：手动安装（脚本不可用时按此操作）

顺序与命令见 `REQUIREMENTS.md`（§1 软件、§2 npm、§3 pip、§4 WSL、§5 数据）。

手动部署两步：
```powershell
# 1) 部署 skill 与配置
robocopy opencode\skills "%USERPROFILE%\.config\opencode\skills" /E
copy opencode\opencode.jsonc "%USERPROFILE%\.config\opencode\"
copy opencode\instructions.md "%USERPROFILE%\.config\opencode\"
copy opencode\evolution.md  "%USERPROFILE%\.config\opencode\"
copy opencode\package.json  "%USERPROFILE%\.config\opencode\"

# 2) 部署辅助脚本（skill 引用路径约定为 %LOCALAPPDATA%\Temp\opencode）
robocopy scripts "%LOCALAPPDATA%\Temp\opencode" /E
```
> 手动部署后，若新电脑用户名不是 `job_p`，需自行把 skill 与脚本里的旧路径全局替换为新路径（脚本方式 A 的"阶段 7"会自动完成这一步）。

## 验证清单

```powershell
opencode --version          # opencode CLI
mmdc -V                     # mermaid-cli
python --version            # 3.12
p2t predict --help          # pix2text
wsl -l -v                   # Ubuntu-22.04 VERSION=2
Test-Path "$env:USERPROFILE\.config\opencode\skills\3gpp_skill\SKILL.md"   # True
Test-Path "$env:LOCALAPPDATA\Temp\opencode\extract-docx.ps1"               # True
```

## 常见问题

| 问题 | 处理 |
|---|---|
| winget 不存在 | 商店安装"应用安装程序"，或直接官网下载各软件手动装 |
| winget 装 Python 后 PATH 无 python | 重启终端；仍无则手动把 Python 与 `Scripts` 目录加入 PATH |
| p2t 模型下载失败 | 设 `HF_ENDPOINT=https://hf-mirror.com`；或从旧机拷贝 `p2t-models` 目录 |
| mmdc 报无 Chrome | 设 `$env:PUPPETEER_EXECUTABLE_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"` |
| WSL 商店渠道失败 | 用 `curl.exe -L -o ubuntu2204.appx https://aka.ms/wslubuntu2204` + `Add-AppxPackage`（见 REQUIREMENTS.md §4） |
| 3GPP 文档缺失 | 跑 `setup\download-specs.ps1`；再用 `scripts\extract-docx.ps1` 生成文本索引 |
