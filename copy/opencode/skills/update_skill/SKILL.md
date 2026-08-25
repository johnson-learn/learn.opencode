---
name: update_skill
description: 技能同步更新技能（全局 skill，仅显式触发，不靠关键词自动调用）。Use ONLY when 用户消息显式包含 "update_skill：" 或 "update_skill:"，或以 "update_skill&"、"update_skill " 与其他技能名并列后跟冒号——冒号后为用户任务或同步目标目录。加载后执行任务：自动检查本机全局 opencode 配置（skills/instructions.md/evolution.md/opencode.jsonc/plugins/scripts）的新改动，以差异合入模式同步到 Git 仓库目录（首次调用必须由用户指出目标目录，格式 update_skill：<目录>；后续默认用最近指定目录），并 git add/commit/push 到 GitHub，保证其它机器可下载移植。普通消息仅提及同步/git 但无 "update_skill：" 前缀时，不调用本技能。
---

# update_skill —— 技能同步更新技能

本技能负责把本机 opencode 配置（全局 skill + 规则 + 脚本）同步到 GitHub 仓库，实现"本机进化 → 云端同步 → 其它机器移植"闭环。每台机器上的 skill 进化成果经本技能汇聚到同一 GitHub 仓库，其它机器 clone 即可获得。

## 🛠 工具依赖清单（移植到新机器时先逐项检查）

| 工具 | 用途 | 本机位置/版本 | 检查命令 | 缺失时安装 |
|---|---|---|---|---|
| git | 版本同步 | WSL Ubuntu 内 git 2.x（Windows 侧也可，WSL 更稳） | `wsl -d Ubuntu -e bash -c "git --version"` | `apt install git` |
| SSH 密钥 | GitHub 推送认证（SSH 远程） | `~/.ssh/id_*`（github.com 已授权） | `wsl -d Ubuntu -e bash -c "ssh -T git@github.com"` | 生成密钥并添加到 GitHub 账号 |
| 同步源（本机全局配置） | 进化后的最新内容 | `<用户目录>\.config\opencode\`（skills/instructions.md/evolution.md/opencode.jsonc/package.json/plugins） | `Test-Path <用户目录>\.config\opencode\instructions.md` | — |
| 同步源（本机脚本） | 配套 PS/Python 脚本 | `<用户目录>\AppData\Local\Temp\opencode\*.ps1`、`inject_skills.py` 等 | `Test-Path` | — |
| 目标 Git 仓库 | 云端同步落点 | 用户指定的 git 仓库根目录（本机示例：`/home/github/learn.opencode`，Windows 访问 `\\wsl.localhost\Ubuntu\home\github\learn.opencode`；迁移包位于其 `copy/` 子目录） | `wsl -d Ubuntu -e bash -c "cd <仓库根目录> && git remote -v"` | 从 GitHub clone：`git clone git@github.com:<账号>/<仓库>.git` |

## 处理流程（目标目录确定 → git pull → 同步三环节 → git 三步骤，按序执行）

### 目标目录确定（记忆机制，第一步必做）
- **首次调用必须指出同步目标目录**，格式：`update_skill：<目标目录路径>`（目标目录 = git 仓库根目录，内含 `copy/` 迁移包；Windows UNC 如 `\\wsl.localhost\Ubuntu\home\github\learn.opencode`，或 WSL 路径如 `/home/github/learn.opencode`）
- 首次调用未指出目录 → **提示用户**："请指出同步目标目录，格式：update_skill：<目录路径>"，等待用户给出后再继续
- 目录记忆：本机状态文件 `<用户目录>\.config\opencode\skills\update_skill\sync_target.txt` 保存最近指定的目录；每次用户显式给出新目录 → 更新该文件
- 后续调用未指出目录 → 读取状态文件用最近目录；状态文件不存在或内容无效 → 按首次调用处理（提示用户）
- Windows UNC 与 WSL 路径互转：UNC `\\wsl.localhost\Ubuntu\...` ↔ WSL `/...`；git 操作一律在 WSL 路径下执行

### 第 0 步：先 git pull（强制，防止覆盖他人更新）
```
wsl -d Ubuntu -e bash -c "cd <仓库根目录> && git pull --rebase origin main"
```
- pull 成功 → 继续；**pull 冲突** → 停止同步并报告冲突文件，由用户裁决，不得强行 push；冲突文件逐个 diff 对比，按"信息完整性优先"合并两边有效内容
- 工作树非干净（有未提交改动）→ 先 stash（`git stash`），pull 后 `git stash pop`；冲突同上处理
- 网络失败（无法连 GitHub）→ 报告"无法 pull"，询问是否仅本地 commit（不 push）

### 同步三环节（差异合入模式，禁止简单删除替换）

> ⚠ 该 git 仓库可能被其它电脑同时更新修改，**必须对比差异、优化整合合入，不得 rm -rf 删除替换**；仓库中本机没有的文件一律保留（可能是别的电脑的新增），同名文件以内容差异为准逐文件裁决。

1. **合入全局配置** → 仓库 `copy/opencode/` 子目录（覆盖式合入：cp -r 覆盖同名、保留仓库多出文件）：
   ```
   wsl -d Ubuntu -e bash -c "cp -r /mnt/c/Users/<用户名>/.config/opencode/skills/* <仓库根目录>/copy/opencode/skills/ && cp /mnt/c/Users/<用户名>/.config/opencode/{instructions.md,evolution.md,opencode.jsonc,package.json} <仓库根目录>/copy/opencode/ && mkdir -p <仓库根目录>/copy/opencode/plugins && cp -r /mnt/c/Users/<用户名>/.config/opencode/plugins/* <仓库根目录>/copy/opencode/plugins/"
   ```
2. **合入本机脚本** → 仓库 `copy/scripts/`（同样覆盖式合入）：
   ```
   cp <用户目录>\AppData\Local\Temp\opencode\*.ps1、*.py 与 <项目目录>\temp\inject_skills.py、fetch_skills.py → <仓库根目录>/copy/scripts/
   ```
3. **差异对比与裁决**：
   - `git status --short` 列出全部差异：`A`（本机新增→直接接受）、`M`（同文件两边可能都改）、`D`（仓库有本机无→**不删除，恢复保留**，除非确认已废弃）
   - 对 `M` 文件逐个 `git diff <文件> | head` 查看变化，确认本机内容合理即接受；**同文件两边都改过**（git pull 后与 HEAD 差异 + 远端新提交）时，逐文件对比内容并按"信息完整性优先"合并（保留两边独有的有效内容，冲突点报告用户裁决）
   - **路径改写回退（防噪音关键，✓ 本机实测）**：本机文件经 setup-windows.ps1 第 7 步部署时已被路径改写（`C:\Users\job_p\...`→`C:\Users\<本机用户>\...`、`E:\openCodeDefault\temp`→`<本机 Temp>\opencode`），且被改写文件的 UTF-8 BOM 被剥除。同步前必须把这类纯路径/BOM 差异回退为仓库规范路径，**禁止把本机改写后的路径写回仓库**（否则仓库被本机路径污染、换机移植失效、每次同步产生大量噪音 diff）。判定方法：`git diff` 仅含旧机用户名/`E:`/本机用户名/BOM 变化 → 无实质进化，直接 `git checkout -- copy/` 恢复并报告"无新改动"（本机实测：37 个 M 文件全部为此类噪音）
   - **敏感信息扫描**：检查变更中无密钥/token/凭证；`.gitignore` 覆盖凭证类（`sync_target.txt` 等本机状态文件已排除）
   - 一致性校验：skill 数量 ≥ 源数量（合入后只增不减）、关键文件非空
   - 无任何差异 → 报告"无新改动"并结束

### git 三步骤
1. `git add -A`
2. `git commit -m "sync: YYYY-MM-DD <变更摘要>"`——摘要自动生成规则：优先列出新增/改名 skill 名（如 "+update_skill"），其次概括修改类别（如 "3gpp_skill FTP 结构、instructions 规则"）；正文可加 `-m` 详细条目（新增了哪些文件、改了什么章节）
3. `git push origin main`；**push 失败**（网络/权限）→ 保留 commit 并明确报告"本地已提交，待推送"，不丢弃成果

### 收尾报告
输出：pull 结果、变更文件数与关键变更清单、commit hash、push 结果；若仓库内 README/INSTALL 提及的技能清单与现状不符，提醒用户是否一并更新

## 通用输出规则（全部任务遵守）

- **语言跟随提问**：用户以何种语言提问，思考、回答、输出就以何种语言；命令、路径、字段名等必要原文保持原样
- **含"输出"二字 → HTML 交付**：提问中出现"输出"二字时，最终答案必须以 HTML 文件输出（规范排版），内容详细、不限字数篇幅；HTML 保存到提问时所在工作目录并浏览器打开（用户另行指定目录时按用户指定）

## 环境注意

- 目标仓库根目录在 WSL 内（本机示例 `/home/github/learn.opencode`，迁移包在其 `copy/` 子目录），本机 Windows 源经 `/mnt/c/` 访问；WSL 未运行时先 `wsl -d Ubuntu` 拉起
- **目录记忆状态文件**：`<用户目录>\.config\opencode\skills\update_skill\sync_target.txt`（记录最近目标目录；首次调用必须由用户指出目录，后续默认用最近目录）
- 推送认证走 SSH（git@github.com）；若换 HTTPS 需配 token
- 仓库内 `copy/setup/`（install-wsl.ps1 等）、`README.md`、`INSTALL.md`、`REQUIREMENTS.md` 为移植配套文档，同步时保留不动
- **风险规避**：同步前检查不包含任何密钥/token；`~/.lobehub-market/credentials.json` 等凭证一律不进入仓库
- 本机配置类内容（绝对路径/版本）集中在各 skill 的工具依赖清单，新机器按清单重配即可
- 新增 skill 后记得手动跑一次本技能，把新 skill 同步到 GitHub

## 智能进化

每次执行本技能后，按 instructions.md「智能进化协议」检查：同步流程中的新踩坑（SSH 失败、pull 冲突、路径变化、新文件类型）立即固化到本技能；经验表述保持可移植（本机路径用占位符）。
