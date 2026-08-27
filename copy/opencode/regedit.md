# 全体系注册表（Registry）—— 唯一权威加载方式登记表

> **规则三层与冲突优先级**：AGENTS.md 铁律 > 本注册表（加载方式权威）> instructions.md 详版协议。冲突时以高优先级层为准；本表只登记「加载方式与生效时机」，规则细则见 instructions.md，铁律摘要见 AGENTS.md。
> 本表登记整个 opencode 体系的**全部组件**及其**生效/加载方式**。任何组件（技能/插件/工具/测试/数据/同步/规则）加入或变更时，必须同步更新本表，并跑 `python <opencode配置目录>\tests\test_regedit.py` 校验一致性。
> 读取约定：本表由 AGENTS.md 铁律第 0 条强制——**每次会话开始必须读取**；插件 session.created 程序化提醒兜底。

## 生效方式分类（保证等级量化 + 本质二元标注：平台 vs LLM）

> **本质判据（用户 2026-08-26 定）**：执行归属按"谁决定"划分——平台执行代码/工具 → 属于平台；LLM 发起/决定 → 属于 LLM。本质只分两类，不模棱两可：
> **「100%：平台读 md 文件，并把内容注入 LLM」** 或 **「非100%（等级）：LLM 直接读 md 内容」**。
> 触发与读取分离的类别（C/D）：触发环节归谁不确定，但**触发后读文件 100% 是平台**（skill 工具=平台内置工具，平台读 SKILL.md 全文注入）。

| 代号 | 名称 | 机制 | 保证等级（量化） | 本质（谁执行，二元） |
|---|---|---|---|---|
| **A 系统注入** | opencode 启动即注入系统提示 | **100%** | **平台读 md 文件，并把内容注入 LLM**（LLM 无任何动作） |
| **B 会话必读** | 铁律第 0 条强制 read + 插件提醒（双通道督促） | 非100%（极高） | **LLM 直接读 md 内容**（read 工具由 LLM 发起；铁律与插件提醒仅是督促，不能替代读动作） |
| **C 技能匹配** | description 进技能列表；任务匹配时加载正文 | 非100%（触发环节：LLM 决定是否调 skill 工具） | 触发前=LLM 决定；**触发后=平台读 md 文件并把内容注入 LLM**（skill 工具由平台执行） |
| **D 显式调用** | 用户消息带前缀触发 | 非100%（触发环节：用户消息决定） | 触发前=用户决定；**触发后=平台读 md 文件并把内容注入 LLM** |
| **E 运行时事件** | 插件 hook 程序化触发 | **100%**（opencode 保证事件发生） | **平台执行代码**（插件/脚本确定性运行，非读 md） |
| **F 按需读取** | 响应中按铁律主动 read | 非100%（低，LLM 可能不读） | **LLM 直接读 md 内容** |
| **G 流程强制** | 流程步骤内强制执行 | 非100%（极高；流程内强制） | **LLM 直接读 md 流程规则并发起脚本调用**；脚本内部门禁=平台执行代码（确定性拒绝） |
| **H 响应检查** | 铁律在每次响应结束前强制自查 | 非100%（极高） | **LLM 直接读已注入的铁律内容并执行检查动作**（检查由 LLM 完成） |

## 铁律层

> **注入策略（2026-08-27 实测修正 + 回滚）**：opencode.jsonc 的 instructions 字段在本机 1.18 系列（1.18.18 实测）**解析但不消费**——1.18 系统提示构建只认 AGENTS.md/CLAUDE.md/CONTEXT.md（二进制证据），该字段是 0.x dev/beta 线功能（npm latest=1.18.23 为 1.18 线末版）；该字段已于 2026-08-27 按用户指令**回滚移除**（opencode.jsonc 现仅保留 $schema）。**平台注入通道 = 插件注册事件**：skill-banner.js 注册 `experimental.chat.system.transform`（平台每次请求构建系统提示时确定性触发），直读本层四文件 push 进 output.system——E 类 100% 平台执行、与 AGENTS.md 同级进入系统提示（mtime 缓存防重复读盘；环境变量 OPENCODE_DISABLE_MD_INJECT=1 禁用）。原 B/F/G/H 按需读取路径全部保留为双保险。**技术债务与回退预案**：该 hook 是实验性 API，opencode 升级可能变更/移除——由 test_platform_api.py（G 类，health_check 必跑）持续检测；若失效，回退方案按序：① 重启 opencode.jsonc instructions 字段（若新版已实现该字段，1.18 不实现的历史已核实）② 依赖铁律第 0 条强制 read + 插件提醒的 B 类路径。

| 注册项 | 位置 | 生效 | 说明 |
|---|---|---|---|
| AGENTS.md（9 条铁律） | `<opencode配置目录>\AGENTS.md` | A | 每会话系统提示必达，最高优先级；0=读注册表、1=每次响应复盘进化、2=同步边界、3=语言、4=输出HTML、5=输出位置、6=注入、7=工具登记、8=测试先行、9=字符边界规范 |
| regedit.md（本注册表） | `<opencode配置目录>\regedit.md` | E（原 B） | 插件 system.transform 直读注入系统提示；原铁律第 0 条强制 read + 插件提醒保留为双保险；全体系组件加载方式登记 |
| instructions.md（详版协议） | `<opencode配置目录>\instructions.md` | E（原 F） | 插件 system.transform 直读注入系统提示；五步进化流程/五大进化能力/skill 编写规范/通用回答规则详版 |
| docs-sync.md（配套同步映射表） | `<opencode配置目录>\docs-sync.md` | E（原 G） | 插件 system.transform 直读注入系统提示；变更类型→必须同步更新文件清单的权威映射 |
| tools-manifest.md（工具总表） | `<opencode配置目录>\tools-manifest.md` | E（原 H） | 插件 system.transform 直读注入系统提示；工具登记铁律（第 7 条）；唯一权威工具表 |
| evolution.md（进化规则文件） | `<opencode配置目录>\skills\default\evolution_skill\evolution.md` | H | 规则类经验可执行载体；更新前须结合 evolution_log.txt 核对 + 弹窗确认 |
| evolution_log.txt（进化历史流水） | `<opencode配置目录>\skills\default\evolution_skill\evolution_log.txt` | H | 历史流水，只增不改 |

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
| skill-banner.js | `plugins\skill-banner.js` | E | session.created：toast 技能清单 + 注入"读 regedit.md"提醒（noReply）+ **异步平台 API 保障检查（test_platform_api 失败即 toast 风险告警）**；session.idle：注入进化检查 6 项强制清单兜底 + **五步检查点程序化强制（拉会话消息→gate --check-5step→缺步警告并入任务）**；**experimental.chat.system.transform：平台直读 4 铁律/协议文件注入系统提示（mtime 缓存，OPENCODE_DISABLE_MD_INJECT=1 禁用）**；写 evolution_trace.jsonl / plugin-evolution.log |

## 工具层（修炼工具）

| 注册项 | 位置 | 生效 | 说明 |
|---|---|---|---|
| inject_skills.py | `tools\inject_skills.py` | H | 新项目首次显式调用全局 skill 时执行（铁律第 6 条） |
| path_convert.py | `tools\path_convert.py` | G | update_skill 流程强制：to_portable/to_local 双向转换 |
| slim_skills.py | `tools\slim_skills.py` | F | SKILL.md 瘦身（超 8KB 时） |
| fetch_skills.py | `tools\fetch_skills.py` | F | 从技能目录网站获取 skill |
| cross_move.py | `tools\cross_move.py` | F | 跨 skill 归位 |
| generalize.py | `tools\generalize.py` | F | 经验通用化改写 |
| evolution_gate.py | `tools\evolution_gate.py` | E | 进化门禁脚本：session.created 时插件调 --drain（**异步后台**自愈补跑残留快照，max_n=3 限流防阻塞会话启动）+ --snapshot；session.idle 时 --check——机制步骤（流水兜底追加/自动测试/一致性校验/**配套漏更检测（docs-sync 映射反向校验）**）确定性执行，不依赖模型自觉；**--check-5step：五步检查点检测（stdin 读会话消息，固化响应缺五步标记即检出，插件把缺步警告并入进化检查任务）** |
| health_check.py | `tools\health_check.py` | F | 一键健康检查：①核心配置齐全 ②skill frontmatter+体积门限 ③插件最近执行 ④测试可解析 ⑤门禁 idle/drain 记录 ⑥evolution_log 待处理项 ⑦平台 API 依赖保障（实验性 hook 可用性）⑧字符边界规范（CRLF/BOM/编码扫描）；--run 实跑全部测试 / --run-quick 实跑快子集（跑前提示预计耗时） |
| sync_push.py | `tools\sync_push.py` | G | 推送门禁脚本化：强制校验用户弹窗确认标记（无标记/非 push 选择直接拒绝 commit/push）；推送成功后自动清除标记；**WSL 仓库（wsl.localhost 路径）自动走 WSL 内 git 推送（SSH 密钥与 commit author 与历史一致）** |
| archive\（18 个） | `tools\archive\` | F | 历史一次性脚本存档，不执行 |

## 测试层

| 注册项 | 位置 | 生效 | 说明 |
|---|---|---|---|
| skill_validate.py | `tests\skill_validate.py` | G | 每次 skill 改动后强制（铁律第 8 条）；体积门限可配置（--set-limit/--ignore/--ignore-all） |
| test_skill_validate_config.py | `tests\test_skill_validate_config.py` | G | skill_validate 配置机制改动后强制（7/7） |
| test_plugin.js | `tests\test_plugin.js` | G | 插件改动后强制（42/42：事件分支 20 + 注册事件注入 13 + 五步检查点/API 告警闭环 9） |
| test_charset.py | `tests\test_charset.py` | G | 字符边界规范防线：框架文件 CRLF/BOM/UTF-8 解码扫描 + 铁律第 9 条存在性（7/7）；health_check 第⑧项必跑；扫描失败立即归一修复再交付 |
| test_platform_api.py | `tests\test_platform_api.py` | G | **平台 API 依赖保障**：opencode 二进制仍实现 experimental.chat.system.transform hook / jsonc 通道 / 插件注册 / 4 注入文件就绪（11/11）——opencode 升级或移除该实验性 API 时此测试失败告警；每次 health_check --run 必跑 |
| test_path_convert.py | `tests\test_path_convert.py` | G | path_convert 改动后强制（13/13：往返转换/STATE_FILES/残留扫描/tests 与 archive 目录跳过转换） |
| test_update_skill.py | `tests\test_update_skill.py` | G | 同步机制改动后强制（14/14，隔离临时仓库） |
| test_regedit.py | `tests\test_regedit.py` | G | 注册表改动后强制（本表与实际文件系统一致性） |
| test_tools_manifest.py | `tests\test_tools_manifest.py` | G | 工具总表改动后强制（分类计数吻合/待补充无重复/包可导入/表结构，21/21） |
| test_instructions.py | `tests\test_instructions.py` | G | instructions.md 改动后强制（章节/铁律互查/引用存在/技能清单与目录一致/编写规范，31/31） |
| test_evolution_gate.py | `tests\test_evolution_gate.py` | G | evolution_gate 改动后强制（快照/改动检测/流水兜底/自动测试触发/待补充清单/--drain 自愈补跑/max_n 限流/配套漏更检测/五步检查点，25/25） |
| test_health_check.py | `tests\test_health_check.py` | G | health_check 改动后强制（可运行/报告结构/七检查项/无失败项/regedit 登记/--run-quick 实跑，8/8） |
| test_sync_push.py | `tests\test_sync_push.py` | G | sync_push 改动后强制（无标记拒绝/非push拒绝/有效推送/标记清除/重推需重确认/WSL 路径判定与转换，11/11） |
| test_docs_sync.py | `tests\test_docs_sync.py` | G | docs-sync.md 改动后强制（变更类型/校验测试存在/被 regedit+AGENTS 引用，19/19） |
| test_audit_references.py | `tests\test_audit_references.py` | G | 框架引用审计（引用存在性/旧术语残留/README 双向一致，3/3） |
| test_repo_face.py | `tests\test_repo_face.py` | G | 仓库门面一致性（门面文件与框架现状对照 + STATE_FILES 工作树残留 + 本机用户名路径动态扫描，17/17；WSL 不可达回退 tests\repo_face\ 镜像） |
| test_setup_ps1.py | `tests\test_setup_ps1.py` | G | setup-windows.ps1 自动化测试（开关/部署范围/path_convert 体系/AST 语法/盘符动态探测/注册事件注入验证/ToolDir 空值防护/**必备工具缺失告警与退出码**，30/30；首跑即抓出 SkipDeploy 块缺 } 语法错误与 tests/tools 漏部署） |
| README.md（测试清单） | `tests\README.md` | F | 查测试入口与运行命令 |

## 数据层

| 注册项 | 位置 | 生效 | 说明 |
|---|---|---|---|
| tools-manifest.md（工具总表） | `<opencode配置目录>\` | H | 工具登记铁律（第 7 条）；唯一权威工具表 |
| docs-sync.md（配套同步映射表） | `<opencode配置目录>\` | G | 变更类型→必须同步更新文件清单的权威映射（铁律第 8 条引用）；evolution_gate 改动检测后按本表跑校验测试 |
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
| 门面文档同步 | update_skill SKILL.md「第五步·门面文档同步」+ test_repo_face.py | G | 仓库门面（根 README、copy\README/INSTALL/REQUIREMENTS）只在仓库工作树维护；推送前对照框架现状核查更新；无权限机器 pull 即得，不需 update_skill 修改 |
| 项目资产盘点 | update_skill SKILL.md「第二步·项目资产盘点」+ project_list.txt | G | 同步前遍历项目（当前目录 + project_list.txt 清单 + 显式指定），提取通用资产（新 skill/通用脚本）到全局并随同步上 GitHub；拿不准的列建议清单 |

## 进化层（第八层：保证智能自我进化）

| 注册项 | 位置 | 生效 | 说明 |
|---|---|---|---|
| evolution_skill（进化执行器） | `skills\default\evolution_skill\SKILL.md` | C | 铁律第 2 条复盘进化发现需固化时自动调用；五步固化（**每步强制输出【第X步·XX】标记行，gate --check-5step 程序化检测**）/ 注册表更新 / 工具登记 / 配套文档 / 校验自测全流程封装 |
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
