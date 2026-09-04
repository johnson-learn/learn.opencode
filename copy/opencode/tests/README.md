# 测试目录（Tests）—— 自测用例统一管理

> 进化协议铁律：**每个修改都必须自测**——有对应用例则运行；无用例则在本目录新增用例后再改。
> 测试目录随仓库同步（update_skill 的 scripts/ 或独立 tests/ 目录），移植后同样可用。

## 测试清单

| 被测对象 | 测试文件 | 运行命令 | 状态 |
|---|---|---|---|
| skill 结构（frontmatter/name/description/路由引用/体积门限） | `skill_validate.py` | `python tests\skill_validate.py <opencode配置目录>\skills` | ✓ 已建（门限可配置，见 skill_validate_config.json） |
| skill_validate 配置机制（门限修改/忽略/持久化） | `test_skill_validate_config.py` | `python tests\test_skill_validate_config.py` | ✓ 7/7 |
| skill-banner 插件（事件处理/任务注入/日志落盘/注册事件系统提示注入/六步检查点/API 风险告警闭环/待办内存传递/平台语言检测持续约束/新增文件适配第 7 项/使用率追踪端到端） | `test_plugin.js` | `node tests\test_plugin.js`（需 node） | ✓ 52/52（事件分支 20 + 注册事件注入 14 + 六步/API/待办 7 + 语言检测 5 + 使用率追踪 6） |
| 平台 API 依赖保障（opencode 二进制 hook 存在性/jsonc 通道/插件注册/注入文件就绪） | `test_platform_api.py` | `python tests\test_platform_api.py` | ✓ 11/11 |
| 字符边界规范防线（框架文件 CRLF/BOM/编码一致性扫描 + 铁律第 9 条存在性） | `test_charset.py` | `python tests\test_charset.py` | ✓ 7/7 |
| path_convert.py（往返转换/STATE_FILES/残留扫描白名单化/tests 与 archive 跳过转换/空值映射过滤/工具类全集检出） | `test_path_convert.py` | `python tests\test_path_convert.py` | ✓ 23/23 |
| update_skill 双向同步（调用解析/commit 摘要/状态保护/对称回退判定/五步流程要素/模拟远端操作/可移植性校验/弹窗确认分支） | `test_update_skill.py` | `python tests\test_update_skill.py`（需 Windows git，隔离临时仓库） | ✓ 40/40 |
| 注册表一致性（regedit.md ↔ 文件系统 ↔ AGENTS.md 互查） | `test_regedit.py` | `python tests\test_regedit.py` | ✓ 47/47 |
| tools-manifest 完整性（分类计数吻合/待补充无重复/包可导入/表结构） | `test_tools_manifest.py` | `python tests\test_tools_manifest.py` | ✓ 21/21 |
| instructions.md 规则一致性（章节/铁律互查/引用存在/技能清单与目录一致/编写规范） | `test_instructions.py` | `python tests\test_instructions.py` | ✓ 31/31 |
| evolution 一致性（evolution_log.txt 近 5 条「」声明落入规则文件/evolution.md 规则文件定位与弹窗确认流程抽查） | `test_evolution_consistency.py` | `python tests\test_evolution_consistency.py` | ✓ 15/15 |
| evolution 门禁（快照/改动检测/流水兜底追加/自动测试触发/待补充清单/--drain 自愈补跑/max_n 限流/配套漏更检测/六步检查点（含第三步·确认）/判定四条件声明与可追溯/四条件依据软提示与渐进硬告警/阈值配置化/经验健康引擎结构化扫描/新增与删除文件检测） | `test_evolution_gate.py` | `python tests\test_evolution_gate.py` | ✓ 45/45 |
| 健康检查（可运行/报告结构/九检查项/无失败项/regedit 登记/--run-quick 实跑/注入量管控） | `test_health_check.py` | `python tests\test_health_check.py` | ✓ 9/9 |
| sync_push 推送门禁（无标记拒绝/非push拒绝/有效推送/标记清除/重推需重确认/WSL 路径判定/自动 to_portable/可移植性阻断/msgfile_exists 双通道） | `test_sync_push.py` | `python tests\test_sync_push.py` | ✓ 19/19 |
| **L1 领域自测**（各 skill 内：入口规范/模块引用无悬空/references 无悬空/技能特定断言；program_skill 另有 c-project 骨架 WSL 实编译行为自测） | `skills\<skill>\tests\test_skill_self.py` | `python skills\<skill>\tests\test_skill_self.py`（evolution_gate 改动 skill 时自动精准触发） | ✓ 7 个 skill 全绿 |
| docs-sync 映射表完整性（变更类型/校验测试存在/被 regedit+AGENTS 引用） | `test_docs_sync.py` | `python tests\test_docs_sync.py` | ✓ 19/19 |
| 框架引用审计（框架自有文件引用存在性/旧术语残留/README 双向一致） | `test_audit_references.py` | `python tests\test_audit_references.py` | ✓ 3/3 |
| 仓库门面一致性（门面文件与框架现状对照 + STATE_FILES 残留 + 本机路径动态扫描 + 仓库内 repo_face 镜像=门面一致性 9 对，WSL 不可达时回退 repo_face 镜像） | `test_repo_face.py` | `python tests\test_repo_face.py` | ✓ 27/27 |
| setup-windows.ps1（2026-09-01 检测模式：开关精简/工具清单必须可选分类/共享检测模块 setup-check/双通道检测/PATH 自动修复/未装提示跳过/无自动安装残留/npm-pip 缺失汇总/WSL 检测化/install-tools 一键安装脚本/AST 语法/部署范围/path_convert 体系/盘符动态探测/注册事件注入验证/必备工具缺失告警/tools-manifest 总表自动对齐） | `test_setup_ps1.py` | `python tests\test_setup_ps1.py` | ✓ 78/78 |

> skill_validate 体积门限：默认 8KB，超限输出「待决清单」，用户选择（--set-limit 改门限 / --ignore 忽略指定 / --ignore-all 忽略全部）写入 `skill_validate_config.json` 持久化，后续一致性生效（当前本机门限 15KB，用户 2026-08-26 设定）。

## 新增测试用例规范

1. 被测对象有修改 → 先查本表；无用例 → 在 tests\ 新建 `test_<对象>.py`/`.js` 再动手
2. 用例格式：独立可运行（`python`/`node` 直接跑）、输出"通过 N 项/失败 M 项"、失败退出码非 0
3. 测试数据用临时目录，跑完清理
4. 断言写错导致的失败也是 bug——修正断言后重跑至全绿，并记录踩坑
5. 新用例建好后立即登记到本表

## 本机路径约定

- 测试目录：`<项目目录>\tests\`（本机 <opencode配置目录>\tests）
- path_convert.py 测试副本：`tests\path_convert.py`（与被测源保持同步）
