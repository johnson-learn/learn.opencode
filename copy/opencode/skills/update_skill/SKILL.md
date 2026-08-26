---
name: update_skill
description: 技能双向同步更新技能（全局 skill，仅显式触发，不靠关键词自动调用）。Use ONLY when 用户消息显式包含 "update_skill" 字样（"update_skill：" 带冒号+片段序列、或裸 "update_skill" 无冒号、或 "update_skill&" 与其它技能名并列）。加载后执行任务：消息按中文冒号（英文冒号同）分割为片段序列，从左到右依次执行——片段四分类：① update_skill 标记片段=执行双向同步（功能1：本机全局 opencode 配置的新改动差异合入仓库并 commit/push；功能2：检查远端新提交并反向合入本机）；② 路径片段=记录目标目录；③ 约束片段（含"别/不要/禁止/只"等词，如"别反复修改"）=约束其后双向更新为零修改模式（噪音恢复不提交、无实质进化不 push）；④ 问题片段=按全局回答规则回答。多标记意义：首轮更新吸收远端→中间问题基于最新状态回答→末轮更新对齐收尾。裸 "update_skill"=仅双向更新。普通消息仅提及同步/git 但无 "update_skill" 字样时，不调用本技能。
---
# update_skill —— 技能同步更新技能

## 核心准则（一句话，执行时必须全部保证）

> **update_skill 执行时必须保证三点：① 当前电脑的新增修改同步到远端（GitHub）；② 远端内容保持可移植（占位符体系），能移植安装到全新电脑；③ 远端新提交能反向更新到另一台已移植旧版本的电脑上（pull + 版本对齐 + to_local）。**

本技能负责把本机 opencode 配置（全局 skill + 规则 + 脚本）同步到 GitHub 仓库，实现"本机进化 → 云端同步 → 其它机器移植"闭环。



## 处理流程（目标目录确定 → git 五步 + 同步三环节，按序执行）

### 调用解析（第一步必做，片段四分类 + 顺序执行）

- **消息分割**：按中文冒号 `：`（英文 `:` 同）把冒号后内容分割为片段序列，**从左到右依次执行每个片段**（后片段依赖前片段已产生的最新状态，如问题片段基于前面双向更新后的最新数据作答）。
- **片段四分类**（按特征识别）：
  1. **update_skill 标记片段**：片段以 `update_skill` 开头 → 执行双向更新流程（见下）；片段内同时含路径特征 → **先记录该目录为同步目录，再双向更新**——同步目录是三方链路的中转：**本机 ↔ 同步目录（git 仓库工作树）↔ GitHub**（本机 cp 到同步目录 → to_portable → commit/push 上 GitHub；GitHub pull 到同步目录 → 反向合入本机）
  2. **路径片段**：片段为目录路径（含 `\`、`/`、盘符 `C:`、UNC `\\`、WSL `/home/` 等特征）→ 仅记录为同步目标目录，不执行更新
  3. **约束片段**：片段含"别""不要""禁止""注意""只/仅"等约束词（如"别反复修改"）→ 约束其后的所有双向更新为**零修改模式**：正向噪音 diff（教学行误伤等）恢复仓库不提交、无实质进化不 push、只做对齐校验；约束持续到本条消息结束
  4. **问题片段**：其它内容 → 作为问题/任务执行（按全局通用回答规则回答）
- **规则总结（示例）**：冒号 `：` 为片段间隔符，片段**从左到右依次执行**，多标记交替进行
  - `update_skill`（无冒号）= 仅双向更新（用已记录的同步目录）
  - `update_skill：<目录路径>` = 记录该目录为同步目录 + 双向更新（链路：本机 ↔ 同步目录 ↔ GitHub）
  - `update_skill：问题` = 双向更新 → 回答问题
  - `问题：update_skill` = 回答问题 → 双向更新
  - `update_skill：问题：update_skill` = 双向更新 → 回答问题 → 双向更新
  - `update_skill：问题：update_skill：问题：update_skill` = 双向更新 → 问题 → 双向更新 → 问题 → 双向更新（按冒号间隔交替，依次类推）
  - `update_skill：别反复修改：问题：update_skill` = 双向更新（正常模式，此时约束尚未出现）→ 记录零修改约束 → 回答问题 → 双向更新（零修改模式）——**约束片段只约束其后的片段，不回溯之前的**
- **多标记的意义**：首轮 update_skill 吸收远端新提交并把本机对齐 → 中间问题基于最新状态作答 → 末轮 update_skill 做最终对齐校验（吸收中间新发现的远端变化）
- **首次调用必须指出同步目标目录**：任一片段含路径特征即记录；从未指出过目录 → 提示用户

### 目标目录确定（记忆机制）
- **首次调用必须指出同步目标目录**，格式：`update_skill：<目标目录路径>`（Windows UNC 如 `\\wsl.localhost\Ubuntu\home\github\learn.opencode`，或 WSL 路径如 `/home/github/learn.opencode`）
- 首次调用未指出目录 → **提示用户**："请指出同步目标目录，格式：update_skill：<目录路径>"，等待用户给出后再继续
- 目录记忆：本机状态文件 `<opencode配置目录>\skills\update_skill\sync_target.txt` 保存最近指定的目录；每次用户显式给出新目录 → 更新该文件
- 后续调用未指出目录 → 读取状态文件用最近目录；**幂等**：目录已存在（或默认目录已存在）且状态文件有效时，不再重复询问，直接使用
- Windows UNC 与 WSL 路径互转：UNC `\\wsl.localhost\Ubuntu\...` ↔ WSL `/...`；git 操作一律在 WSL 路径下执行

### 第 0 步：先 git pull（强制，防止覆盖他人更新）
```
wsl -d Ubuntu -e bash -c "cd /home/github/learn.opencode/copy && git pull --rebase origin main"
```
- pull 成功 → 继续；**pull 冲突** → 停止同步并报告冲突文件，由用户裁决，不得强行 push；冲突文件逐个 diff 对比，按"信息完整性优先"合并两边有效内容
- 工作树非干净（有未提交改动）→ 先 stash（`git stash`），pull 后 `git stash pop`；冲突同上处理
- 网络失败（无法连 GitHub）→ 报告"无法 pull"，询问是否仅本地 commit（不 push）

### 第 0.5 步：版本对齐检查（旧机器升级场景防倒退，必做）
> 场景：本机是早期移植的旧版本（如旧路径体系、缺新 skill），远端已有其它机器的新提交。**必须防止旧本机内容覆盖仓库新内容（版本倒退）**。
1. pull 后对比本机与仓库的差异方向：
   - 本机全局配置目录：`<opencode配置目录>\`（含 skills、instructions.md、evolution.md、plugins）
   - 仓库目录：`copy\opencode\`（占位符版本）
2. 判定规则：
   - **仓库有、本机没有**的文件/skill → 这是远端新增 → **先反向合入本机**（复制仓库文件 → path_convert to_local → 覆盖到本机），本机完成升级
   - **本机有、仓库没有**的 → 本机新增 → 正常正向同步
   - **两边都有但内容不同** → 逐文件对比：以内容更完整/更新的一方为主体，**保留对方独有的有效条目**（信息完整性优先）；本机旧版本内容不得简单覆盖仓库新内容
3. 对齐完成后（本机已吸收远端新内容），再继续正向同步三环节
4. 旧体系兼容：若仓库是旧路径体系（含真实路径非占位符），先用 `path_convert.py to_portable` 就地升级仓库文件为占位符体系，再执行本流程
5. **对称回退防护（✓ 双机实测重大教训）**：同名文件本机源与仓库（git HEAD）不一致时，**先判断差异方向再决定谁覆盖谁**——`git log -1 --oneline -- <文件>` 查最后修改者：若最后修改者是其它机器的提交，且本机源与其内容不一致 → **本机源落后，必须先反向合入该文件到本机，再正向同步**；严禁本机旧文件覆盖仓库中新修复（双机各自用旧工作树 cp 会把对方修复对称回退）。判定口诀：仓库 HEAD 含本机没有的修复内容 = 本机落后 = 先吸收后同步

### 同步三环节（差异合入模式，禁止简单删除替换）

> ⚠ 该 git 仓库可能被其它电脑同时更新修改，**必须对比差异、优化整合合入，不得 rm -rf 删除替换**；仓库中本机没有的文件一律保留（可能是别的电脑的新增），同名文件以内容差异为准逐文件裁决。

1. **合入全局配置** → 仓库 `opencode/` 子目录（覆盖式合入：cp -r 覆盖同名、保留仓库多出文件）：
   ```
   wsl -d Ubuntu -e bash -c "cp -r /mnt/c/Users/<用户名>/.config/opencode/skills/* /home/github/learn.opencode/copy/opencode/skills/ && cp /mnt/c/Users/<用户名>/.config/opencode/{instructions.md,evolution.md,opencode.jsonc} /home/github/learn.opencode/copy/opencode/ && mkdir -p /home/github/learn.opencode/copy/opencode/plugins && cp -r /mnt/c/Users/<用户名>/.config/opencode/plugins/* /home/github/learn.opencode/copy/opencode/plugins/"
   ```
2. **合入本机脚本** → 仓库 `scripts/`（同样覆盖式合入）：
   ```
   cp <用户临时目录>\opencode\*.ps1、*.py 与 <项目目录>\temp\inject_skills.py、fetch_skills.py → copy/scripts/
   ```
3. **差异对比与裁决**：
   - `git status --short` 列出全部差异：`A`（本机新增→直接接受）、`M`（同文件两边可能都改）、`D`（仓库有本机无→**不删除，恢复保留**，除非确认已废弃）
   - 对 `M` 文件逐个 `git diff <文件> | head` 查看变化，确认本机内容合理即接受；**同文件两边都改过**（git pull 后与 HEAD 差异 + 远端新提交）时，逐文件对比内容并按"信息完整性优先"合并（保留两边独有的有效内容，冲突点报告用户裁决）
   - **敏感信息扫描**：检查变更中无密钥/token/凭证；`.gitignore` 覆盖凭证类
   - 一致性校验：skill 数量 ≥ 源数量（合入后只增不减）、关键文件非空
   - 无任何差异 → 报告"无新改动"并结束

### git 三步骤
1. `git add -A`
2. `git commit -m "sync: YYYY-MM-DD <变更摘要>"`——摘要自动生成规则：优先列出新增/改名 skill 名（如 "+update_skill"），其次概括修改类别（如 "3gpp_skill FTP 结构、instructions 规则"）；正文可加 `-m` 详细条目（新增了哪些文件、改了什么章节）
3. `git push origin main`；**push 失败**（网络/权限）→ 保留 commit 并明确报告"本地已提交，待推送"，不丢弃成果

### 第 4 步：反向合入本机（git → 本机，双向同步必须执行）
> push 成功不代表结束——**必须检查远端是否有其它机器在 push 之前刚推送的新提交**，有则把远端新变化反向移植回本机（实现双向同步）。
1. push 前记录旧 HEAD：`OLD=$(git rev-parse HEAD)`
2. push 成功后检查远端：`git fetch origin && git log --oneline $OLD..origin/main | head`——有输出说明其它机器有新提交
3. 有远端新提交 → `git pull --rebase origin main` → 提取变更文件：`git diff --name-only $OLD..HEAD` → 将这些文件**从仓库反向复制回本机**（差异合入、不删除本机文件）：
   - `opencode/skills/...` → `<opencode配置目录>\skills\...`
   - `opencode/instructions.md、evolution.md、opencode.jsonc` → `<opencode配置目录>\`
   - `opencode/plugins/...` → `<opencode配置目录>\plugins\`
   - `scripts/...` → `<用户临时目录>\opencode\`
4. 反向合入的冲突处理：同名文件本机与远端都改过时，按"信息完整性优先"合并（本机当前内容为主、远端新增有效内容并入），无法自动合并的报告用户裁决
5. 无远端新提交 → 报告"远端无新变化"，流程结束

### 收尾报告
输出：pull 结果、本机→git 变更清单与 commit hash、push 结果、git→本机 反向合入清单（若有）；若仓库内 README/INSTALL 提及的技能清单与现状不符，提醒用户是否一并更新



## 通用输出规则（全部任务遵守）

- **语言跟随提问**：用户以何种语言提问，思考、回答、输出就以何种语言；命令、路径、字段名等必要原文保持原样
- **含"输出"二字 → HTML 交付**：提问中出现"输出"二字时，最终答案必须以 HTML 文件输出（规范排版），内容详细、不限字数篇幅；HTML 保存到提问时所在工作目录并浏览器打开（用户另行指定目录时按用户指定）



## 环境注意

- 目标仓库在 WSL 内（`/home/github/learn.opencode/copy`），本机 Windows 源经 `/mnt/c/` 访问；WSL 未运行时先 `wsl -d Ubuntu` 拉起
- **目录记忆状态文件**：`<opencode配置目录>\skills\update_skill\sync_target.txt`（记录最近目标目录；首次调用必须由用户指出目录，后续默认用最近目录）
- 推送认证走 SSH（git@github.com）；若换 HTTPS 需配 token
- 仓库内 `setup/`（install-wsl.ps1 等）、`README.md`、`INSTALL.md`、`REQUIREMENTS.md` 为移植配套文档，同步时保留不动
- **风险规避**：同步前检查不包含任何密钥/token；`~/.lobehub-market/credentials.json` 等凭证一律不进入仓库
- 本机配置类内容（绝对路径/版本）集中在各 skill 的工具依赖清单，新机器按清单重配即可
- 新增 skill 后记得手动跑一次本技能，把新 skill 同步到 GitHub



## 智能进化

每次执行本技能后，按 instructions.md「智能进化协议」检查：同步流程中的新踩坑（SSH 失败、pull 冲突、路径变化、新文件类型）立即固化到本技能；经验表述保持可移植（本机路径用占位符）。



## 详细知识（按需读取 references/，不随入口加载）

- 详见 `references/tools.md`
- 详见 `references/portable-paths.md`
