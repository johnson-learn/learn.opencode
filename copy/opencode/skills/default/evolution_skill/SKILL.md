---
name: evolution_skill
description: 智能进化协议执行技能（全局 skill，默认触发）。Use when 需要执行进化固化——经验归纳与五步固化（踩坑/更优路径/新工具/机制缺陷/违反协议）、工具登记（tools-manifest.md）、注册表更新（regedit.md）、配套文档同步、进化建议产出（合并/拆分/迁移）、或响应插件注入的进化检查任务。AGENTS.md 铁律第 2 条每次响应复盘进化发现需固化时自动调用本技能。
collaborates_with:
  - update_skill
---

# 智能进化协议执行技能（evolution_skill）

## 🛠 工具依赖清单

| 工具 | 用途 | 检查命令 |
|---|---|---|
| skill_validate.py | skill 结构校验（五步流程第 5 步） | `python <opencode配置目录>\tests\skill_validate.py <opencode配置目录>\skills` |
| test_regedit.py | 注册表一致性校验 | `python <opencode配置目录>\tests\test_regedit.py` |

无额外外部依赖；进化固化本身只用 edit/read 工具与上述校验脚本。

## 职责

本 skill 是进化协议的**执行器**。铁律第 2 条（每次响应复盘进化）发现需固化时，按本 skill 流程执行；详版协议见 `<opencode配置目录>\instructions.md` 智能进化协议章节。

## 处理流程

> **进化门禁（evolution_gate.py，机制步骤确定性执行）**：插件在 session.created 调 `--snapshot`（记录规则文件快照）、session.idle 调 `--check`——脚本自动完成：检测本会话改动 / 流水兜底追加（模型未记录时）/ 按改动类型自动跑对应测试 / 输出待模型补充清单。**本技能只需完成智能部分**：经验归纳、归属判定、edit 固化到可执行载体。

1. **触发确认**：踩坑 / 更优路径 / 新工具 / 机制缺陷 / 违反协议 → 需固化
2. **五步固化（每步先输出结构化中间结果再动作；标记格式程序化强制）**：
   > **五步检查点强制输出格式（2026-08-27 起由插件+evolution_gate --check-5step 程序化检测，缺步自动告警补做）**：执行固化动作（声明"已固化"）时，响应中必须按序出现以下五个标记行，每行后跟该步的结构化中间结果；只做"无固化"声明（"进化：无新固化"）时不需要五步：
   > `【第一步·归纳】` → 输出 `{经验描述, 经验类型(规则|记录|知识), 触发场景}`，一句精确描述、通用化（无本机路径）；**先过固化判定四条件（2026-08-28 报告评审后新增；V2 报告后程序化强制）**：① ≥2 个不同场景出现（或 1 个场景但代价高/用户点名）② 可移植 ③ 不与已有规则重复 ④ 能写出触发条件与适用边界——任一不满足 → 仅追加 evolution_log.txt（事实类），不进规则文件；**必须显式输出结论行 `【判定四条件】场景数：X / 可移植：是 / 无重复：是 / 边界：明确`（gate --check-5step 程序化检测，缺声明告警）**
   > `【第二步·归属】` → 输出 `{主载体, 配套同步文件, 校验测试}`（**归属二分判定**）：规则/流程/机制类 → 主载体=对应 SKILL.md / instructions.md / regedit.md / AGENTS.md / evolution.md 规则文件（**只写 evolution_log.txt = 归属失败**）；记录/事实类 → 仅 evolution_log.txt；配套按 docs-sync.md 映射表列出；校验测试=test_regedit / test_instructions / test_evolution_consistency 等
   > `【第三步·edit】` → 按归属清单逐个 edit 目标文件（每个 edit 后立即自检：改了什么/是否误删无关内容）
   > `【第四步·流水】` → 追加 evolution_log.txt（**只增不改**：追加尾部，禁止替换既有条目——教训 2026-08-26：替换导致记录覆盖丢失）
   > `【第五步·校验】` → 跑归属清单中的校验测试 + 行为实测（涉及命令实跑）；不通过立即修正；**含过期经验排查（2026-08-28 报告评审后新增）**：新经验与旧经验矛盾 → 以新验证结果为准修订旧条目 + 追加 deprecation 记录（只标记不删历史）；本会话推翻某旧经验 → 同样处理
   - **evolution.md 规则文件更新附加铁律**：更新前必须 ① 结合 evolution_log.txt 核对 ② **弹窗让用户确认**（question 工具）③ 确认后才 edit ④ 更新后跑 test_evolution_consistency.py
3. **修改复盘核查（edit 完成后、自测前强制，用户 2026-08-26 定）**：改了什么/为什么改/有无误删误改无关内容？规则类内容是否已进全部应改载体（不只 evolution.md）？是否符合占位符/可移植性/归属二分铁律？配套文档是否同步？——核查通过才跑测试
4. **注册表更新（强制）**：组件新增/变更 → 更新 regedit.md（位置/生效方式/说明）→ 跑 `python <opencode配置目录>\tests\test_regedit.py`
5. **工具登记（强制）**：新工具/脚本/库 → tools-manifest.md
6. **配套文档同步（强制，不许等用户提醒）**：结构/机制/工具变更 → README/INSTALL/REQUIREMENTS/tests\README.md 等同步；**流程类变更 → 必须同步 SKILL.md 与 regedit.md**；配套更新清单以 docs-sync.md 映射表为权威
7. **回应末尾附进化行**：`进化：已固化 …` 或 `进化：无新固化`

## 进化质量与可持续性（2026-08-28 报告评审后新增，防"写而不用/错误进化/规则膨胀"）

- **经验状态标记**：evolution_log 新条目默认 active；失效/被推翻时只追加 deprecation/invalidated 记录并修订对应规则文件，不删不改历史；**被标记 deprecated 的经验必须在对应规则文件条目上显式加 `[DEPRECATED]` 前缀或删除线**（V2 报告采纳：状态只写流水不可见，规则文件显式标记确保注入系统提示时 LLM 能看到）
- **重要经验二次验证**：写入 evolution.md 或铁律级规则的经验标注"待二次验证"；下次相关任务主动套用验证，结果追加 evolution_log；通过则标"✓ 二次验证通过"；门禁（gate --check）程序化统计"待二次验证/二次验证通过"计数，未闭环时主动提示
- **注入量管控**：instructions/regedit/tools-manifest/docs-sync 四注入文件合计上限 50KB（V2 报告修正：核心两文件即 40KB，30KB 不现实），超限触发精简（压缩示例/重复摘要，大表留速览头行）；health_check 检测告警
- **使用率自审**：进化检查时附带自查——本会话套用了哪些已固化经验；约 10 次会话未被提及的经验提示"低活性，建议下沉 references/ 或标 deprecated"
- **冲突显式裁决**：新经验与旧规则矛盾时禁止静默二选一，必须在响应中标注"与旧规则 X 冲突，按新验证结果修订"并同步改旧条目

## 新增文件适配决策（A+C 方案，2026-08-28 用户选定实施）

> 门禁（evolution_gate --check）会输出 `【新增文件】N 个（待适配决策）` 清单及分类提示，随进化检查任务注入。本流程保障"新增 skill/md/脚本"被发现、决策、纳入、验收的闭环。

1. **四问分析**（对清单中每个新增文件）：
   ① 它是什么（skill 入口 / skill 附属 references / 测试 / 工具脚本 / 插件 / 规则文档 / 一次性任务产物）？
   ② 是否应纳入框架（可复用通用 vs 一次性产物——产物建议存档 `tools\archive\` 或忽略）？
   ③ 归到哪类载体（regedit 技能层/工具层/测试层/插件层/数据层 + tools-manifest 类别 + instructions 技能清单）？
   ④ 触发方式（全局仅显式 / 项目级默认触发）+ 配套测试（skill_validate / test_regedit / test_plugin / 新测试文件）？
2. **弹窗决策**（question 工具，逐项让用户选择，不得 AI 擅自决定）：
   - `适配` → 执行第 3 步完整纳入
   - `忽略` → 加入 evolution_gate.py `IGNORE_DIRS` 或仓库 `.gitignore` 白名单（防每会话重复提醒）
   - `存档` → 移入 `tools\archive\`（一次性脚本归宿）
3. **纳入动作**（按四问结论）：
   - 新 skill → regedit 技能层登记（C+D 生效方式）+ instructions 技能清单表 + frontmatter description 规范检查（全局仅显式触发格式）+ 新项目注入判定（inject_skills.py）
   - 新工具/脚本 → tools-manifest 分类表 + regedit 工具层 + 按需挂入 evolution_gate 自动测试链
   - 新测试 → tests\README 登记 + regedit 测试层 + 挂入门禁（改动检测自动跑）
   - 新规则 md → regedit 登记生效方式（E 注入/F 按需）+ 30KB 注入量管控判定
4. **纳入验收（程序化证明，全绿才算成功）**：`python <opencode配置目录>\tests\test_regedit.py`（登记与实际文件系统一致）+ `skill_validate.py`（frontmatter/体积/路由）+ `test_instructions.py`（技能清单双向一致）+ `test_tools_manifest.py`（计数吻合）+ `health_check.py`；失败项即"适配未完成"证据，修复后重跑直至全绿
5. 完成后在回应中报告：适配清单（每文件：四问结论 → 用户选择 → 纳入动作 → 验收结果）

## 五大进化能力

| 能力 | 执行方式 |
|---|---|
| 自动更新（更优路径/新边界） | 直接执行 |
| 自动生成（全新领域经验 → 新 skill） | 直接执行，按编写规范新建 |
| 自动合并（两 skill 高重叠） | 只出「进化建议」待用户确认 |
| 自动拆分（职责过多） | 只出「进化建议」待用户确认 |
| 跨层迁移（项目↔全局） | 只出「进化建议」待用户确认 |

## 校验自测（每条固化强制，不得跳过）

1. **内容核查**：命令可执行 / 无本机硬编码路径 / 标注验证状态 / 通用性达标
2. **结构化自测**：`python <opencode配置目录>\tests\skill_validate.py <opencode配置目录>\skills`
3. **行为实测**：涉及可执行内容（命令/脚本/流程）必须实跑一次；无法实测标注"未实测，待验证"
4. 组件新增/变更后跑对应测试（test_regedit / test_plugin / test_path_convert / test_update_skill）

## 铁律

- **不得附 git 同步**（同步边界铁律：同步只能由用户显式 update_skill 触发）
- 合并/拆分/迁移只出建议，用户说"执行"才动手
- 进化检查任务（插件注入）不可跳过、不可精简
- 注册表自身也受本协议进化：分类可新增、条目按五步固化 + test_regedit.py 校验
