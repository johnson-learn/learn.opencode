# 测试目录（Tests）—— 自测用例统一管理

> 进化协议铁律：**每个修改都必须自测**——有对应用例则运行；无用例则在本目录新增用例后再改。
> 测试目录随仓库同步（update_skill 的 scripts/ 或独立 tests/ 目录），移植后同样可用。

## 测试清单

| 被测对象 | 测试文件 | 运行命令 | 状态 |
|---|---|---|---|
| skill 结构（frontmatter/name/description/路由引用/体积门限） | `skill_validate.py` | `python tests\skill_validate.py <opencode配置目录>\skills` | ✓ 已建（门限可配置，见 skill_validate_config.json） |
| skill_validate 配置机制（门限修改/忽略/持久化） | `test_skill_validate_config.py` | `python tests\test_skill_validate_config.py` | ✓ 7/7 |
| skill-banner 插件（事件处理/任务注入/日志落盘） | `test_plugin.js` | `node tests\test_plugin.js`（需 node） | ✓ 20/20 |
| path_convert.py（往返转换/STATE_FILES/残留扫描） | `test_path_convert.py` | `python tests\test_path_convert.py` | ✓ 9/9 |
| update_skill 双向同步（调用解析/commit 摘要/状态保护/对称回退判定/五步流程要素/模拟远端操作/可移植性校验/弹窗确认分支） | `test_update_skill.py` | `python tests\test_update_skill.py`（需 Windows git，隔离临时仓库） | ✓ 40/40 |
| 注册表一致性（regedit.md ↔ 文件系统 ↔ AGENTS.md 互查） | `test_regedit.py` | `python tests\test_regedit.py` | ✓ 47/47 |
| tools-manifest 完整性（分类计数吻合/待补充无重复/包可导入/表结构） | `test_tools_manifest.py` | `python tests\test_tools_manifest.py` | ✓ 21/21 |
| instructions.md 规则一致性（章节/铁律互查/引用存在/技能清单与目录一致/编写规范） | `test_instructions.py` | `python tests\test_instructions.py` | ✓ 31/31 |
| evolution 一致性（evolution_log.txt 近 5 条「」声明落入规则文件/evolution.md 规则文件定位与弹窗确认流程抽查） | `test_evolution_consistency.py` | `python tests\test_evolution_consistency.py` | ✓ 15/15 |
| evolution 门禁（快照/改动检测/流水兜底追加/自动测试触发/待补充清单/--drain 自愈补跑/max_n 限流） | `test_evolution_gate.py` | `python tests\test_evolution_gate.py` | ✓ 14/14 |

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
