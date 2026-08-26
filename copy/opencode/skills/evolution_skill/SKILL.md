---
name: evolution_skill
description: 智能进化协议执行技能（全局 skill，默认触发）。Use when 需要执行进化固化——经验归纳与五步固化（踩坑/更优路径/新工具/机制缺陷/违反协议）、工具登记（tools-manifest.md）、注册表更新（regedit.md）、配套文档同步、进化建议产出（合并/拆分/迁移）、或响应插件注入的进化检查任务。AGENTS.md 铁律第 2 条每次响应复盘进化发现需固化时自动调用本技能。
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

1. **触发确认**：踩坑 / 更优路径 / 新工具 / 机制缺陷 / 违反协议 → 需固化
2. **五步固化**：归纳 → 归属 → edit 更新 → 追加 evolution.md → 校验自测
3. **修改复盘核查（edit 完成后、自测前强制，用户 2026-08-26 定）**：改了什么/为什么改/有无误删误改无关内容？规则类内容是否已进全部应改载体（不只 evolution.md）？是否符合占位符/可移植性/归属二分铁律？配套文档是否同步？——核查通过才跑测试
4. **归属二分判定（关键，防"规则当记录"遗漏）**：
   - **规则/流程/机制类**（新增环节、流程步骤、执行约束、铁律、判定标准）→ **必须**写入可执行载体：对应 SKILL.md / instructions.md / regedit.md / AGENTS.md——只写 evolution.md = 归属失败
   - **记录/事实类**（本次执行了什么、分析结论、历史流水）→ evolution.md 即可
   - 固化后自检：本经验是规则还是记录？规则 → 已进可执行载体否？未进 → 立即补齐
4. **注册表更新（强制）**：组件新增/变更 → 更新 regedit.md（位置/生效方式/说明）→ 跑 `python <opencode配置目录>\tests\test_regedit.py`
5. **工具登记（强制）**：新工具/脚本/库 → tools-manifest.md
6. **配套文档同步（强制，不许等用户提醒）**：结构/机制/工具变更 → README/INSTALL/REQUIREMENTS/tests\README.md 等同步；**流程类变更 → 必须同步 SKILL.md 与 regedit.md**
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
