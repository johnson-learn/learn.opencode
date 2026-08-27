# 3gpp_skill 参考：示意图绘制（NR-f40 实战打磨）

## 示意图绘制（文本/数据 → SVG，NR-f40 实战打磨）

**判据**：涉及空间关系 / 时序关系 / 块结构 / 流程跳转 / 处理链五类关键关系时，仅文字不够，必须配图。**禁止手写 SVG 坐标**（易错位、布局差）——按图类选工具自动生成：

| 图类 | 工具 | 生成方式 | 典型用例 |
|---|---|---|---|
| 流程图（决策/双路径/多分支） | **Mermaid flowchart**（首选） | 写 `.mmd` → `mmdc.cmd -i x.mmd -o x.svg -b white` 渲染 | 按需 SI 双路径、端到端流程、状态机 |
| 信令/时序图 | **Mermaid sequenceDiagram**（首选） | 同上 | RACH 流程、SI 请求/响应、寻呼时序 |
| 状态图/类图/甘特 | Mermaid stateDiagram / classDiagram / gantt | 同上 | RRC 状态机、修改周期甘特排布 |
| 结构/网格/频谱块图 | **matplotlib**（首选） | `pcolormesh` 网格着色 + `scatter` 打点 + `annotate` 引线 → `savefig(x.svg)`；中文字体 `plt.rcParams['font.sans-serif']=['Microsoft YaHei']` | SSB 时频块图、资源网格、Point A 频域关系 |
| 走势图/曲线/波形 | **matplotlib** | `plot`/`barh`/`axvspan`/`fill_between` | 波束扫描时间轴、门限曲线、时序排布 |
| 精细标注空间图 | matplotlib `annotate`（xytext 错行）优先；手写 SVG 仅兜底 | — | 带多引线标注的示意图 |

**工作流**：① Mermaid：写 `.mmd` 源码 → 设 `$env:PUPPETEER_EXECUTABLE_PATH`（指向系统 Chrome）→ `& "<用户AppData目录>\npm\mmdc.cmd" -i in.mmd -o out.svg -b white`（注意用 mmdc.cmd 而非 mmdc，ps1 被执行策略禁）；② matplotlib：脚本 `savefig(out.svg, format='svg')`；③ 两种产出 SVG 后嵌入 HTML 的 `<figure>`，与手写 SVG 同跑重叠检测兜底；④ 图内变量用 Mermaid/matplotlib 原生上下标（matplotlib 用 LaTeX mathtext 如 `$k_{SSB}$`；Mermaid 支持 HTML 实体 `<sub>`）。

**质量要点**：文字/图标不重叠（重叠检测归零）；超宽文字缩小字号适配而非硬挤；图内与图注统一用正式符号（正文 MathJax `\(...\)`、图内 mathtext/HTML 下标）；禁止自造比喻词汇。
