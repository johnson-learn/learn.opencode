# 智能进化日志（evolution log）

记录全局 skill 与指令文件的每次自我进化。格式：`[日期] 来源 → 更新点`

[2026-08-21] 用户规则 → 建立智能进化协议（instructions.md），确定五步固化流程与风险规避清单
[2026-08-21] 用户规则 → 进化协议修订：触发时机改为每次提问思考回答末尾强制触发；新增可移植性要求（经验通用化、本机路径占位化、区分通用经验与本机配置）
[2026-08-21] 首跑 update_skill 踩坑 → git commit/push 经 PowerShell 双引号嵌套时引号转义失败；经验：WSL 命令统一用 `bash -c '单引号包裹'` 避免引号地狱，commit 与 push 分步执行便于定位失败；已固化至 update_skill 技能环境注意
[2026-08-21] 用户规则 → update_skill 同步方式改为差异合入模式（禁止 rm -rf 删除替换）：仓库可能被多机器更新，覆盖式 cp 合入、保留仓库多出文件、M 类文件逐文件 diff 裁决、D 类文件恢复保留、冲突按信息完整性优先合并
[2026-08-21] 用户规则 → update_skill 升级为双向同步：功能1 本机→git（差异合入+commit+push）；功能2 git→本机（push 后 fetch 检查远端新提交，git diff old..HEAD 提取变更文件反向合入本机，冲突信息完整性优先）；执行时踩坑：本机状态文件 sync_target.txt 不应进仓库（.gitignore 排除）
[2026-08-25] 用户规则 → 路径可移植层建立：仓库文件占位符化（自动类/填写类两级）、path_convert.py 转换工具（正反斜杠+URL 风格+长路径优先）、双向同步自动转换；踩坑：path_map.txt 误入仓库（git rm --cached + .gitignore 排除）；bash 传参反斜杠被吃（--home 用正斜杠）；WSL 内运行 Windows Python 需显式 --home
[2026-08-25] 用户提问 → update_skill 增加第 0.5 步版本对齐检查（旧机器升级防倒退）：本机旧版本不得覆盖仓库新内容；仓库有本机无→先反向合入本机升级；两边不同→信息完整性优先合并；旧路径体系仓库先用 to_portable 就地升级
[2026-08-26] 用户规则（重要边界） → 同步边界铁律：只有显式调用 update_skill 才允许远端↔本机同步（pull/反向合入/复制同步目录/commit/push）；其它场景不得擅自执行任何 git 同步动作，本机 skill 文件直接编辑除外；已写入 instructions.md 全局规则第 0 条
[2026-08-26] 用户规则 → 目录选择幂等：setup 的 path_map.txt 已配置完整（数据类 5 项非 FILL_ME）则跳过交互直接复用；已配置项回车保留原值；update_skill 目标目录已存在且状态文件有效时不再重复询问
[2026-08-26] 远端实测反馈（重大踩坑） → 状态文件保护缺失导致双向同步链断裂：反向合入时仓库占位符版 path_map.txt 覆盖本机真实映射（<X>=<X> 自我指涉）→ to_portable 失去映射 → E:\ 真实路径泄漏进仓库（6 文件）→ 远端机器收到他机路径；修复：本机 path_map.txt 恢复真实映射、path_convert.py 增加 STATE_FILES 跳过保护、update_skill 固化状态文件保护三规则（反向合入跳过状态文件/转换前检查完整性）
[2026-08-26] 远端机器自主进化（双向协同验证） → 远端独立踩坑并修复：scan_unknown_placeholders 补 STATE_FILES 跳过（消除 path_convert 自身源码占位符键误报）、STATE_FILES 补自身跳过防自毁、update_skill 合并重复条目；本机经 update_skill 双向对齐（0f1e7fa）；本机执行教训：反向合入 cp 需显式跳过状态文件（本次侥幸未坏）
[2026-08-26] 用户规则 → update_skill 调用方式扩展：冒号后为路径（含盘符/UNC/斜杠特征）按目录指定处理；冒号后为问题任务（无路径特征）先执行问题再执行双向更新；无内容仅双向更新
[2026-08-26] 远端实测（对称回退重大教训） → 双方各持旧工作树 cp 覆盖导致对方修复被对称回退（path_convert 两处 STATE_FILES 保护被回退删除，远端恢复后推 74e35ea）；固化 update_skill 0.5 步「对称回退防护」：同名文件先查 git log 最后修改者判断差异方向，仓库 HEAD 含本机没有的修复 = 本机落后 = 先吸收后同步，严禁本机旧文件覆盖远端新修复
[2026-08-26] 用户规则 → update_skill 调用解析升级为顺序标记序列：消息按冒号分割片段，update_skill 标记=执行双向更新，其它片段=问题；按顺序交替执行（update_skill：问题=先更新后问题；问题：update_skill=先问题后更新；多标记依次类推）
[2026-08-26] 豆包外部分析（参考资料学习） → 提取 3 项改进：① 编写规范新增"入口 SKILL.md 精炼原则"（≤5KB 目标，大块知识移 references/，防单次加载上万 token）；② 新增 skill_validate.py 自检脚本（frontmatter/name/description/路由引用校验，兼容 BOM）；③ 已知短板清单（SKILL.md 过大/缺回归校验/进化靠自觉）作为后续改进方向；首测结果：3gpp 23KB、files 18KB、update_skill 10.5KB 超 8KB 阈值待瘦身
[2026-08-26] 用户要求（体系升级） → 自我进化从"靠自觉"升级为"程序化强制 + 轨迹驱动"：① skill-banner 插件监听 session.idle 自动注入进化检查任务（不靠模型自觉）；② evolution_trace.jsonl 轨迹记录；③ 五大自动进化能力判定规则（更新/生成=直接执行；合并/拆分/迁移=产出建议待用户确认）；④ 执行分级铁律（建议类不自动动手）；⑤ update_skill 附带轨迹分析产出进化建议
[2026-08-26] 用户规则 → 每条进化强制"校验+自测"（升级五步流程第 5 步）：① 内容正确性核查（命令/路径/参数可执行、无矛盾、标注齐全、通用性达标）；② 结构化自测（skill_validate.py：frontmatter/name/description/路由引用）；③ 行为自测（涉及可执行内容实际跑一遍验证，无法实测标注"未实测"）；④ 校验不通过立即修正才进入下一条
[2026-08-26] 瘦身执行（豆包短板落地） → 三个大 SKILL.md 拆 references：3gpp 23KB→13.2KB（-46%，6 个参考文件）、files 18KB→10KB（-44%，4 个）、update 13.9KB（2 个）；入口保留 frontmatter/流程/路由/铁律+引用行；skill_validate 自测 0 错误；踩坑：章节标题与关键词不一致导致首轮 2 章未移出（配置链梳理输出模板≠教学输出模板）
[2026-08-26] 用户要求（跨 skill 归位） → files_skill 的 3GPP 相关内容合并到 3gpp_skill，3gpp_skill 的文件处理内容合并到 files_skill：①「示意图绘制（NR-f40 教学专属）」→ 3gpp_skill/references/figure-svg.md；②「双轨提取」（通用文件处理能力）→ files_skill/references/dual-track-extraction.md 并通用化表述（一切含 OLE 公式文档，3GPP 为例）；③ files 残留 3 处 3GPP 特指措辞通用化（NR-f40 验证→实战验证、check-pdcch→通用表述）；踩坑：标题"示意图"非"示例图"导致首轮未命中
[2026-08-26] 用户指出（体系补全） → 建立工具总清单 tools-manifest.md（唯一权威工具管理表）：分类 A~G 共 34 项工具 + 本机配置 5 项 + 待补充 5 项；规则：新增/变更工具必须同步更新总表、新机器按总表逐项检查、各 skill 工具清单为摘录冲突以总表为准；instructions.md 编写规范新增 3c 条；豆包速查手册分析结论（10 个可补工具）已入总表"待补充"清单
[2026-08-26] 用户规则（收录范围扩展） → tools-manifest.md 收录范围强制扩展：① 项目级 skill 新增依赖工具也必须登记总表；② 思考回答中发现的好用工具/脚本（即使未归属任何 skill）也必须登记总表（先入待补充清单，装好后移入对应类别）；已写入 instructions.md 3c 条与总表头部说明
[2026-08-26] 用户规则（自动强制触发） → 所有进化行为（经验固化/工具登记/总表更新/校验自测）由插件 session.idle 程序化注入的强制清单任务驱动，不可跳过不可精简：① skill-banner.js 注入任务升级为 6 项强制清单（经验固化→工具登记→总表同步→校验自测→建议类→完成汇报）；② instructions.md 进化触发章节同步明确强制清单；③ 自动强制触发链：插件注入（程序化）→ 模型执行清单（强制）→ 校验自测（强制）
[2026-08-26] 用户质疑（机制验证） → 承认程序化机制仅纸面设计未实测；加固：① 插件加 plugin-evolution.log 日志（触发/成功/失败全记录，失败不再静默）；② 待实测方案：重启 opencode → 完成小对话 → 会话结束观察进化检查任务是否自动注入 + 查日志文件；③ 教训固化：程序化机制必须实测运行才算生效，写入机制后需标注"待实测"
[2026-08-26] 插件自测（test_plugin.js） → 15/15 通过：session.created 主/子会话 toast 行为、session.idle 进化任务注入（六项强制清单）、缺 sessionID 容错、未知事件零副作用、轨迹与日志落盘；自测发现真 bug：edit 误删 export 闭合（已修复）；test_plugin.js 纳入行为自测清单
[2026-08-26] 用户指出（commit message 摘要丢失） → 多个提交只剩 "sync:"（中文摘要经 PowerShell→wsl→bash 多层 shell 传递丢失）；修复：update_skill git 三步骤改为 printf 写 /tmp/cmsg.txt + git commit -F 文件方式传递；已存在裸 sync: 提交不改历史（共享仓库 amend 危险），向前修复
[2026-08-26] 用户要求（修炼文件归档全局） → 自查发现 skill 修炼文件散落 <项目目录>\temp：建立全局 <opencode配置目录>\tools\ 目录（path_convert/inject_skills/fetch_skills/slim_skills/cross_move/generalize 六个核心修炼工具）+ tools\archive\（18 个一次性已执行脚本归档）；测试用例已在 tests\；更新全部路径引用（instructions/skills）；三套测试全绿（10+15+0 错误）；原则：一切 skill 修炼文件必须放全局目录随 update_skill 同步 GitHub，任务产物（图片/文档）才留在项目 temp
[2026-08-26] 用户规则（项目资产盘点反哺全局） → update_skill 新增「第 0.9 步：项目资产盘点」：同步前遍历项目（当前工作目录 + project_list.txt 状态清单 + 用户显式指定目录），扫描三类资产（项目级 skill / 项目脚本 / tools 目录），按通用性判定（可复用+职责独立+非项目特定+其它机器使用框架功能时需要）提取到全局 skills\ 或 tools\，regedit.md 注册 + tools-manifest 登记 + 校验自测，随本次同步上 GitHub；拿不准的列「提取建议清单」待确认（与进化协议分级铁律一致）。本轮盘点 <项目目录>：6 个项目级 skill 均为全局同名副本（跳过）、无通用脚本（temp 为任务产物）——无提取项







