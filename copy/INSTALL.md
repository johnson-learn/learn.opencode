# INSTALL.md — 新电脑安装指南

适用：Windows 10/11 办公电脑（x64），从零复现本工作环境。

## 方式 A：一键脚本（推荐）

```powershell
# 克隆仓库（或解压 zip）
git clone <仓库地址>
进入\copy\setup

# 一键安装：软件 + npm/pip 源 + WSL + 部署 skill/配置/脚本 + 路径自动改写
powershell.exe -NoProfile -ExecutionPolicy Bypass -File setup-windows.ps1 -UseChinaMirror
```

脚本各阶段说明（均可单独跳过）：

| 阶段 | 开关 | 内容 |
|---|---|---|
| 1 基础软件 | `-SkipWinget` | Git / Node.js LTS / Python 3.12 / Chrome / LibreOffice（winget 静默安装，已装的自动跳过） |
| 2 npm 源 | `-SkipNpm` | opencode-ai、@mermaid-js/mermaid-cli（`-UseChinaMirror` 走 npmmirror） |
| 3 pip 源 | `-SkipPip` | pix2text、matplotlib、PyMuPDF、pillow（`-UseChinaMirror` 走清华源） |
| 4 WSL | `-SkipWsl` | 调起 `install-wsl.ps1`（管理员窗口；可能需要重启一次） |
| 5~6 部署 | `-SkipDeploy` | 复制 skill/配置/tests/tools 到 `~\.config\opencode\`；辅助脚本到 `%LOCALAPPDATA%\Temp\opencode\` |
| 6.5~7 路径配置 | `-NoPathRewrite` | 自动探测工具类目录（LibreOffice/Chrome/Node/WSL）+ 数据类目录交互选择（默认/定制）+ path_convert.py 占位符转本机真实路径 |

安装完成后：
1. 重启终端 / opencode
2. 首次使用 p2t 会下载模型（约 1~2 GB），慢网先设 `$env:HF_ENDPOINT = "https://hf-mirror.com"`
3. mmdc 渲染前设 `$env:PUPPETEER_EXECUTABLE_PATH` 指向系统 Chrome（skill 中有记载）
4. WeasyPrint 需设用户环境变量 `WEASYPRINT_DLL_DIRECTORIES=C:\msys64\ucrt64\bin`（MSYS2 已装 GTK 后）

## 方式 B：手动安装（脚本不可用时按此操作）

顺序与命令见 `REQUIREMENTS.md`（① 软件、② npm、③ pip、④ WSL、⑤ 数据）。

手动部署三步：

```powershell
# 1) 部署 skill 与配置
robocopy opencode\skills "%USERPROFILE%\.config\opencode\skills" /E
copy opencode\opencode.jsonc "%USERPROFILE%\.config\opencode\"
copy opencode\AGENTS.md      "%USERPROFILE%\.config\opencode\"
copy opencode\instructions.md "%USERPROFILE%\.config\opencode\"
copy opencode\regedit.md     "%USERPROFILE%\.config\opencode\"
copy opencode\docs-sync.md   "%USERPROFILE%\.config\opencode\"
copy opencode\tools-manifest.md "%USERPROFILE%\.config\opencode\"
copy opencode\package.json   "%USERPROFILE%\.config\opencode\"

# 2) 部署辅助脚本（skill 引用路径约定 %LOCALAPPDATA%\Temp\opencode）
robocopy scripts "%LOCALAPPDATA%\Temp\opencode" /E

# 3) 部署测试与修炼工具
robocopy opencode\tests "%USERPROFILE%\.config\opencode\tests" /E
robocopy opencode\tools  "%USERPROFILE%\.config\opencode\tools" /E
robocopy opencode\plugins "%USERPROFILE%\.config\opencode\plugins" /E
```

> 手动部署后，需运行 `python "%USERPROFILE%\.config\opencode\tools\path_convert.py" to_local` 完成占位符→本机路径转换（数据类目录在 path_map.txt 中维护；脚本方式 A 的"阶段 6.5~7"会自动完成）。

## 验证清单

1. 重启 opencode，会话创建时应 toast 展示全局技能清单（6 个 skill）
2. 按 `tools-manifest.md` 逐类检查工具（A~G 检查命令）
3. 跑测试自检：`python "%USERPROFILE%\.config\opencode\tests\skill_validate.py" "%USERPROFILE%\.config\opencode\skills"`，其余用例见 `tests\README.md`
4. 进化门禁：会话结束后查 `plugins\plugin-evolution.log` 应有 evolution_gate 记录
5. 首次 update_skill 需指出同步目标目录

## 双向同步说明（多机使用）

- **有权限机器**：执行 update_skill（五步：吸收远端→修改→自测→弹窗确认→推送）维护框架
- **无权限机器**：只需 `git pull` 获取更新后重启 opencode；不需要执行 update_skill 修改（推送门禁在弹窗确认环节，不会误触）
