# update_skill 参考：🛠 工具依赖清单（移植到新机器时先逐项检查）

## 🛠 工具依赖清单（移植到新机器时先逐项检查）

| 工具 | 用途 | 本机位置/版本 | 检查命令 | 缺失时安装 |
|---|---|---|---|---|
| git | 版本同步 | WSL Ubuntu 内 git 2.34 | `wsl -d Ubuntu -e bash -c "git --version"` | `apt install git` |
| SSH 密钥 | GitHub 推送认证（SSH 远程） | `~/.ssh/id_*`（github.com 已授权） | `wsl -d Ubuntu -e bash -c "ssh -T git@github.com"` | 生成密钥并添加到 GitHub 账号 |
| 同步源（本机全局配置） | 进化后的最新内容 | `<opencode配置目录>\`（skills/instructions.md/evolution.md/opencode.jsonc/plugins） | `Test-Path <opencode配置目录>\instructions.md` | — |
| 同步源（本机脚本） | 配套 PS/Python 脚本 | `<用户临时目录>\opencode\*.ps1`、项目 temp 的 inject_skills.py/fetch_skills.py | `Test-Path` | — |
| 目标 Git 仓库 | 云端同步落点 | `/home/github/learn.opencode/copy`（WSL 内；Windows 访问 `\\wsl.localhost\Ubuntu\home\github\learn.opencode\copy`） | `wsl -d Ubuntu -e bash -c "cd /home/github/learn.opencode/copy && git remote -v"` | 从 GitHub clone：`git clone git@github.com:johnson-learn/learn.opencode.git copy` |

---

