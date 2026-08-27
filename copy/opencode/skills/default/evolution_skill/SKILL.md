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
   > `【第一步·归纳】` → 输出 `{经验描述, 经验类型(规则|记录|知识), 触发场景}`，一句精确描述、通用化（无本机路径）
   > `【第二步·归属】` → 输出 `{主载体, 配套同步文件, 校验测试}`（**归属二分判定**）：规则/流程/机制类 → 主载体=对应 SKILL.md / instructions.md / regedit.md / AGENTS.md / evolution.md 规则文件（**只写 evolution_log.txt = 归属失败**）；记录/事实类 → 仅 evolution_log.txt；配套按 docs-sync.md 映射表列出；校验测试=test_regedit / test_instructions / test_evolution_consistency 等
   > `【第三步·edit】` → 按归属清单逐个 edit 目标文件（每个 edit 后立即自检：改了什么/是否误删无关内容）
   > `【第四步·流水】` → 追加 evolution_log.txt（**只增不改**：追加尾部，禁止替换既有条目——教训 2026-08-26：替换导致记录覆盖丢失）
   > `【第五步·校验】` → 跑归属清单中的校验测试 + 行为实测（涉及命令实跑）；不通过立即修正
   - **evolution.md 规则文件更新附加铁律**：更新前必须 ① 结合 evolution_log.txt 核对 ② **弹窗让用户确认**（question 工具）③ 确认后才 edit ④ 更新后跑 test_evolution_consistency.py
3. **修改复盘核查（edit 完成后、自测前强制，用户 2026-08-26 定）**：改了什么/为什么改/有无误删误改无关内容？规则类内容是否已进全部应改载体（不只 evolution.md）？是否符合占位符/可移植性/归属二分铁律？配套文档是否同步？——核查通过才跑测试
4. **注册表更新（强制）**：组件新增/变更 → 更新 regedit.md（位置/生效方式/说明）→ 跑 `python <opencode配置目录>\tests\test_regedit.py`
5. **工具登记（强制）**：新工具/脚本/库 → tools-manifest.md
6. **配套文档同步（强制，不许等用户提醒）**：结构/机制/工具变更 → README/INSTALL/REQUIREMENTS/tests\README.md 等同步；**流程类变更 → 必须同步 SKILL.md 与 regedit.md**；配套更新清单以 docs-sync.md 映射表为权威
7. **回应末尾附进化行**：`进化：已固化 …` 或 `进化：无新固化`

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
