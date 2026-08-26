# 3gpp_skill 参考：配图要求（关键关系必须配图，光文字不够）

## 配图要求（关键关系必须配图，光文字不够）

- **判据**：涉及"空间关系 / 时序关系 / 块结构 / 流程跳转 / 处理链"五类关键关系时，仅文字描述不够，必须配 SVG 示意图。按图类对应（适用于任何专题，不止某一功能）：
  - **空间关系图**：两个或多个参数/资源在频域、时域或物理位置上的相对关系（如 Point A / offsetToPointA / \(k_{SSB}\) / SSB 与资源块栅格的错位关系、CORESET 与 SSB 相对位置、BWP 带宽关系）
  - **块结构图**：信道/信号/协议块在资源网格中的布局（如 SSB 时频结构、PUCCH 格式布局、资源网格层次、PDU 结构图）
  - **时序图**：周期、窗口、定时关系在时间轴上的排布（如 SI 窗口、修改周期、beam sweep、寻呼时机、SPS 周期、切换时延定义）
  - **流程图**：多步/多分支流程（如信令流程、双路径决策、端到端流程、状态转移）
  - **处理链图**：比特/数据处理步骤（如 PBCH/PDCCH/PDSCH 编码链、CRC/RNTI 加扰链、LDPC/Polar 链路）
- **工具选型（禁止手写 SVG 坐标——易错位、布局差；按图类选工具自动生成）**：
  | 图类 | 工具 | 典型用例 |
  |---|---|---|
  | 流程图/状态机 | **Mermaid flowchart**（`.mmd` → `mmdc.cmd -i x.mmd -o x.svg -b white`） | 双路径、端到端、决策分支 |
  | 信令/时序图 | **Mermaid sequenceDiagram** | RACH、SI 请求、寻呼/切换流程时序 |
  | 结构/网格/频谱块图 | **matplotlib**（`pcolormesh`+`scatter`+`annotate` → `savefig(x.svg)`，中文字体 Microsoft YaHei） | SSB 块图、资源网格、频域关系图 |
  | 走势图/波形/时间轴 | **matplotlib**（`plot`/`barh`/`axvspan`/`fill_between`） | beam sweep、门限曲线、窗口排布、功率曲线 |
  | 精细标注空间图 | matplotlib `annotate` 优先；手写 SVG 仅兜底 | 多引线示意图 |
  - Mermaid 渲染注意：PowerShell 下须调 `mmdc.cmd`（非 mmdc）；设环境变量 `PUPPETEER_EXECUTABLE_PATH` 指向系统 Chrome 跳过 Chromium 下载
- **SVG/图技术规范**（对所有产出图统一生效）：图内公式/变量用原生上下标（Mermaid HTML 实体 `<sub>`；matplotlib mathtext `$k_{SSB}$`；手写 SVG 用 `<tspan baseline-shift="sub|super">`，禁用 foreignObject 嵌 MathJax）；标注错行布局 + 虚线引线；任何文字、图标不得重叠；超宽文字缩小字号适配而非硬挤；图内标注一律用原协议符号（k_SSB、N_CRB^SSB、offsetToPointA 等），图注与正文统一 MathJax `\(...\)` 正式符号；**禁止自造比喻词汇**（如"灯塔/司令部/户口本/指路牌"类，图内与正文一律禁止）
- **符号一致性（图 ↔ 正文双向）**：图上的变量标号与正文解释必须用同一套正式符号——正文所有变量一律 MathJax（含小节标题、表格单元格、例题、习题答案、计算器 JS 输出；JS 输出用 HTML `<sub>/<sup>`），不得一处 `\(k_{SSB}\)` 一处裸写 k_SSB；交付前跑残留扫描（`N_ID\^|k_SSB|L_max|c_init` 等裸写法计数应为 0）
- **交付校验**：重叠检测（check-overlap.ps1 或 Python 解析版）归零；图错位必查项——文字出画布、跨块文字、图例重叠、箭头穿过文字、窗口/刻度比例换算错误（如 20 槽多乘 10 成 380px 类）；改动后回归重跑

---

