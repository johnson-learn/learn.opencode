# 全体系注册表（Registry）—— 唯一权威加载方式登记表

> **规则三层与冲突优先级**：AGENTS.md 铁律 > 本注册表（加载方式权威）> instructions.md 详版协议。冲突时以高优先级层为准；本表只登记「加载方式与生效时机」，规则细则见 instructions.md，铁律摘要见 AGENTS.md。
> 本表登记整个 opencode 体系的**全部组件**及其**生效/加载方式**。任何组件（技能/插件/工具/测试/数据/同步/规则）加入或变更时，必须同步更新本表，并跑 `python <opencode配置目录>\tests\test_regedit.py` 校验一致性。
> 读取约定：本表由 AGENTS.md 铁律第 0 条强制——**每次会话开始必须读取**；插件 session.created 程序化提醒兜底。

## 生效方式分类（保证等级从高到低）

| 代号 | 名称 | 机制 | 保证等级 |
|---|---|---|---|
| **A 系统注入** | opencode 启动即注入系统提示（无需模型任何动作） | 100%（每会话必达） |
| **B 会话必读** | AGENTS.md 铁律第 0 条强制 read + 插件 session.created 提醒（双通道） | 指令级（极高） |
| **C 技能匹配** | skill 的 name+description 每会话进技能列表（A 级可见），任务匹配时 skill 工具加载正文 | 匹配时加载 |
| **D 显式调用** | 用户消息带 skill 前缀/关键字才触发 | 用户触发 |
| **E 运行时事件** | 插件 hook 程序化触发，opencode 保证事件发生 | 事件级（opencode 保证） |
| **F 按需读取** | 响应过程中按铁律主动 read 的数据/手册文件 | 模型主动 |
| **G 流程强制** | update_skill / 进化固化 / 注入等流程步骤内强制执行 | 流程执行时 |
| **H 响应检查** | AGENTS.md 铁律在每次响应结束前强制执行的检查动作 | 指令级（极高） |

## 铁律层

| 注册项 | 位置 | 生效 | 说明 |
|---|---|---|---|
| AGENTS.md（8 条铁律） | `<opencode配置目录>\AGENTS.md` | A | 每会话系统提示必达，最高优先级；0=读注册表、1=每次响应复盘进化、2=同步边界、3=语言、4=输出HTML、5=输出位置、6=注入、7=工具登记、8=测试先行 |
| regedit.md（本注册表） | `<opencode配置目录>\regedit.md` | B | 铁律第 0 条强制每会话开始读取 |
| instructions.md（详版协议） | `<opencode配置目录>\instructions.md` | F | 五步进化流程/五大进化能力/skill 编写规范/通用回答规则详版 |
| evolution.md（进化规则文件） | `<opencode配置目录>\skills\default\evolution_skill\evolution.md` | H | **最新进化规则权威文件**（规则类经验可执行载体）；更新前必须结合 evolution_log.txt 核对 + **弹窗让用户确认**；更新后跑 test_evolution_consistency.py |
| evolution_log.txt（进化历史流水） | `<opencode配置目录>\skills\default\evolution_skill\evolution_log.txt` | H | 历史流水，**只增不改**（追加尾部）；test_evolution_consistency.py 的程序化校验数据源（近 5 条「」声明须落入规则文件） |

## 技能层（全局 6 个）

| 注册项 | 位置 | 生效 | 说明 |
|---|---|---|---|
| 3gpp_skill | `skills\3gpp_skill\SKILL.md` | C+D | 全局仅显式"3gpp_skill："；项目级副本默认触发 |
| files_skill | `skills\files_skill\SKILL.md` | C+D | 全局仅显式"files_skill："；项目级副本默认触发 |
| find_skill | `skills\find_skill\SKILL.md` | C+D | 全局仅显式"find_skill："；项目级副本默认触发 |
| program_skill | `skills\program_skill\SKILL.md` | C+D | 全局仅显式"program_skill："；项目级副本默认触发 |
| update_skill | `skills\update_skill\SKILL.md` | D | 仅显式"update_skill"；含双向同步全流程与同步边界铁律 |
| evolution_skill | `skills\default\evolution_skill\SKILL.md` | C | 进化执行器，默认触发（见进化层） |

## 项目技能层

| 注册项 | 位置 | 生效 | 说明 |
|---|---|---|---|
| 项目级副本（4 个，无 update_skill） | `<项目目录>\.opencode\skills\` | C | inject_skills.py 生成（description 改默认触发）；全局源进化后需重新注入 |

## 插件层

| 注册项 | 位置 | 生效 | 说明 |
|---|---|---|---|
| skill-banner.js | `plugins\skill-banner.js` | E | session.created：toast 技能清单 + 注入"读 regedit.md"提醒（noReply）；session.idle：注入进化检查 6 项强制清单兜底；写 evolution_trace.jsonl / plugin-evolution.log |

## 工具层（修炼工具）

| 注册项 | 位置 | 生效 | 说明 |
|---|---|---|---|
| inject_skills.py | `tools\inject_skills.py` | H | 新项目首次显式调用全局 skill 时执行（铁律第 6 条） |
| path_convert.py | `tools\path_convert.py` | G | update_skill 流程强制：to_portable/to_local 双向转换 |
| slim_skills.py | `tools\slim_skills.py` | F | SKILL.md 瘦身（超 8KB 时） |
| fetch_skills.py | `tools\fetch_skills.py` | F | 从技能目录网站获取 skill |
| cross_move.py | `tools\cross_move.py` | F | 跨 skill 归位 |
| generalize.py | `tools\generalize.py` | F | 经验通用化改写 |
| evolution_gate.py | `tools\evolution_gate.py` | E | 进化门禁脚本：session.created 时插件调 --drain（**异步后台**自愈补跑残留快照，max_n=3 限流防阻塞会话启动）+ --snapshot；session.idle 时 --check——机制步骤（流水兜底追加/自动测试/一致性校验）确定性执行，不依赖模型自觉 |
| archive\（18 个） | `tools\archive\` | F | 历史一次性脚本存档，不执行 |

## 测试层

| 注册项 | 位置 | 生效 | 说明 |
|---|---|---|---|
| skill_validate.py | `tests\skill_validate.py` | G | 每次 skill 改动后强制（铁律第 8 条）；体积门限可配置（--set-limit/--ignore/--ignore-all） |
| test_skill_validate_config.py | `tests\test_skill_validate_config.py` | G | skill_validate 配置机制改动后强制（7/7） |
| test_plugin.js | `tests\test_plugin.js` | G | 插件改动后强制（20/20） |
| test_path_convert.py | `tests\test_path_convert.py` | G | path_convert 改动后强制（9/9） |
| test_update_skill.py | `tests\test_update_skill.py` | G | 同步机制改动后强制（14/14，隔离临时仓库） |
| test_regedit.py | `tests\test_regedit.py` | G | 注册表改动后强制（本表与实际文件系统一致性） |
| test_tools_manifest.py | `tests\test_tools_manifest.py` | G | 工具总表改动后强制（分类计数吻合/待补充无重复/包可导入/表结构，21/21） |
| test_instructions.py | `tests\test_instructions.py` | G | instructions.md 改动后强制（章节/铁律互查/引用存在/技能清单与目录一致/编写规范，31/31） |
| test_evolution_gate.py | `tests\test_evolution_gate.py` | G | evolution_gate 改动后强制（快照/改动检测/流水兜底/自动测试触发，7/7） |
| README.md（测试清单） | `tests\README.md` | F | 查测试入口与运行命令 |

## 数据层

| 注册项 | 位置 | 生效 | 说明 |
|---|---|---|---|
| tools-manifest.md（工具总表） | `<opencode配置目录>\` | H | 工具登记铁律（第 7 条）；唯一权威工具表 |
| path_map.txt | `skills\update_skill\` | G | update_skill 流程；STATE_FILES 保护对象 |
| sync_target.txt | `skills\update_skill\` | G | 同步目标记忆；STATE_FILES 保护对象 |
| evolution_trace.jsonl | `<opencode配置目录>\skills\default\evolution_skill\` | E | 插件写（供合并/拆分分析） |
| plugin-evolution.log | `<opencode配置目录>\plugins\` | E | 插件日志（验证兜底机制实跑） |
| skill_validate_config.json | `tests\` | G | skill_validate 体积门限用户选择持久化（--set-limit/--ignore/--ignore-all 写入，后续一致性生效，随同步跨机器） |

## 同步层

| 注册项 | 位置 | 生效 | 说明 |
|---|---|---|---|
| update_skill 双向同步流程 | `skills\update_skill\SKILL.md` | D+G | 用户显式触发；五步框架强制（吸收远端含对端修改评审→修改→自测缺用例先补写→**弹窗确认**（question 工具）推送/填新内容→按选择执行）；推送前必须弹窗确认 |
| GitHub 仓库 | `github.com/johnson-learn/learn.opencode.git` | G | 仅 update_skill 允许触碰（铁律第 2 条） |
| WSL 工作副本 | `\\wsl.localhost\Ubuntu\home\github\learn.opencode\` | G | 同上 |
| 占位符体系 | path_map.txt + path_convert.py | G | 三级占位符（自动/工具/数据），双向转换 |
| 同步过滤规则 | update_skill SKILL.md「同步过滤规则」章节 + 仓库 .gitignore | G | 判断标准：其它机器使用框架/skill/功能时需要的才同步；临时文件（编译产物/测试样本/日志/状态文件/大资产）由 .gitignore 自动过滤 |
| 可移植性校验 | update_skill SKILL.md「第五步·推送前强制」+ test_update_skill.py 用例 8 | G | 提交到远端前强制：待提交内容不得含本机特征（home 真实路径/用户名路径/本机特有绝对路径）；用例 8 已进入提交前自测用例库 |
| 项目资产盘点 | update_skill SKILL.md「第 0.9 步」+ project_list.txt | G | 同步前遍历项目（当前目录 + project_list.txt 清单 + 显式指定），提取通用资产（新 skill/通用脚本）到全局并随同步上 GitHub；拿不准的列建议清单 |

## 进化层（第八层：保证智能自我进化）

| 注册项 | 位置 | 生效 | 说明 |
|---|---|---|---|
| evolution_skill（进化执行器） | `skills\default\evolution_skill\SKILL.md` | C | 铁律第 2 条复盘进化发现需固化时自动调用；五步固化 / 注册表更新 / 工具登记 / 配套文档 / 校验自测全流程封装 |
| 进化协议详版 | `instructions.md` 智能进化协议章节 | F | 五步流程 / 五能力 / 校验标准 / 风险规避详版 |
| 进化规则 | `evolution.md`（在 skills\default\evolution_skill\ 下） | H | 规则类经验可执行载体（更新前核对 evolution_log.txt + 弹窗确认，见铁律层登记） |
| 会话轨迹 | `evolution_trace.jsonl`（在 skills\default\evolution_skill\ 下） | E | 插件写，供合并/拆分分析 |
| 进化检查注入 | skill-banner.js session.idle | E | 会话结束兜底注入 6 项强制清单（幂等去重） |
| 注册表自我进化 | `regedit.md` 本身 | B+G | 本表条目/生效分类变更按五步固化 + test_regedit.py 校验；**生效方式分类可新增**（保证等级机制自身可进化） |

### 进化层闭环（保证智能自我进化）

```
铁律第2条（A类·每响应必查）→ 发现需固化 → evolution_skill（C类·自动调用）
  → 五步固化 → evolution.md / instructions.md / skill / tools-manifest.md / regedit.md
  → 校验自测（skill_validate + test_regedit + 行为实测）
  → 回应末尾附"进化：…"行（可审计）
兜底：插件 session.idle 注入进化检查（E类）→ 幂等去重防堆积
注册表自身进化：组件/分类变更 → 更新本表 → test_regedit.py 校验闭环
```
