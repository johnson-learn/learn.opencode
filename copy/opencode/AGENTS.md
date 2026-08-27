# 全局铁律（每个会话自动加载，最高优先级）

> **规则三层与冲突优先级**：AGENTS.md 铁律（本文件）> regedit.md 注册表（加载方式权威）> instructions.md 详版协议（细则）。冲突时以高优先级层为准；内容重叠处只在本层保留摘要，细则指向下层。

## 0. 注册表必读（每会话开始第一动作）
每次会话开始，必须先读取 `<opencode配置目录>\regedit.md`（全体系注册表）。
按其中「生效方式分类」（A 系统注入 / B 会话必读 / C 技能匹配 / D 显式调用 / E 运行时事件 / F 按需读取 / G 流程强制 / H 响应检查）确定每个组件何时加载、何时执行。组件新增/变更必须同步更新注册表并跑 `python <opencode配置目录>\tests\test_regedit.py`。

## 1. 同步边界铁律
只有用户显式调用 `update_skill`（或消息含 `update_skill` 字样）时才允许 git pull/合入/commit/push。
其它任何场景（需求、讨论、进化固化、编辑 skill 文件）都不得擅自执行 git 同步动作。
本机 skill/指令文件直接编辑（进化固化）不受此限，但绝不附带 git 同步。

## 2. 每次响应后强制复盘进化（执行点：每次回答结束前，不是会话结束时）
每次回答用户之前，必须自查本响应过程：
- 是否踩了坑 / 发现更优路径 / 用到新工具或脚本 / 暴露机制缺陷 / 违反本协议？
- 有 → 加载 `evolution_skill`（进化执行器），按其流程五步固化（归纳→归属→edit 更新→追加进化流水→校验自测）+ 注册表更新（regedit.md + test_regedit.py）+ 配套文档同步，并在回答末尾附一行：`进化：已固化 …`
- 无 → 回答末尾附一行：`进化：无新固化`
固化位置：`<opencode配置目录>\instructions.md` / `<opencode配置目录>\skills\default\evolution_skill\evolution.md`（进化规则，更新需弹窗确认）/ `<opencode配置目录>\skills\default\evolution_skill\evolution_log.txt`（历史流水，只增不改）/ 对应 skill 的 SKILL.md 或 references\ / `tools-manifest.md` / `regedit.md`。
**归属二分铁律**：规则/流程/机制类经验必须写入可执行载体（SKILL.md/instructions.md/regedit.md/AGENTS.md/evolution.md 规则文件），只写 evolution_log.txt = 归属失败；记录/事实类才仅写 evolution_log.txt。
任何结构/机制/工具变更后，README/INSTALL/REQUIREMENTS/tests\README.md 等配套文档必须同步更新——不许等用户提醒；**流程类变更必须同步 SKILL.md 与 regedit.md**；**配套更新清单以 `<opencode配置目录>\docs-sync.md` 映射表为权威**（按变更类型逐项更新对应文件并跑校验测试）。
校验自测（每条固化强制）：内容核查（命令可执行/无本机硬编码路径/标注验证状态）+ `python <opencode配置目录>\tests\skill_validate.py` + 行为实测（涉及命令必须实跑）。
详版五步流程与五大进化能力见 `<opencode配置目录>\instructions.md` 与 `evolution_skill`。

## 3. 语言跟随提问（回答语言硬约束，任何会话、任何模型都必须遵守）
用户以何种语言提问，思考、回答、输出就必须用该语言：**中文提问必须用中文回答，英文提问必须用英文回答**；任何情况下不得因模型偏好/文档语言/任务习惯改用其它语言；协议原文、配置名、代码、命令、报错等必要原文保持原样不翻译。

## 4. "输出"二字触发 HTML 交付
提问含"输出"→ 最终答案以 HTML 文件交付（MathJax/代码高亮/详版不限字数），保存在提问所在文件夹并浏览器打开；否则普通文本。

## 5. 输出文件跟随提问位置
在哪个文件夹（会话工作目录）提问，输出文件默认保存在哪里；用户另行指定时按用户指定。

## 6. 新项目 skill 注入
新项目首次显式调用全局 skill → 执行全部全局 skill 注入（脚本 `<opencode配置目录>\tools\inject_skills.py <项目目录>`，description 改默认触发）并提醒用户重启 opencode。

## 7. 工具总表登记
思考/回答中发现的好用工具、脚本、库，即使未写进具体 skill 也必须登记 `<opencode配置目录>\tools-manifest.md`（可先入"待补充"）。

## 8. 修改复盘核查 + 测试先行
每个文件修改完成后、跑自测之前，必须自我复盘核查该次修改（用户 2026-08-26 定，防低级错误）：
- 改了什么、为什么改、有无误删/误改无关内容？
- 该次修改的**规则/机制类内容是否已进全部应改载体**（SKILL.md/instructions.md/regedit.md 等，不只见于 evolution_log.txt 流水）？
- 是否符合占位符/可移植性/归属二分铁律？配套文档是否同步？
核查发现问题 → 立即修正；核查通过才跑测试。
每次对 skill/插件/工具/流程的修改，必须跑 `<opencode配置目录>\tests\` 下对应测试（skill_validate.py / test_plugin.js / test_path_convert.py / test_update_skill.py）；新增机制必须同步新增测试用例。

## 9. 字符边界规范（跨系统/跨工具执行脚本的强制约定，用户 2026-08-27 定）
本机环境 = Windows PowerShell（GBK 默认）↔ Python/Node/WSL（UTF-8），任何跨界都可能发生编码/转义/换行转换。执行以下强制规范：
- **跨工具传数据一律文件化**：① 禁 `python -c`/`node -e` 内联含中文的代码 → 写临时 `.py`/`.js`/`.mjs` 文件再执行；② 禁 `wsl -e bash -c` 内联多行/含引号脚本 → 写 `.sh` 文件 + `wsl -d Ubuntu -e bash /mnt/c/.../x.sh` 执行；③ git commit 消息一律 `-F` 文件传递；④ 临时文件统一放 `<临时目录>`（本机 = `%LOCALAPPDATA%\Temp\opencode`）。
- **写文件规范**：Python 写文本文件显式 `encoding="utf-8"` + `newline="\n"`（防 Windows 默认换行转换把 LF 变 CRLF 破坏跨平台解析）；读子进程输出显式 `encoding="utf-8", errors="replace"`；框架文本文件统一 UTF-8 无 BOM + LF 行尾。
- **命令行包装**：PowerShell 直调 opencode/npm 等 .ps1/.cmd 包装命令被执行策略拦截 → 用 `cmd /c` 包装。
- **防线**：`<opencode配置目录>\tests\test_charset.py` 程序化扫描框架文件 CRLF/BOM/编码一致性，health_check 必跑；扫描失败立即修复再交付。
