---
name: session_compress_skill
description: 会话压缩技能（会话上下文精简/压缩执行技能）（全局 skill，仅显式触发，不靠关键词自动调用）。Use ONLY when 用户消息显式包含 "session_compress_skill：" 或 "session_compress_skill:"，或以 "session_compress_skill&"、"session_compress_skill " 与其他技能名并列后跟冒号——冒号后为用户任务。加载后执行任务：当前会话历史过长、需要压缩时，按 `references/config-template.md` 模板结构（A 历史会话主题 / B 目录 / C 要点 / D 修改输出文件 / E 使用工具），把当前会话的业务上下文压缩生成 `session.md`（放当前工作目录，文件名固定 session.md，供新会话继承继续同一主题）。内容只含业务类，不含框架 skill 的讨论/修改/工具；只写已核实+已落地+用户确认的结论；不写"下一步"。普通消息仅提及压缩/精简/太长等关键词但无 "session_compress_skill：" 前缀时，不调用本技能。
collaborates_with:
  - task_tracking_skill
---

# 会话压缩/上下文精简技能（session_compress_skill）

## 🛠 工具依赖清单

| 工具 | 用途 | 说明 |
|---|---|---|
| write（opencode 内置工具） | 生成/覆盖工作目录下 `session.md` | 零外部依赖，opencode 内置 |
| read（opencode 内置工具） | 读取 `references/config-template.md` 模板、现有 session.md | 零外部依赖，opencode 内置 |

无额外外部依赖；会话压缩只用 opencode 内置工具 + 模板文件。模板位置：`references/config-template.md`。校验脚本引用：`skill_validate.py` / `test_regedit.py` / `test_instructions.py` / `test_inject_skills.py`（改动后跑）。

## 职责

本 skill 是「长会话上下文压缩」的执行器。当会话历史过长、输入 token 过大时，用户显式触发本 skill，把当前会话的业务上下文按模板压缩成 `session.md`，供**开新会话时手动继承**（新窗口由用户按需把内容复制进去，不做自动化加载）。

## 配套模板（references/config-template.md，权威）

- 压缩生成的 **结构、字段、使用规则** 全部以 `references/config-template.md` 为唯一权威，本文只给流程与铁律。
- 触发本 skill 时，**先 read `references/config-template.md`** 再按其结构填写生成 `session.md`。

## 处理流程

1. **确认触发**：用户消息含 `session_compress_skill：` → 进入压缩流程。
2. **读模板**：read `references/config-template.md`，明确 A/B/C/D/E 结构、字段、规则。
3. **收集当前会话业务上下文**：基于本会话已知的「已核实 + 已落地 + 用户确认」的业务结论、目录、输出文件、工具，按模板分类整理。
4. **生成 session.md**：write 到**当前工作目录**，文件名固定 `session.md`（覆盖旧版）；严格套用模板结构。
5. **自检**：校验内容只含业务类、字段符合模板、命名正确、无框架 skill 内容，向用户汇报生成位置 + 提示开新会话继承方式。

## 铁律

- **只写业务类**：A 主题 / B 目录 / C 要点 / D 修改输出文件 / E 工具——全部为本任务业务类内容。
- **上下-SESSION 不含框架 skill**：框架 skill 的**讨论、修改、工具、进化**一律不写入 session.md（框架变更走单独进化流程，不混入业务交接）。
- **C 要点**：只收"已核实(原文/实测) + 已落地 + 用户确认"的结论，禁止未验证推测；只含本任务业务结论，不含框架 skill 讨论。
- **D 文件**：只列本会话产生/修改的**业务输出文件**，不列框架 skill 的改动文件。
- **E 工具**：只列实际使用过的**业务工具名**；opencode 内置工具不写、框架运营类工具（health_check、skill_validate 等）不写；不写操作步骤/方法。
- **不写"下一步"**：交给新会话由用户按新需求提出，避免绑架新方向。
- **文件名固定**：一律 `session.md`，放当前工作目录。

## 继承使用（供用户，本 skill 不自动执行）

- 会话太长 → 用户显式触发本 skill 生成 `session.md` → **开新会话** → 用户手动把 `session.md` 内容复制进新窗口，即可从业务结论继续，无需重读旧会话历史。

## 与其它 skill 分工

- 与 `task_tracking_skill` 配合：压缩前先保证任务窗已完成/归档；压缩是长任务节奏（铁律 10：超长会话开新会话续做）的落地执行器。

## 自检（交付前）

- `session.md` 是否套用了 `references/config-template.md` 的结构（A/B/C/D/E）？
- 是否只含业务类？有无误入框架 skill 的讨论/修改/工具/路径？
- C 是否仅"已核实 + 已落地 + 用户确认"？是否误写了未验证推测或"下一步"？
- E 是否只列非内置业务工具？是否误写 opencode 内置/框架运营工具？
- 文件名是否固定 `session.md`、且放当前工作目录？
- 若发现漏项，立即补齐后交付。

## 详细知识

- 模板结构、字段、使用规则：`references/config-template.md`（按需读取）。
- 无 modules（非聚合型 skill）。

## 本 skill 经验索引（分域健康监控台账）

> 本 skill 相关经验在 `<opencode配置目录>\skills\default\evolution_skill\evolution_log.txt` 中带「归属：session_compress_skill」字段的条目；active 摘要：会话压缩（A/B/C/D/E 结构、业务类、模板 config-template.md、文件名固定 session.md、E 只列非内置工具）；低活性/待验证条目由经验健康引擎按归属分组提示。
