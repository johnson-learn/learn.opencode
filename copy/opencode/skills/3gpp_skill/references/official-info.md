# 3gpp_skill 参考：3GPP 官网权威信息（2026-08 分析）

## 3GPP 官网权威信息（2026-08 分析）

### 组织与架构
- **7 个组织合作伙伴**：ARIB（日）、ATIS（美）、CCSA（中）、ETSI（欧）、TSDSI（印）、TTA（韩）、TTC（日）
- **3 大 TSG**：RAN（无线接入网：WG1 物理层/WG2 协议层/WG3 接口/WG4 射频/WG5 终端一致性）、SA（业务与系统：WG1~6）、CT（核心网与终端：WG1/3/4/6）
- 工作方式：成员公司贡献驱动 → WG 会议 → 每季度 TSG 全会（SA# 编号会议）批准
- 成立 1998 年（3G 目标），范围已扩展至 LTE/5G/后续演进

### Release 时间线（最新状态，来源：官网 Releases 页）
| Release | 状态 | 功能冻结（Stage 3） | 结束（协议稳定） |
|---|---|---|---|
| Rel-21 | 新启动 | — | — |
| Rel-20 | Open | 2027-03（预计 SA#115） | 2027-06（预计 SA#116） |
| Rel-19 | Open（冻结中） | 2025-09（SA#109） | 2025-12-12（SA#110） |
| Rel-18 | Frozen | 2024-03（SA#103） | 2024-06（SA#104） |
| Rel-17 | Frozen | 2022-03-18（SA#95） | 2022-06-10（SA#96） |
| Rel-16 | Frozen | 2020-07-03（SA#88-e） | 2020-07-03 |
| Rel-15 | Frozen | 2019-03-22（SA#83） | 2019-06-07（SA#84） |

- 代际映射：Rel-99~7=3G（UMTS），Rel-8~14=4G（LTE），Rel-15~18=5G，Rel-19+=5G-Advanced 演进
- 冻结（Frozen）= 不能再加新功能（B/C 类 CR 禁止）；冻结后至少两年仍有修正 CR
- 并行 Release 制度：多个 Release 同时推进，保证连续稳定演进

### 版本号规则（x.y.z）
- 第一字段 x = Release 号（版本主号）；第二字段 y = 技术修改次数（每批 CR +1）；第三字段 z = 编辑修改次数（编辑部更正 +1）
- y 递增时 z 归零；x 递增时 y、z 归零
- 0.x.y/1.x.y/2.x.y = 未批准的新草案
- 每个版本变化记录在规范末尾的 change history 附录

### 存档文件名约定（FTP 目录内，官方规则）
- 格式：`<规范号去点>-<3位base36版本码>.zip`，内含 doc/dot 文件及附件
- 版本码映射：**1-9 用数字；10=a、11=b、12=c、13=d、14=e、15=f、16=g、17=h、18=i、19=j、20=k、21=l**（...33=x、34=y、35=z），后两位 = y z
- 例：21.900 v15.1.1 → `21900-f11.zip`；38.211 V16.4.0 → `38211-g40.zip`；极老规范 6 位扩展（24.229 v8.37.0 → `24229-083700.zip`）
- 多部分规范：51.010-1 v7.12.0 → `51010-1-7c0.zip`；29.998-06-2 v8.0.0 → `29998-06-2-800.zip`
- 超长规范拆多 Word 文件：`51010-1-d80_s00-s11.doc`、`..._sAnnexes_A.doc` 等分段后缀

### 存档 FTP 结构（https://www.3gpp.org/ftp/，2026-08 实测分析）

**⚠ 持续更新约定（详见 instructions.md「智能进化协议」：每次任务后归纳新经验并按五步流程固化到本 skill）**：后续每次访问 3GPP FTP/官网，若发现新的目录、系列、资料类型或代际划分变化，必须同步更新本 skill 的 FTP 结构分析（本节与系列映射表）。

**FTP 访问技巧（实测踩坑总结）**：
- **目录列表必须带浏览器 UA 头**：curl 无 UA 时返回空/403；用 PowerShell `Invoke-WebRequest -Headers @{"User-Agent"="Mozilla/5.0 ..."}` 或 curl `-A` 参数
- **找下载链接优先 DynaReport**：直接猜 archive 路径常 403（新规范目录名带点号）；先抓 `https://www.3gpp.org/dynareport/<规范号>.htm`，正则提取页面内 `href="([^"]*\.zip)"` 得全部版本真实链接
- **目录名带点规律**：新规范（22.870、38.914 等）目录带点（`archive/22_series/22.870/`）；老规范去点（`archive/38_series/38211/`）
- **latest 目录按 Release 分层**：`Specs/latest/Rel-XX/<系列>_series/`（Rel-10~Rel-20 实测存在）；archive 按系列平铺
- **提案文件名不含主题关键词**：6G 研究提案文件名为 `R1-xxxxxx.zip` 等编号（grep "6G" 命中为 0），需按会议目录+标题浏览；正式输出看 TR 而非提案
- **6G 文档获取完整流程（已验证）**：官网 release 页找 TR 编号（如 TR 22.870/38.914）→ DynaReport 提取 zip 链接 → 下载最新版+历史版 → soffice 转 PDF → python-docx 提取文本索引（`docx.Document(...).paragraphs`）

**FTP 根目录地图（实测 20 个顶级目录）**：
| 目录 | 内容 | 代际关联 |
|---|---|---|
| `Specs/` | 正式 TS/TR 规范：`latest/`（最新版）、`latest-drafts/`（最新草案）、`archive/`（历史全部版本）、按年代快照（1999-10 起） | 全部代际 |
| `tsg_ran/` | RAN 工作组提案与会议文档：`TSG_RAN`（全会）、`WG1_RL1`~`WG4_Radio`、`WG5_Test_ex-T1`、`WG6_legacyRAN`（3G 遗留）、`WGs_LongTermEvolution`（**早期 LTE 提案历史**）、`AHG1_ITU_Coord` | 3G/4G/5G |
| `tsg_sa/`、`tsg_ct/` | SA/CT 工作组（业务、核心网、终端）提案 | 全部 |
| `tsg_geran/` | GERAN 工作组（2G 无线） | 2G |
| `tsg_cn/`、`tsg_t/` | 旧 CN/终端工作组（历史） | 2G/3G |
| `Meetings_3GPP_SYNC/` | 全会同步文档（如 SA/Inbox/SP-260360.zip 提案） | 全部 |
| `PCG/`、`Op/`、`Joint_Meetings/` | 项目管理/运营商/联合会议 | 全部 |
| `Information/` | 信息资料（演示、协议文本等） | 全部 |
| `Email_Discussions/`、`Docs/`、`TdocListDefault/`、`Inbox/` | 讨论/文档/提案列表/临时 | 全部 |
| `webExtensions/`、`workshop/` | 网站扩展资料（如 3GPP Agreement PDF）、专题研讨会文档（2026-08 实测新增） | 全部 |
| `3guInternal/`、`MembersOnly/` | 内部/会员专区（需权限） | — |

**系列目录 → 代际映射（archive/ 实测 44 个系列目录）**：
| 系列 | 内容 | 代际 |
|---|---|---|
| 00~12 series | GSM 时代旧规范 | **2G** |
| 41~52、55 series | GSM/GERAN（需求、业务、无线、信令、测试、算法） | **2G** |
| 25 series | UTRAN 无线（WCDMA/TD-SCDMA/HSPA） | **3G** |
| 21/22/23/24/26~35 series | 需求/业务/架构/信令/编解码/安全等通用系列（跨代演进，按版本区分代际） | 2G/3G/**4G/5G 共用** |
| **36 series** | **LTE（E-UTRA）/LTE-Advanced/LTE-A Pro 无线电技术** | **4G 专属** |
| 37 series | 多 RAT 技术（MR-DC 等） | **4G/5G 共用** |
| **38 series** | **超越 LTE 的无线电技术（= 5G NR）** | **5G 专属** |

**按代际找资料（重点）**：
- **4G（LTE）**：`archive/36_series/` 全部（36.101/104/211/212/213/214/300/304/321/322/323/331 等）；核心网部分取 23/24/29/33 系列中 **Rel-8~Rel-14 版本**（文件名后缀 8xx~e.yy）；早期提案历史在 `tsg_ran/WGs_LongTermEvolution/`
- **5G（NR）**：`archive/38_series/` 全部（38.101/104/133/211/212/213/214/215/300/304/321/322/323/331/401/413 等）；37_series（MR-DC/EN-DC）；核心网部分取 23/24/29/33 系列中 **Rel-15 及以后版本**（后缀 f.yy 起）
- **6G**：暂无专属系列。当前研究产出：TR 22.870（22_series，Rel-20 版本）与 TR 38.914（38_series，Rel-20 版本）；Rel-21 规范工作启动后跟进新系列/新版本；会议提案看 `Meetings_3GPP_SYNC/` 与各 tsg 目录
- **3G（UMTS）**：25_series；**2G（GSM）**：41~52/55 与 00~12 series

**RAN 提案目录导航（NR 提案查找，实测确认）**：
| 子目录（tsg_ran/ 下） | 负责 | 提案编号 | 说明 |
|---|---|---|---|
| `WG1_RL1/` | 物理层 | `R1-xxxxxx` | **NR 提案主战场**（波形/信道结构/DCI/HARQ 等）；NR 提案自 TSGR1_86（2017）起 |
| `WG2_RL2/` | 无线协议层 | `R2-xxxxxx` | MAC/RLC/PDCP/RRC |
| `WG3_Iu/` | RAN 接口 | `R3-xxxxxx` | F1/Xn/NG 接口 |
| `WG4_Radio/` | 射频与性能 | `R4-xxxxxx` | RF 指标、RRM |
| `WG5_Test_ex-T1/` | 一致性测试 | `R5-xxxxxx` | UE 终端测试 |
| `TSG_RAN/` | RAN 全会 | `RP-xxxxxx` | 批准层（WI/SI 立项、规范升级） |
| `AHG1_ITU_Coord/` | ITU 协调 | — | 含 IMT-2030/6G 相关 |
| `WGs_LongTermEvolution/` | 早期 LTE 提案 | — | 4G 历史，非 NR |

- 结构规律：各 WG 目录下按会议组织（`TSGR1_99` = RAN1 第 99 次会议）；**传统会议目录止于约 2019–2023 年的会议**（WG1_RL1 止于 TSGR1_99（2019 年，Docs 内为 R1-19xxxxx 提案），TSG_SA 止于 TSGS_99_Rotterdam_2023-03，TSG_CT 止于 TSGC_99_Rotterdam_2023-03，TSG_RAN 止于 TSGR_99）
- **⚠ 最新会议文档（2024 年起）在 `Meetings_3GPP_SYNC/<组名>/`**：实测 2026-08 `Meetings_3GPP_SYNC/RAN1/Docs/` 有 1425 个 `R1-26xxxxx.zip`（2026 年提案）、`Meetings_3GPP_SYNC/SA/Inbox/` 有 SP-26xxxx 提案；子目录结构 `Docs/`（提案 zip）+ `Inbox/`（临时上传）+（全会另有 Agenda/Report/Tdoclist/LSin/LSout/Info_for_workplan/Joint_SA_RAN_CT/Templates/Invitation）
- 会议目录内部标准结构：`Agenda/`（议程）、`Docs/`（提案 zip）、`Inbox/`（临时上传）、`LS/`（联络函）、`Report/`（会议报告）、`Invitation/`（邀请函）
- 提案编号规则：前缀（R1/R2/…/RP/SP/CP）+ 年份后两位 + 序号，如 `R1-2605180.zip` = 2026 年 RAN1 提案；WG1_RL1 另有辅助目录 `DRAFT/`、`Templates/`、`Tdoc_index/`、`ConferenceCall/`、`3GPP_3GPP2_SCM/`；TSG_RAN 全会另有 `Work_Item_sheets/`（WI 表格）、`RAN_WI_summaries/`、`CR_implementation/`、`Early_TRs_TSs/`、`TEI_CR_guidance/`、`Tool_Automation_6G/`（6G 相关）、`ToR/`
- 各 WG 另有年度索引 zip（如 `R2_2015.zip`、`RP_2019.zip`、`RT_Index2026.zip`）
- SA/CT 全会提案在 `tsg_sa/TSG_SA/`（SP-xxxxxx，止于 2023-03）、`tsg_ct/TSG_CT/`（CP-xxxxxx，止于 2023-03）；**最新 SA/CT 全会提案见 `Meetings_3GPP_SYNC/SA/`、`Meetings_3GPP_SYNC/CT/`**
- 6G 无线研究（FS_6G_Radio）提案：最新在 `Meetings_3GPP_SYNC/RAN1/`；历史在 WG1_RL1 各会议目录；TSG_RAN 下另有 `Tool_Automation_6G/`
- **FTP 路径带点号规律**：新规范（如 22.870、38.914）在 archive 下的目录名**带点号**（`archive/22_series/22.870/`、`archive/38_series/38.914/`），老规范目录用去点名（`archive/38_series/38211/`）——403 时先经 DynaReport（`dynareport/<规范号>.htm`）拿真实下载链接
- **6G 核心文档本机存档**：`<项目目录>\temp\6G\`（TR 22.870 V2.0.0 正式版 + V1.1.0 历史版、TR 38.914 V0.3.0/0.4.0/0.4.1 草案 + 全会提案 RP-253750/RP-260073/RP-260870、全文文本索引 TR22.870-V2.0.0-文本索引.txt）

**TS vs TR 编号**：xx.9xx = 面向 SDO 转置的 TR；xx.8xx（及 xx.7xx）= 3GPP 内部可行性研究/计划 TR；30.xxx/50.xxx = 计划排期

### Stage 概念（官网定义）
- Stage 1 = 业务描述（用户视角）；Stage 2 = 逻辑架构与信息流（功能实体与参考点）；Stage 3 = 具体实现与协议（物理接口）；可行性研究 TR 视为 Stage 0；测试规范视为 Stage 4

---

