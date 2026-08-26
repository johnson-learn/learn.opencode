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
| 6.5~7 路径配置 | `-NoPathRewrite` | 自动探测工具类目录（LibreOffice/Chrome/Node/WSL）+ 数据类目录交互选择（默认/定制）+ path_convert.py 占位符转本机真实路径 |

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
> 手动部署后，需运行 `python "%USERPROFILE%\.config\opencode\tools\path_convert.py" to_local` 完成占位符→本机路径转换（数据类目录在 path_map.txt 中维护；脚本方式 A 的"阶段 6.5~7"会自动完成）。

## 验证清单

1. 重启 opencode，会话创建时应 toast 展示全局技能清单
2. 按 `tools-manifest.md` 逐类检查工具（A~G 检查命令）
3. 跑测试自检：`python "%USERPROFILE%\.config\opencode\tests\skill_validate.py" "%USERPROFILE%\.config\opencode\skills"`，其余用例见 `tests\README.md`
4. 首次 update_skill 需指出同步目标目录

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
| pip 装 pix2text 报 `OSError ... No such file or directory`（torch 路径过长） | Windows 长路径未启用。以管理员运行：`reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f` 后重启重试 |
| 系统里是 Microsoft Store 版 Python | 其 `--user` 目录路径极长易触发 torch 安装失败；建议 `winget install Python.Python.3.12` 改用官方 Python |
| p2t 命令找不到 | 脚本已自动把 pip 的 Scripts 目录加入用户 PATH，新开终端即可；仍不行则手动把 `python -c "import site;print(site.getuserbase())"` 输出的 `Scripts` 目录加入 PATH |
| soffice 命令找不到（LibreOffice 已装） | 脚本已自动把 `C:\Program Files\LibreOffice\program` 加入用户 PATH；或直接用全路径 `soffice.com` |
| p2t 模型下载失败 | 设 `HF_ENDPOINT=https://hf-mirror.com`；或从旧机拷贝 `p2t-models` 目录 |
| mmdc 报无 Chrome | 设 `$env:PUPPETEER_EXECUTABLE_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"` |
| WSL 商店渠道失败 | 用 `curl.exe -L -o ubuntu2204.appx https://aka.ms/wslubuntu2204` + `Add-AppxPackage`（见 REQUIREMENTS.md §4） |
| 3GPP 文档缺失 | 跑 `setup\download-specs.ps1`；再用 `scripts\extract-docx.ps1` 生成文本索引 |

## 路径可移植配置（clone 后必做，把占位符转成本机真实路径）

仓库内所有文件使用占位符表示路径（如 、），clone 后必须转换：

1. 填写本机路径映射（复制 skills 到本机后）：
   - 编辑 ，每行 ：
     
2. 执行转换（把占位符转为本机真实路径）：
   
3. 校验残留： 应为空
4. 自动类占位符（用户目录等）无需填写，脚本按新机器自动推导


## 路径可移植配置（clone 后必做，把占位符转成本机真实路径）

仓库内所有文件使用占位符表示路径（如 <用户目录>、<项目目录>），clone 后必须转换：

1. 填写本机路径映射（skills 复制到本机后）：
   - 编辑 <用户目录>\.config\opencode\skills\update_skill\path_map.txt，每行 `占位符=本机真实路径`：
     ```
     <项目目录>=D:\work\project
     <源码目录>=D:\code
     <WSL安装目录>=D:\WSL
     <离线安装包目录>=D:\software\wls
     <工具目录>=D:\
     <LibreOffice目录>=C:\Program Files\LibreOffice
     <Chrome目录>=C:\Program Files\Google\Chrome\Application
     <Node目录>=C:\Program Files\nodejs
     <3GPP文档库目录>=D:\docs\NR
     ```
2. 执行转换（占位符转为本机真实路径）：
   ```
   python scripts\path_convert.py to_local --home="<本机用户目录正斜杠>" <本机opencode配置目录>
   python scripts\path_convert.py to_local --home="<本机用户目录正斜杠>" <用户临时目录>\opencode
   ```
3. 校验残留：grep 搜索 "<用户目录>" 等占位符应为空
4. 自动类占位符（用户目录等）无需填写，脚本按新机器自动推导


## 语言规则验证（解决"中文提问英文回答"）

install 脚本完成并重启 opencode 后，必须验证全局规则注入：

1. 检查注册：`C:\Users\<新用户>\.config\opencode\opencode.jsonc` 含 `"instructions": ["instructions.md"]`
2. 检查文件：同目录下 `instructions.md` 存在且非空
3. **完全重启 opencode**（不是新会话，是退出进程重启——instructions 只在启动时加载）
4. 新会话用中文提问验证：回答应为中文；若仍英文 → instructions 未加载：
   - 确认 opencode.jsonc 内容无误（JSON 合法、instructions 键存在）
   - 确认无项目级 opencode.json 覆盖了全局配置
   - 排查后仍无效：把 instructions 内容合并进项目 AGENTS.md 作为临时兜底
