# 新增文件四问适配输出模板（evolution_skill templates）

> 门禁（evolution_gate --check）输出【新增文件】清单后，对每个文件按四问分析并输出：

```
文件：{路径}
① 它是什么：skill 入口 / skill 附属 references / 测试 / 工具脚本 / 插件 / 规则文档 / 一次性产物
② 是否纳入框架：可复用通用 → 纳入；一次性产物 → 存档 tools\archive\ 或忽略
③ 归到哪类载体：regedit（技能层/工具层/测试层/插件层/数据层）+ tools-manifest 类别 + instructions 技能清单
④ 触发方式：全局仅显式（C+D）/ 项目级默认触发（C）+ 配套测试

【用户决策】question 弹窗 → 适配 / 忽略 / 存档

【纳入动作】
- regedit.md 登记 + tools-manifest.md 登记 + instructions.md 清单（如涉）
- 测试：skill_validate.py / test_regedit.py / test_instructions.py / test_tools_manifest.py

【纳入验收】全部测试绿灯才算完成；失败项=适配未完成证据，修复后重跑
```
