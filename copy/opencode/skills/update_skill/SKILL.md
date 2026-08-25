---
name: update_skill
description: 技能同步更新技能（全局 skill，仅显式触发，不靠关键词自动调用）。Use ONLY when 用户消息显式包含 "update_skill：" 或 "update_skill:"，或以 "update_skill&"、"update_skill " 与其他技能名并列后跟冒号——冒号后为用户任务。加载后执行任务：自动检查本机全局 opencode 配置（skills/instructions.md/evolution.md/opencode.jsonc/plugins/scripts）的新改动，同步到 Git 仓库目录 /home/github/learn.opencode/copy，并 git add/commit/push 到 GitHub（git@github.com:johnson-learn/learn.opencode.git），保证其它机器可下载移植。普通消息仅提及同步/git 但无 "update_skill：" 前缀时，不调用本技能。
---

# update_skill —— 技能同步更新技能

本技能负责把本机 opencode 配置（全局 skill + 规则 + 脚本）同步到 GitHub 仓库，实现"本机进化 → 云端同步 → 其它机器移植"闭环。

## 🛠 工具依赖清单（移植到新机器时先逐项检查）

| 工具 | 用途 | 本机位置/版本 | 检查命令 | 缺失时安装 |
|---|---|---|---|---|
| git | 版本同步 | WSL Ubuntu 内 git 2.34 | `wsl -d Ubuntu -e bash -c "git --version"` | `apt install git` |
| SSH 密钥 | GitHub 推送认证（SSH 远程） | `~/.ssh/id_*`（github.com 已授权） | `wsl -d Ubuntu -e bash -c "ssh -T git@github.com"` | 生成密钥并添加到 GitHub 账号 |
| 同步源（本机全局配置） | 进化后的最新内容 | `<用户目录>\.config\opencode\`（skills/instructions.md/evolution.md/opencode.jsonc/plugins） | `Test-Path <用户目录>\.config\opencode\instructions.md` | — |
| 同步源（本机脚本） | 配套 PS/Python 脚本 | `<用户目录>\AppData\Local\Temp\opencode\*.ps1`、项目 temp 的 inject_skills.py/fetch_skills.py | `Test-Path` | — |
| 目标 Git 仓库 | 云端同步落点 | `/home/github/learn.opencode/copy`（WSL 内；Windows 访问 `\\wsl.localhost\Ubuntu\home\github\learn.opencode\copy`） | `wsl -d Ubuntu -e bash -c "cd /home/github/learn.opencode/copy && git remote -v"` | 从 GitHub clone：`git clone git@github.com:johnson-learn/learn.opencode.git copy` |

## 处理流程（git 五步 + 同步三环节，按序执行）

### 第 0 步：先 git pull（强制，防止覆盖他人更新）
```
wsl -d Ubuntu -e bash -c "cd /home/github/learn.opencode/copy && git pull --rebase origin main"
```
- pull 成功 → 继续；**pull 冲突** → 停止同步并报告冲突文件，由用户裁决，不得强行 push
- 工作树非干净（有未提交改动）→ 先 stash（`git stash`），pull 后 `git stash pop`；冲突同上处理
- 网络失败（无法连 GitHub）→ 报告"无法 pull"，询问是否仅本地 commit（不 push）

### 同步三环节
1. **同步全局配置** → 仓库 `opencode/` 子目录（全量一致：先删后拷，防止本地已删除文件残留）：
   ```
   wsl -d Ubuntu -e bash -c "rm -rf /home/github/learn.opencode/copy/opencode/skills && cp -r /mnt/c/Users/<用户名>/.config/opencode/skills /home/github/learn.opencode/copy/opencode/ && cp /mnt/c/Users/<用户名>/.config/opencode/{instructions.md,evolution.md,opencode.jsonc} /home/github/learn.opencode/copy/opencode/ && rm -rf /home/github/learn.opencode/copy/opencode/plugins && cp -r /mnt/c/Users/<用户名>/.config/opencode/plugins /home/github/learn.opencode/copy/opencode/"
   ```
2. **同步本机脚本** → 仓库 `scripts/`（同样先删后拷）：
   ```
   复制 <用户目录>\AppData\Local\Temp\opencode\*.ps1、*.py 与 <项目目录>\temp\inject_skills.py、fetch_skills.py → copy/scripts/
   ```
3. **检查与校验**：
   - `git status --short` 列出全部变更
   - **敏感信息扫描**：检查变更中无密钥/token/凭证（如 `credentials.json`、`id_rsa`、`API_KEY=`）；`.gitignore` 应包含凭证类文件名
   - **一致性校验**：同步后 skill 数量与源一致（`ls skills | wc -l` 对比）、关键文件非空
   - 无任何变更 → 报告"无新改动，无需提交"并结束

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

- 目标仓库在 WSL 内（`/home/github/learn.opencode/copy`），本机 Windows 源经 `/mnt/c/` 访问；WSL 未运行时先 `wsl -d Ubuntu` 拉起
- 推送认证走 SSH（git@github.com）；若换 HTTPS 需配 token
- 仓库内 `setup/`（install-wsl.ps1 等）、`README.md`、`INSTALL.md`、`REQUIREMENTS.md` 为移植配套文档，同步时保留不动
- **风险规避**：同步前检查不包含任何密钥/token；`~/.lobehub-market/credentials.json` 等凭证一律不进入仓库
- 本机配置类内容（绝对路径/版本）集中在各 skill 的工具依赖清单，新机器按清单重配即可
- 新增 skill 后记得手动跑一次本技能，把新 skill 同步到 GitHub

## 智能进化

每次执行本技能后，按 instructions.md「智能进化协议」检查：同步流程中的新踩坑（SSH 失败、pull 冲突、路径变化、新文件类型）立即固化到本技能；经验表述保持可移植（本机路径用占位符）。
