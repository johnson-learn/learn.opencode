# 3gpp_skill 参考：协议配置链梳理通用模版（config-chain-template）

> 适用：任何"3GPP 协议配置链梳理"任务（PDCCH、PDSCH、BWP、RRC、CSI 等）。
> 本质不是逐字段翻译协议，而是梳理"配置从哪来、到哪去"的链条。本文件为通用要求，可移植到其它机器直接套用。
> 依据：NR-f40 文档 PDCCH 配置链多轮打磨产出。

## P0 组织原则（最高优先级）

1. **按源头信令分主线**：
   - 信令源头不同，**必分开成独立主线**，不强行合并。
   - "源头"= 谁以何种消息（广播/专用）把配置送到 UE，常见为 **MIB、SIB1、RRCSetup、RRCReconfiguration**（或对应域的 Setup / Reconfig / 系统消息）。
2. **源头相同则同类**：同一条源头的多级配置放同一主线内；内容相近但源头不同 → 分开列，用"作用/用途"说明区分。
3. **给完整配置链，不只列末梢**：每条主线必须从根（源头消息）到叶（目标功能 IE）把**每个中间层级（容器 IE 逐级嵌套）写全**，禁止只给最后一两个 IE。
4. **逐级分层展示**：配置链**一级一级独立成行**、树形缩进（`└─` / `├─`），**禁止**用 `a:b → c:d → e:f` 一行串联多个层级。
5. **字段名与类型名成对并标注**：
   - 统一写 `字段名 : 类型名`（如 `spCellConfigCommon : ServingCellConfigCommon`）。
   - 强调 38.331 存在"字段名（小写）与类型名（大写）重名 / 易混"，**读协议以冒号右侧类型名为准**。
   - 注意 **SIB 版 / 完整版后缀差异**（如 `ServingCellConfigCommonSIB` vs `ServingCellConfigCommon`）。

## P1 每主线必含三要素

| 要素 | 要求 |
|---|---|
| **源头信令** | 明确写"MIB、SIB1、RRCSetup、RRCReconfiguration 等源头信令" |
| **完整配置链** | 树形、逐级、`字段:类型` 成对 |
| **作用 / 用途** | **详细说明**这条链"用来干什么""和内容相近的其它链有何不同" |

## P2 层级坐标法（可复用框架）

38.331 常采用"两层 Common/Dedicated"结构，梳理时用**两级坐标**避免混淆：

- 小区级：`ServingCellConfigCommon`（公共）vs `ServingCellConfig`（专用）
- BWP 级：每 BWP 内 `bwp-Common`（公共）vs `bwp-Dedicated`（专用）

**运维方法**：先定"源头信令"，再**一级一级**到 cell(Common/Dedicated) 分片、BWP(Common/Dedicated) 分片，一级一级到最后才是目标 IE，**中间不可跳过**。

## P3 协议细节辨析（遇到时展开成表）

- **查表 vs 配置**：明示哪些参数来自"协议规定查表"（如 TS 38.213 表 10.1-1 / 第 13 节），哪些来自"RRC 配置"。判据以协议原文（"given in Table xx.x-x"）为准。
- **同一 IE 多信令通道**：同一份概念配置（如 ServingCellConfigCommon）在不同信令（SIB1 广播 vs RRCReconfiguration 专用）里以不同版本 / 类型出现时，说明其"本小区 vs 目标小区（切换）"的用途差异。
- **取值 / 边界**：如"该 ID=0 特指什么""该字段缺省时回退 / 查表 / 取默认"。

## P4 结尾

- 附"源头汇总总表"（源头 × 广播/专用 × 容器 × 用途）。
- 零散细节（编号上限、监控时机、数量限制、术语）统一收进**附录表格**，不散落正文。
- 标注协议版本与文件来源。

## 样例：SIB1 配置 PDCCH（演示配置链格式）

**源头信令**：SIB1（广播）

**完整配置链**（逐级分层、字段名:类型名、从根到叶、中间层不跳过）：
```
SIB1
 └─ servingCellConfigCommon : ServingCellConfigCommonSIB
     └─ downlinkConfigCommon : DownlinkConfigCommonSIB
         └─ initialDownlinkBWP : BWP-DownlinkCommon
             └─ pdcch-ConfigCommon : PDCCH-ConfigCommon
                 ├─ searchSpaceSIB1 : SearchSpaceId                  (→Type0 CSS，SIB1调度)
                 ├─ searchSpaceOtherSystemInformation : SearchSpaceId (→Type0A CSS，其他SIB)
                 ├─ ra-SearchSpace : SearchSpaceId                   (→Type1 CSS，RAR)
                 ├─ pagingSearchSpace : SearchSpaceId                (→Type2 CSS，寻呼)
                 └─ commonSearchSpaceList : SEQUENCE OF SearchSpace   (额外公共CSS)
```

**作用 / 用途（详细）**：本小区所有 UE 共享的公共 PDCCH 配置，服务 SIB 调度、随机接入响应 RAR、寻呼等公共控制；与 RRCSetup / RRCReconfiguration 的专用配置（USS、Type3 CSS）不同——这里是"小区公共"，专用链只服务单个 UE 的数据调度（虽然同经 BWP 的 bwp-Common / bwp-Dedicated 分片承载，但容器 IE 与源头信令不同）。

**格式要点对照（正确 vs 错误）**：
- ✅ 一级一行树形（`└─`/`├─`），不写 `a:b → c:d → e:f`
- ✅ `字段名 : 类型名` 成对
- ✅ 源头 = SIB1 写清
- ✅ 中间层（ServingCellConfigCommonSIB → DownlinkConfigCommonSIB → BWP-DownlinkCommon → PDCCH-ConfigCommon）不跳过
- ✅ 用途详细说明（做什么 + 与相近链的区别）
