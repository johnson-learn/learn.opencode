# 配套文档同步映射表（Docs Sync Map）—— 变更类型 → 必须同步更新的文件

> 本表是"框架变更后配套文档更新"的唯一权威清单（用户定）。
> 使用方式：任何变更发生后，按「变更类型」行查「必须同步更新的文件」列逐项更新，并跑「校验方式」列测试。
> 登记：regedit.md 铁律层（A 类系统注入）；铁律第 8 条引用；evolution_gate 的 --check 按本表程序化反向校验（改了 A 但应同步的 B 未改 → 输出漏更警告）。
> 本表自身变更 → 更新 regedit.md 登记说明并跑 test_regedit.py。

| 变更类型 | 必须同步更新的文件 | 校验方式（程序化） |
|---|---|---|
| **skill 新增/删除/改名** | instructions.md 技能清单表、regedit.md 技能层、tests\README.md（如涉测试）、skill-banner 动态扫描（自动） | test_instructions（清单双向一致）、test_regedit（登记一致） |
| **测试用例新增/变更** | tests\README.md（用例数+描述）、regedit.md 测试层（如新增测试文件） | test_regedit、各测试自跑 |
| **工具新增/变更** | tools-manifest.md（分类表+速览计数）、regedit.md 工具层 | test_tools_manifest（计数吻合）、test_regedit |
| **流程/机制变更** | 对应 SKILL.md、instructions.md、regedit.md（如登记条目）、AGENTS.md（如需铁律） | test_evolution_consistency（「」声明落规则文件）、test_update_skill（五步要素） |
| **规则变更** | evolution.md（规则文件，**弹窗确认后更新**）、instructions.md、evolution_log.txt（流水） | test_evolution_consistency |
| **目录/结构变更（文件移动等）** | 全部引用该路径的文件 + regedit.md 位置列 | test_regedit（文件存在反查）、test_instructions |
| **数据/状态文件变更** | regedit.md 数据层登记说明 | test_regedit |
| **插件变更** | regedit.md 插件层、tests\README.md | test_plugin、test_regedit |
| **opencode.jsonc 配置变更**（配置项增减等） | regedit.md 铁律层生效方式登记更新 + 重启 opencode 验证变更生效 | test_regedit |
| **仓库门面文档变更**（根 README、copy\README/INSTALL/REQUIREMENTS、copy\setup 脚本、tools-manifest） | 仓库工作树直接编辑（不在本机全局目录）；update_skill 第五步「门面文档同步」环节核查+推送；**同步刷新仓库内与本机 repo_face 镜像（9 文件）** | test_repo_face（含 6d 镜像一致性） |
