# 进化规则（Evolution Rules）—— 最新进化规则权威文件

> **本文件定位（用户 2026-08-26 定）**：进化不是机械记录历史——本文件承载**最新进化的规则与机制**，
> 是规则类经验的可执行载体之一（与 AGENTS.md 铁律 / regedit.md 登记 / instructions.md 详版 / 各 SKILL.md 流程并列）。
> **历史流水在 evolution_log.txt**（只增不改）。
> **更新本文件的强制流程**：① 结合 evolution_log.txt 内容核对（新规则与历史教训不矛盾）；② **弹窗让用户确认**
> （question 工具）是否更新；③ 确认后才 edit 本文件；④ 更新后跑 test_evolution_consistency.py。

## 现行进化规则（按固化时间倒序，均来自 evolution_log.txt 沉淀）

### 2026-08-27
1. **五步检查点程序化强制**：执行固化（声明"已固化"）必须按序输出【第一步·归纳】~【第五步·校验】标记行；evolution_gate --check-5step 由插件 session.idle 自动检测（拉会话消息→缺步检出→警告并入进化检查任务）；只声明"无固化"不需五步
2. **注册事件注入（E 类平台直读）**：opencode 1.18 系列不消费 instructions 字段（实测：解析进配置但系统提示构建只认 AGENTS.md/CLAUDE.md/CONTEXT.md）；平台注入通道=skill-banner 注册 experimental.chat.system.transform（每次请求构建系统提示时直读 instructions/regedit/docs-sync/tools-manifest 四文件 push 进 output.system，mtime 缓存，OPENCODE_DISABLE_MD_INJECT=1 禁用）
3. **平台 API 依赖保障**：experimental.chat.system.transform 是实验性 API——test_platform_api.py（11/11）硬检查二进制 hook 实现存在性，health_check 第⑦项必跑，插件 session.created 异步检测失败即 toast 告警；失效回退预案：重启 instructions 字段（若新版实现）→ 铁律第 0 条 B 类路径
4. **experimental API 使用前提**：opencode 配置字段"被解析≠被消费"——必须用 debug config + 二进制字符串证据 + 新对话实测三段法核实后才可依赖
5. **语言跟随裁定规则**：语言跟随的唯一权威依据=当条消息实际语言（思考/回答/输出三者一致跟随）；平台语言指令（【语言指令·平台检测】）只是会话默认基调兜底，与当条消息冲突或平台检测失效（未触发/恒旧值）时一律以当条消息实际语言为准——实测事故：message.part.updated 语言检测本机未触发（plugin-evolution.log 无记录），指令恒为"中文"致英文提问轮"思考中文、回答英文"分裂；规则兜底写入 instructions.md 第 1 条裁定条款

### 2026-08-26
1. **进化门禁机制（evolution_gate.py）**：机制步骤（流水兜底追加/自动测试/一致性校验/改动检测/五步检查点检测）由脚本确定性执行——插件 session.created 调 --snapshot、session.idle 调 --check、五步标记由 --check-5step 检测；模型只负责智能部分（经验归纳/归属判定/edit 固化）。解决"提示语体系无法 100% 保证必须步骤执行"的物理上限
2. **本文件定位**：进化规则文件（非历史流水）；历史流水独立于 evolution_log.txt
2. **进化规则更新流程**：核对历史（evolution_log.txt）→ 弹窗确认 → 更新本文件 → 校验自测
3. **evolution_log.txt 只增不改**：追加尾部，禁止替换既有条目
4. **弹窗确认**：update_skill 第五步前强制（question 工具弹窗，禁止文字提问代替；未确认前禁 commit/push）
5. **修改复盘核查**：每个文件修改完成后、自测前强制自查（改了什么/应改载体是否全改/占位符可移植性/配套文档）
6. **归属二分铁律**：规则/流程/机制类经验必须写入可执行载体（SKILL.md/instructions.md/regedit.md/AGENTS.md/本文件），
   只写 evolution_log.txt = 归属失败；记录/事实类才仅写历史流水
7. **对端修改评审**：pull 到对端新提交后逐 diff 评审；不合理则回退+注释（commit/时间/回退原因三要素）
8. **提交前可移植性校验**：待提交内容不得含本机特征（home 真实路径/用户名路径/本机特有绝对路径），
   test_update_skill.py 用例 8 已入提交前自测库
9. **同步过滤规则**：判断标准=其它机器使用框架/skill/功能时需要的才同步；临时文件由 .gitignore 自动过滤
10. **五步同步框架**：吸收远端→修改→自测（缺用例先补写，双向更新用例须模拟远端）→弹窗确认→按选择执行
11. **项目资产盘点**：同步前遍历项目提取通用资产到全局（拿不准的列建议清单）
12. **测试先行**：每次修改必须跑对应测试；新增机制必须同步新增测试用例并更新 tests/README.md
13. **进化触发双机制**：AGENTS.md 铁律第 2 条（每次响应复盘进化）主 + 插件 session.idle 兜底注入（幂等去重）
14. **同步边界铁律**：只有显式 update_skill 才允许 git 同步动作
15. **SKILL.md 体积门限可配置**：默认 8KB，超限待决清单三选一（改门限/忽略/忽略全部），skill_validate_config.json 持久化
16. **注册表机制**：regedit.md 全体系组件加载方式登记（A~H 八分类），组件变更必须同步更新并跑 test_regedit.py
17. **进化质量与可持续性（2026-08-28 报告评审后新增）**：① 固化判定四条件（≥2 场景/可移植/不重复/有边界）——不满足只记流水事实类；② 经验状态标记（active/deprecated/invalidated，只追加标记不删改历史）；③ 重要经验二次验证（标待二次验证→下次任务验证→记结果）；④ 注入量管控（四注入文件合计上限 30KB，超限触发精简，health_check 告警）；⑤ 使用率自审（约 10 次会话未被提及→提示下沉/标 deprecated）；⑥ 冲突显式裁决（禁止静默二选一，响应中标注并同步改旧条目）
