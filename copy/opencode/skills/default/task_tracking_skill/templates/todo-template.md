# 任务窗（todo）标准写入模板 —— task_tracking_skill

本模板提供任务窗（todowrite 工具）的标准写入格式与时机，随 task_tracking_skill 使用。复制即用。

## 一、单个 todo 项的标准格式（todowrite 参数）

```
{
  "content": "<任务内容：一句话，简明、可执行>",
  "status": "pending | in_progress | completed | cancelled",
  "priority": "high | medium | low"
}
```

- **content**：一句话讲清"做什么"（含对象/目标），不用超长描述；子智能体任务也各为一项。
- **status**：四种——`pending`(待做)/`in_progress`(进行中)/`completed`(完成)/`cancelled`(取消)。
- **priority**：high/medium/low。

## 二、核心要求：实时更新

**实时更新** = 任务窗条目列表中，**每完成一个任务即同步更新该条目状态，逐条推进直至全部 completed**（in_progress→completed；做了没标/标了没做都要立即纠正）。这是任务窗生效的第一性要求。

## 三、四项强制时机（与 AGENTS 铁律第 8 条一致）

| 时机 | 动作 |
|---|---|
| 0. 收到新要求/新消息 | **第一步即建/更新任务窗**，为该要求建项并标 `in_progress`（禁止先做后补窗） |
| 1. 每完成一个任务 | **立即把对应条目 status 改为 `completed`**（逐条推进直至全清，禁止最后批量补） |
| 2. 用户更新要求 | 同步增删改主+子智能体任务项，使列表始终与最新要求一致 |
| 3. 任务量大 | 用子智能体(task)分担并行，子智能体任务也纳入同一窗跟踪 |

## 四、示例

### 场景：收到"分析协议 X 差异"要求，分 2 步（读 + 写），可能派 1 子智能体

**收到要求后第一步（建窗）：**
```
content: 读协议 X 差异相关章节；status: in_progress；priority: high
content: 生成差异分析结论；status: pending；priority: high
```

**每步完成立即标：**
```
content: 读协议 X 差异相关章节；status: completed；priority: high   ← 读完即标完成
```

**派子智能体时（纳入同窗）：**
```
content: 子智能体A: 精读 38.331 BWP 章节；status: in_progress；priority: high
content: 子智能体B: 精读 38.213 CORESET0 章节；status: in_progress；priority: medium
```

**收尾：**
全部项 `completed`，或未完成项在 `in_progress` 且给出合理说明——不得有悬空"创建后不管"。

## 五、自检口诀（交付前）

- 每条新要求对应一项？有没有"收到要求却没建窗"？
- **每完成一个任务是否即时 `completed`？是否逐条推进直至全部 completed（实时更新）？** 有没有"最后批量补/做了没标/标了没做"？
- 用户更新要求后列表与最新一致？子智能体任务在窗内？

> 模板复用说明：迁移到新机器无需任何本机路径；仅依赖内置 todowrite 工具。
