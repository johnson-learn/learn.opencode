# INSTALL.md — 新电脑安装指南

适用：Windows 10/11 办公电脑（x64），从零复现本工作环境。

## 方式 A：一键脚本（推荐）

```powershell
# 克隆仓库（或解压 zip）
git clone <仓库地址> copy
cd copy

# 一键安装：工具清单检测（不自动安装）+ 部署 skill/配置/脚本 + 路径自动改写
powershell -NoProfile -ExecutionPolicy Bypass -File setup\setup-windows.ps1 -UseChinaMirror
```

> **脚本模式（2026-09-01 改造）**：只检测+修复配置，**不自动安装任何工具**，永不被安装失败阻塞——
> ① 先展示全部工具清单（必须/可选分类）；② 逐项检测是否已安装；③ 已装但 PATH 未配置 → 自动修复；
> ④ 未安装 → 提示（含建议命令，可手动或请大模型安装）后跳过继续；⑤ 后续相关配置跳过并在收尾提示"装好后重跑本脚本自动补齐"。
>
> **一键自动安装**（可选）：检测后想自动装缺失工具，运行：
> ```powershell
> powershell -NoProfile -ExecutionPolicy Bypass -File setup\install-tools.ps1 -UseChinaMirror
> ```
> winget 渠道装基础软件（每工具独立、失败跳过继续）+ npm/pip 渠道装包，收尾汇总失败清单；装完重跑 setup-windows.ps1 补齐配置。二者共用 `setup\setup-check.ps1` 检测清单（tools-manifest 总表自动对齐）。

脚本各阶段说明：

| 阶段 | 开关 | 内容 |
|---|---|---|
| 1 工具清单与检测 | — | 展示清单：**[必须]**（缺失不影响基本使用，update_skill 双向同步除外）Git / Node.js / Python 3.12 / opencode CLI / pip 常规包集 / WSL2+Ubuntu；**[可选]**（使用过程中可随时安装）Chrome / LibreOffice / Tesseract OCR / mermaid-cli / playwright / weasyprint。逐项双通道检测（命令 OR 安装位置），已装但 PATH 未配置自动修复，未装提示建议命令后跳过 |
| 2 npm 检测 | — | opencode-ai、@mermaid-js/mermaid-cli 缺失汇总提示（`-UseChinaMirror` 提示走 npmmirror 并持久化镜像源） |
| 3 pip 检测 | — | tools-manifest B 类 19 包逐包 import 检测，缺失一次性汇总提示补装命令（`-UseChinaMirror` 走清华源并持久化）；已装 Python 时自动把 pip Scripts 目录加入用户 PATH |
| 4 WSL | `-SkipWsl` | 检测 Ubuntu 发行版；未装提示手动右键管理员运行 `setup\install-wsl.ps1`（含 WSL 内 Linux 工具链，可能需重启） |
| 5~6 部署 | `-SkipDeploy` | 复制 skill/配置/tests/tools 到 `~\.config\opencode\`；辅助脚本到 `%LOCALAPPDATA%\Temp\opencode\` |
| 6.5~7 路径配置 | `-NoPathRewrite` | 自动探测工具类目录（未装工具跳过并提示重跑）+ 数据类目录交互选择 + path_convert.py 占位符转本机真实路径 |

安装完成后：
1. 重启终端 / opencode
2. 首次使用 p2t 会下载模型（约 1~2 GB），慢网先设 `$env:HF_ENDPOINT = "https://hf-mirror.com"`
3. mmdc 渲染前设 `$env:PUPPETEER_EXECUTABLE_PATH` 指向系统 Chrome（skill 中有记载）
4. WeasyPrint 需用户环境变量 `WEASYPRINT_DLL_DIRECTORIES=<工具目录>msys64\ucrt64\bin`（未装时脚本已提示手动安装步骤）
5. 有工具未装被提示时：按提示命令安装（可请大模型协助）后重跑本脚本自动补齐配置（已装项自动跳过）

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
