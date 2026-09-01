# find_skill 参考：深度研究流程模板（问题分解→检索计划→证据表→综合→带引用报告）

> 对应模块：`firecrawl-firecrawl-workflows-*-deep-research`（需 FIRECRAWL_API_KEY，先确认）；
> 免费备选：`parallel-web-parallel-agent-skills-*-deep-research`、`lllllllama-rigorpilot-skills-ai-research-explore`。

## 流程（每步输出到研究报告草稿）

```
【第 1 步】问题分解
- 原始问题：{…}
- 子问题 1..N：{…}（每个子问题一句话可回答）

【第 2 步】检索计划
- 每子问题：关键词组合 + 目标来源类型 + 预算（轮数/页面数）

【第 3 步】证据表（边检索边填，见 references/search-strategy.md §4）
- 关键结论必须有 ≥2 独立来源；级别标注 S/A/B/C

【第 4 步】综合
- 按子问题逐节作答；证据不足处显式标注"未证实/待补充"
- 矛盾证据并列呈现，给出倾向与理由，禁止隐瞒

【第 5 步】带引用报告
- 结论后标 [1][2] 引用号；文末参考文献表（标题/URL/访问日期）
- 报告头部注明：检索日期、来源数量、可信度说明
```

## 质量门槛

1. 每个子问题都有对应证据（不允许空转写空话）
2. C 级来源不得单独支撑结论
3. 报告末尾附"局限与未解问题"小节
