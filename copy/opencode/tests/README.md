# 测试目录（Tests）—— 自测用例统一管理

> 进化协议铁律：**每个修改都必须自测**——有对应用例则运行；无用例则在本目录新增用例后再改。
> 测试目录随仓库同步（update_skill 的 scripts/ 或独立 tests/ 目录），移植后同样可用。

## 测试清单

| 被测对象 | 测试文件 | 运行命令 | 状态 |
|---|---|---|---|
| skill 结构（frontmatter/name/description/路由引用） | `skill_validate.py` | `python tests\skill_validate.py <opencode配置目录>\skills` | ✓ 已建 |
| skill-banner 插件（事件处理/任务注入/日志落盘） | `test_plugin.js` | `node tests\test_plugin.js`（需 node） | ✓ 15/15 |
| path_convert.py（往返转换/STATE_FILES/残留扫描） | `test_path_convert.py` | `python tests\test_path_convert.py` | ✓ 10/10 |
| update_skill 双向同步（调用解析/commit 摘要/状态保护/对称回退判定） | `test_update_skill.py` | `python tests\test_update_skill.py`（需 Windows git，隔离临时仓库） | ✓ 14/14 |
| tools-manifest 完整性（A~G 分类检查命令可执行） | `test_tools_manifest.py` | 待新增 | ○ |
| instructions.md 规则一致性（与各 skill 引用互查） | `test_instructions.py` | 待新增 | ○ |

## 新增测试用例规范

1. 被测对象有修改 → 先查本表；无用例 → 在 tests\ 新建 `test_<对象>.py`/`.js` 再动手
2. 用例格式：独立可运行（`python`/`node` 直接跑）、输出"通过 N 项/失败 M 项"、失败退出码非 0
3. 测试数据用临时目录，跑完清理
4. 断言写错导致的失败也是 bug——修正断言后重跑至全绿，并记录踩坑
5. 新用例建好后立即登记到本表

## 本机路径约定

- 测试目录：`<项目目录>\tests\`（本机 <opencode配置目录>\tests）
- path_convert.py 测试副本：`tests\path_convert.py`（与被测源保持同步）
