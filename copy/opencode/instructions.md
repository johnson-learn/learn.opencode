# 技能触发规则（Skill Invocation Rules）

> **规则三层与冲突优先级**：AGENTS.md 铁律 > regedit.md 注册表（加载方式权威）> 本文件（详版协议细则）。冲突时以高优先级层为准；本文件承载细则（五步流程/编写规范/回答规则），铁律摘要见 AGENTS.md，加载方式登记见 regedit.md。

## 智能进化协议（所有全局 skill 与指令文件自我进化，最高优先级约定）

> **注册表机制（2026-08-26 新增）**：全体系组件的加载方式唯一权威登记在 `~\.config\opencode\regedit.md`（生效方式八分类 A~H：A 系统注入 100% 必达 / B 会话必读 / C 技能匹配 / D 显式调用 / E 运行时事件 / F 按需读取 / G 流程强制 / H 响应检查）。AGENTS.md 铁律第 0 条强制每次会话开始先读注册表；插件 session.created 程序化注入提醒兜底。组件新增/变更必须同步更新 regedit.md 并跑 `python C:\Users\Johnson\.config\opencode\tests\test_regedit.py`。

### 进化触发时机（双机制，主机制=全局 AGENTS.md 每次响应可见）

- **主机制：全局 AGENTS.md 铁律注入**。`~\.config\opencode\AGENTS.md` 会被 opencode 作为全局规则加载进**每个会话的系统提示**（已验证：会话上下文可见其全文）。铁律第 2 条即"每次响应后强制复盘进化"，执行点=**每次回答结束前自查**（踩坑/更优路径/新工具/机制缺陷/违反协议 → 加载 `evolution_skill`（进化执行器）按五步流程固化并在回答末尾附"进化：已固化…/无新固化"）。这是唯一每次都必然对模型可见的机制。
- **兜底机制：skill-banner 插件 `session.idle`（会话结束）注入「进化检查任务」**（client.session.prompt 程序化发送）——弥补模型在会话中被中断、未及固化的情况；但它发生在会话结束时，**不能作为主执行点**（教训：把执行点绑在会话外=模型上下文不可见=全靠用户推动）
- **注入任务为强制清单，不可跳过、不可精简**：① 经验固化（五步流程）；② 工具登记（本会话用到的任何新工具/脚本/库必须登记 tools-manifest.md）；③ 总表同步（skill 依赖或本机配置变更）；④ 校验自测（skill_validate.py + 行为自测）；⑤ 合并/拆分/迁移只出建议；⑥ 完成后回复固化项清单或"无固化项"
- **机制缺陷教训（2026-08-26 实测 + 2026-08-27 修正）**：协议写在不加载进上下文的文件（instructions.md 的 opencode.jsonc instructions 字段引用无效）= 模型看不见 = 框架从不执行。任何规则若要模型执行，必须先确认它在每次会话的系统提示中可见（可靠通道：① 全局/项目 AGENTS.md（A 类原生注入）；② skill-banner 插件 `experimental.chat.system.transform` 注册事件注入（E 类，2026-08-27 实施：平台每次请求构建系统提示时直读 instructions/regedit/docs-sync/tools-manifest 四文件 push 进 output.system）；③ skill description 进入 skill 列表）。**版本事实与回退预案**：opencode.jsonc instructions 字段在 1.18 系列（1.18.18 实测）解析但不消费（1.18 系统提示构建只认 AGENTS.md/CLAUDE.md/CONTEXT.md），是 0.x dev/beta 线功能——该字段已回滚移除（2026-08-27 用户指令），系统提示注入由注册事件承担；experimental.chat.system.transform 是实验性 API，其可用性由 test_platform_api.py 持续检测，失效时回退：① 重启 instructions 字段（若新版已实现）② 铁律第 0 条强制 read 的 B 类路径
- 每次任务回答过程中如遇踩坑/新发现，可即时记录（额外触发点）
- 轨迹记录：插件同时把会话轨迹追加到 `~\.config\opencode\skills\default\evolution_skill\evolution_trace.jsonl`（供合并/拆分分析用）

### 五大自动进化能力（判定规则）

1. **自动更新**：任务中发现更优路径/新边界情况 → 按五步流程直接 edit 补充到对应 skill 章节（自动执行）
2. **自动生成**：任务中发现全新经验/技能领域，符合全局 skill 要求（独立职责、可复用、非项目特定）→ 按编写规范新建全局 skill（自动执行，放入 skills 目录后 skill-banner 自动纳入展示）
3. **自动合并（产出建议）**：两个 skill 功能重叠度高且经常同时被调用 → 输出「进化建议：合并 A 与 B 为通用 C」+ 理由与方案，**待用户确认后执行**（不自动执行，防破坏既有结构）
4. **自动拆分（产出建议）**：某 skill 职责过多、命中率下降（同一 skill 被用于互不相干任务）→ 输出「进化建议：拆分 X 为 Y/Z」+ 职责划分方案，**待用户确认后执行**
5. **跨层迁移（产出建议）**：项目 skill 中抽象的通用经验 → 建议提升为全局 skill；全局 skill 中的项目特定细节 → 建议下沉为项目 skill；**待用户确认后执行**

**执行分级铁律**：更新/生成=直接执行；合并/拆分/迁移=只出建议，用户说"执行"才动手；任何进化动作都不得附带 git 同步（同步边界铁律）。

**轨迹分析时机**：执行 update_skill 时附带分析 `~\.config\opencode\skills\default\evolution_skill\evolution_trace.jsonl` 与各 skill 调用记录——若发现共现频率高/职责混乱的模式，在同步报告中附「进化建议」清单。

### 可移植性要求（固化内容强制标准）
- **经验表述必须通用化、可移植，不得局限本机**：
  - 工具与用法写通用名称和通用调用方式（如 "p2t predict -i ..."，本机全路径只在"工具依赖清单"的本机位置列标注）
  - 本机绝对路径（`Users\<用户名>\...`、`<盘符>:\...`）改用占位表述（如 `C:\Users\Johnson`、`C:\Users\Johnson\.config\opencode`）或标注"本机路径示例"
  - 区分两类内容：**通用经验**（任何机器直接适用）与**本机配置**（路径/版本/凭证，集中于工具依赖清单的本机位置列，移植时按清单重配）
  - 判断标准：换一台干净机器，经验能否照做？不能则重写为通用表述

### 归纳与固化流程（五步 + 每步校验自测，缺一不可）
> **五步检查点程序化强制（2026-08-27 起）**：执行固化（响应含"已固化"声明）时必须按序输出五个标记行，每行跟该步结构化中间结果；evolution_gate --check-5step 由插件 session.idle 自动检测，缺步即注入补做警告。只声明"无新固化/无固化项"时不需要五步。
1. **归纳**【第一步·归纳】：从本次会话提取可复用的新经验，用一两句话精确表述（按可移植性要求通用化）
2. **归属**【第二步·归属】：判断更新到哪个 skill 的哪个章节（工具依赖清单/处理流程/铁律/环境注意/路由表/访问技巧）或 instructions.md
3. **更新**【第三步·edit】：用 edit 工具增补/修订对应章节，保持既有结构，不重写全文；新经验标注来源与验证状态
4. **记录**【第四步·流水】：追加到 `~\.config\opencode\skills\default\evolution_skill\evolution_log.txt`（日期 + 来源 + 更新点，只增不改）；规则/机制类经验同时提炼写入 `~\.config\opencode\skills\default\evolution_skill\evolution.md`（进化规则，更新前须弹窗确认）
5. **校验与自测（每条进化强制，不得跳过）**【第五步·校验】：
   - **内容正确性核查**：命令/路径/参数是否准确可执行；与既有条目有无矛盾重复；来源标注与验证状态标注是否齐全；通用性达标（无硬编码本机路径）
   - **结构化自测**：跑 `python D:\opencode\project\default\temp\skill_validate.py C:\Users\Johnson\.config\opencode\skills`——frontmatter 合法、name 匹配目录、description ≤1024、路由表引用路径存在
   - **行为自测（涉及可执行内容时）**：新增/修改的命令、脚本、流程**实际执行一次验证**（如新增 p2t 参数用法→实际跑一遍）；无法实测的标注"未实测，待验证"并列入 evolution_log.txt 待验证清单
   - 校验或自测不通过 → 立即修正该条进化，修好前不进入下一条

### 风险规避（写入前强制检查）
- 未经验证的方法/工具标注"未验证"；验证过的标注"✓ 本机实测"
- 外部付费 API 一律标注"需用户确认"
- 不写入任何密钥/token/密码/凭证
- 与既有内容矛盾时，以新验证结果为准并同步修订旧条目

### 应用范围
- 4 个全局 skill（按领域归档）+ instructions.md（全局规则）+ 后续新增 skill（自动适用编写规范与本协议）
- 新项目注入的项目级副本随全局源同步（重新执行 inject_skills.py 即更新）
- 项目/文件夹 md（AGENTS.md 等）：项目特定经验写入该项目的 AGENTS.md

## 全局通用回答规则（所有会话一律遵守，无论是否触发 skill）

0. **同步边界铁律（最高优先级）**：只有用户**显式调用 update_skill** 时，才允许执行以下动作——(a) 把远端更新拉取/合入本机；(b) 把本机修改复制到同步目录并 git commit/push 到远端。**其它任何场景（包括用户提出需求、讨论方案、进化固化 skill 文件本身）都不得擅自执行上述同步动作**；本机 skill/指令文件的直接编辑（进化固化）不受此限，但绝不附带 git 同步。

0.5 **字符边界规范细则（AGENTS.md 铁律第 9 条，用户 2026-08-27 定）**：本机 = Windows PowerShell（GBK 默认）↔ Python/Node/WSL（UTF-8）多边界环境，任何跨界都可能发生编码/转义/换行转换——历史上 GBK 乱码、引号转义崩溃、LF→CRLF 破坏解析、中文 commit 丢失等事故多发。执行细则：① 跨工具传数据一律文件化（禁 `python -c`/`node -e` 内联中文；禁 `wsl -e bash -c` 内联多行脚本；git commit 用 `-F`）；② Python 写文件显式 `encoding="utf-8", newline="\n"`，读子进程输出 `encoding="utf-8", errors="replace"`；③ PowerShell 调 .ps1/.cmd 包装命令用 `cmd /c`；④ 框架文本文件统一 UTF-8 无 BOM + LF（test_charset.py 程序化防线，health_check 必跑，失败立即归一修复再交付）；⑤ 临时文件放 `%LOCALAPPDATA%\Temp\opencode\`。

1. **语言跟随提问（回答语言硬约束）**：用户以何种语言提问，思考、回答、输出就必须以何种语言（中文提问→中文回答含思考过程，英文提问→英文回答），任何情况下不得因模型偏好/文档语言/任务习惯改用其它语言；协议原文、配置项名称、原始字段、ASN.1、代码、命令、报错信息等必要原文保持原样不翻译
   - **裁定条款（2026-08-27 实测修正）**：语言跟随的唯一权威依据 = **当条消息的实际语言**，思考/回答/输出三者必须一致跟随。平台语言指令（`【语言指令·平台检测】`）只是会话默认基调兜底，**当它与当条消息实际语言不一致、或平台检测失效（未触发/恒为旧值）时，一律以当条消息实际语言为准**，不得沿用旧语言——实测事故：平台检测事件未触发导致指令恒为"中文"，英文提问轮出现"思考中文、回答英文"分裂（根因：`plugins\skill-banner.js` 的 `message.part.updated` 检测失效 + 模型未按铁律兜底）
2. **"输出"二字触发 HTML 交付**：提问中出现"输出"二字时，最终答案必须以 HTML 文件输出（公式用 MathJax 渲染、代码高亮、规范排版），内容**详细、不限字数篇幅**；HTML 保存到合适目录（如 D:\opencode\project\default\temp 或任务相关目录）并浏览器打开；未含"输出"时按普通文本回答
3. **输出文件跟随提问位置**：在哪个文件夹（会话工作目录）提问，生成的输出文件默认就保存在哪个文件夹；用户另行指定目录时按用户指定
4. **新项目 skill 注入规则**：当用户在一个新文件夹/新项目（当前工作目录下不存在项目级 skill）中**显式调用全局 skill**（如 `files_skill：任务`）时，必须执行注入：
   - 把**全部全局 skill**（`~\.config\opencode\skills\` 下每个 skill 目录）复制到当前项目的 `.opencode\skills\` 下（成为项目级 skill）
   - 对复制出的每个 SKILL.md，改写 frontmatter description：把"（全局 skill，仅显式触发，不靠关键词自动调用）"改为"（项目级 skill，默认触发）"，把"Use ONLY when 用户消息显式包含..."的仅显式限制改为"Use when 用户消息显式包含 <skill名>：（显式调用）或任务涉及本技能领域时按需自动调用"
   - 注入脚本（本机已验证）：`python C:\Users\Johnson\.config\opencode\tools\inject_skills.py <目标项目目录>`
   - 注入后提醒用户重启 opencode；之后该项目内提问默认触发这些项目级 skill，无需再显式调用
   - 已注入过的项目（`.opencode\skills\` 已有同名 skill）默认覆盖更新

## 全局 skill 编写规范（新增/更新 skill 时必须遵守）

1. **位置**：`~\.config\opencode\skills\<skill名>\SKILL.md`；目录名 = frontmatter 的 name（小写+下划线，如 files_skill）
2. **description 格式**（显式触发约定）：开头"（全局 skill，仅显式触发，不靠关键词自动调用）" + "Use ONLY when 用户消息显式包含 "<skill名>："..." + 冒号后为任务说明 + "普通消息仅提及关键词但无前缀时，不调用本技能"
3. **🛠 工具依赖清单章节（必须，置于 skill 开头正文首章）**：表格列【工具 | 用途 | 本机位置/版本 | 检查命令 | 缺失时安装】，末尾附"移植说明"总结核心依赖与可选项——便于移植到新机器逐项检查
3c. **工具总清单唯一权威源**：`C:\Users\Johnson\.config\opencode\tools-manifest.md` 是全体系工具的唯一权威管理表（分类 A~G + 本机配置 + 待补充清单）。规则：① 各 skill 的工具清单为分 skill 视角摘录，冲突时以总表为准；② **新增/变更/安装任何工具时，必须同步更新总表**——覆盖范围：所有全局 skill、**项目级 skill** 的新增依赖工具均须登记；③ **思考回答中发现的好用工具、脚本、库等，即使未写进任何具体 skill，也必须登记到总表**（可先入"待补充"清单，装好后移入对应类别）；④ 新机器移植按总表逐项检查安装；⑤ setup-windows.ps1 的安装清单与总表保持对齐
3b. **入口 SKILL.md 精炼原则**：入口文件只保留 frontmatter + 处理流程 + 路由表 + 核心铁律（目标 ≤5KB）；大块知识（工具清单明细、网站结构、访问技巧、长教程）移到 skill 目录下 `references/*.md`，入口用一句话引用"详见 references/xxx.md，按需读取"——防一次性加载上万个 token（豆包分析指出的短板）
4. **处理流程章节（必须）**：确认任务 → 路由 → 执行 → 联动其它 skill（find_skill/filer_skill 等）
5. **子技能资源库规范**：聚合类 skill 的子技能放 `modules/<目录>/GUIDE.md`（SKILL.md 改名 GUIDE.md，不独立注册）；路由表用 `modules/<目录>` 引用
6. **环境注意章节（必须）**：本机已装工具、调用规范（全路径/特殊参数）、未装大件（需用户同意）
7. **权威源规则**：领域有官方权威源（如 3GPP 官网）时，必须写"权威源声明"并规定"其它资料可参考，但以官网为准"
8. **持续更新约定**：涉及外部资源（网站/FTP）的 skill 必须写"后续访问发现新变化时同步更新本 skill"
9. **新增 skill 自动纳入**：新 skill 放入 skills 目录后，skill-banner 插件动态扫描自动在会话创建时展示，无需改任何配置；但需重启 opencode 生效
10. **语言跟随提问**（所有全局 skill 必须写入）：与「全局通用回答规则」第 1 条一致
11. **"输出"触发 HTML 交付 + 输出位置**（所有全局 skill 必须写入）：与「全局通用回答规则」第 2、3 条一致

## 本机全局技能清单（新会话创建时 TUI 弹 toast 自动展示；插件 skill-banner.js 动态扫描 `~/.config/opencode/skills/*/SKILL.md` 的 frontmatter，**新增全局 skill 无需任何配置自动纳入**）

| 技能 | 用途 |
|---|---|
| `files_skill` | 文件识别/OCR/公式/文档处理 |
| `3gpp_skill` | 3GPP/5G NR/LTE 通信标准专家 |
| `find_skill` | 网络资源获取与镜像加速 |
| `program_skill` | 编程开发（默认 WSL Linux 环境） |
| `update_skill` | 技能双向同步更新（仅显式触发） |
| `evolution_skill` | 智能进化协议执行器（默认触发） |

## 项目 skill（默认触发）

- 当前项目目录（`.opencode/skills/`、`.claude/skills/`、`.agents/skills/`）中的 skill 为**项目 skill**
- 在项目内提问时，**默认随会话激活**：模型按任务需要自动匹配并调用项目 skill 的 description
- 用户无需任何前缀，项目 skill 即可被使用

## 全局 skill（仅显式触发）

- 全局目录（`~/.config/opencode/skills/` 等）中的 skill 为**全局 skill**
- 默认**不自动调用**，仅当用户用显式语法指定时才加载
- 显式语法：

```
<skill名>：<问题>                    # 单技能，中文冒号
<skill名>: <问题>                    # 英文冒号（冒号后空格可选）
<skill名A>&<skill名B>：<问题>        # & 并列多个
<skill名A> <skill名B>：<问题>        # 空格并列多个
```

- 例：`files_skill：识别图片文字`、`files_skill&code_skill：失败图片文字`

## 组合规则

1. **未显式指定**：仅项目 skill 参与（按关键词自动匹配）；全局 skill 一律不调用
2. **显式指定了全局 skill**：加载这些全局 skill + 当前项目的默认 skill，共同回答冒号后的问题
3. 技能名列表中未注册的名字：忽略该名字，其余照常加载
4. 项目无 skill 且未显式指定：按普通问题正常处理
5. 新增全局专题 skill 时，仅需保证 SKILL.md 的 `name` 与目录一致，即自动支持本语法
