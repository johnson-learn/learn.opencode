---
name: 3gpp_skill
description: 3GPP 移动通信标准专家技能（全局 skill，仅显式触发，不靠关键词自动调用）。Use ONLY when 用户消息显式包含 "3gpp_skill：" 或 "3gpp_skill:"，或以 "3gpp_skill&"、"3gpp_skill " 与其他技能名并列后跟冒号——冒号后为用户任务。加载后执行任务：回答 3GPP 标准问题（5G NR / LTE / 4G / 6G / 3G / 2G）、协议讲解（PHY/MAC/RLC/PDCP/RRC/NAS 各层）、规范编号与访问（TS/TR/FTP 目录）、参数配置链讲解、端到端流程串联、通信领域文献综述等。铁律：一切以 3GPP 官网（www.3gpp.org）及 FTP 存档文档为准，其它资料仅可参考。普通消息仅提及 5G/LTE/NR 等关键词但无 "3gpp_skill：" 前缀时，不调用本技能。
---

# 3gpp_skill —— 3GPP 移动通信标准专家接口

## 🛠 工具依赖清单（移植到新机器时先逐项检查）

| 工具 | 用途 | 本机位置/版本 | 检查命令 | 缺失时安装 |
|---|---|---|---|---|
| Pix2Text (p2t) | 公式/符号图片识别（双轨提取必备） | `<Python脚本目录>\p2t.exe` | `p2t.exe predict -h` | `pip install pix2text -i 清华源` |
| LibreOffice soffice | 文档批量转 PDF（公式核实链路） | `<LibreOffice目录>\program\soffice.com` | 见 files_skill 检查命令 | winget LibreOffice |
| Python + PyMuPDF | 页面渲染 PNG、文本搜索 | `python` + `pymupdf` | `python -c "import pymupdf, docx"` | `pip install pymupdf python-docx -i 清华源` |
| matplotlib | 结构图/走势图 SVG 生成（配图主力之一） | `python -c "import matplotlib"`（3.11+） | 同上 | `pip install matplotlib -i 清华源` |
| Mermaid CLI (mmdc) | 流程图/时序图/状态图 → SVG（配图主力之一） | `<用户AppData目录>\npm\mmdc.cmd`（node v24 + 全局包） | `mmdc.cmd --version` | `npm.cmd install -g @mermaid-js/mermaid-cli`；渲染设 `$env:PUPPETEER_EXECUTABLE_PATH` 指向系统 Chrome；PowerShell 下用 `mmdc.cmd` 非 `mmdc`（ps1 被执行策略禁） |
| PS 提取脚本 | doc/docx 文本提取 | `<用户临时目录>\opencode\extract-docx.ps1` / `extract-doc.ps1` | `Test-Path <脚本>` | 从原机复制 Temp\opencode |
| 网络抓取 | FTP 目录/下载（需 UA 头） | PowerShell `Invoke-WebRequest` / `curl.exe -A` | `curl.exe --version` | Windows 自带 |
| 本机文档库 | 本地规范（仅用户明确要求时用） | `<用户桌面目录>\NR-f40\` | `Test-Path` | 从 3GPP FTP 重新下载（流程见官网权威信息章节） |
| 本机 6G 文档 | TR 22.870/38.914 存档 | `<项目目录>\temp\6G\` | `Test-Path` | 按「FTP 访问技巧」重下 |

**移植说明**：本技能核心链路 = 文本提取 + p2t 图片识别 + soffice 转 PDF + PyMuPDF 渲染，四件套缺一不可；网络抓取与本地文档库为可选项（缺时全部走官网实时获取）。

本技能是**唯一注册入口**，聚合了 13 个 3GPP/通信子技能（位于 `modules/`，资源库不独立注册），并内嵌 NR-f40 项目验证过的工作铁律。

## ⚠ 权威源声明（最高优先级）

**一切 3GPP 相关内容，其它资料（包括本技能子技能、书籍、第三方网站）只可参考，最终必须以 3GPP 官网（https://www.3gpp.org/）及其 FTP 存档（https://www.3gpp.org/ftp/）发布的正式文档为准。** 官网与其它来源冲突时，以官网为准；回答时优先引用官网文档原文并标注规范号/章节/版本。

## 版本范围规则（默认与例外）

- **默认（官网/FTP 分析）**：不限定任何单一版本（不限于 f40/V15.4.0）。回答时以**该规范最新版本为主**，同时覆盖涉及的各个历史版本；同一内容在不同版本有差异时，**各版本并列列出并标注版本号**（如 "V15.4.0 为 X，V16.4.0 起改为 Y"）
- **例外（本地资料分析）**：仅当用户**明确要求分析本地资料**（如"分析本机文档""按 NR-f40 文档"）时，才以指定本地资料中的 release 版本为准进行分析；此时仍应标注所依据的版本号，并提示与官网最新版本的差异
- 引用规范时一律写明版本号（如 38.211 V16.4.0），不得只说规范号

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

## 通用输出规则（全部任务遵守）

- **语言跟随提问**：用户以何种语言提问，思考、回答、输出就以何种语言（中文提问→中文回答，英文提问→英文回答）；协议原文、配置项名称、原始字段名、ASN.1、代码、命令等必要原文保持原样不翻译
- **含"输出"二字 → HTML 交付**：提问中出现"输出"二字时，最终答案必须以 HTML 文件输出（MathJax 渲染公式、规范排版），内容详细、不限字数篇幅；HTML 保存到提问时所在工作目录并浏览器打开（用户另行指定目录时按用户指定）
- **HTML 篇幅与大小零限制**：输出的 HTML 文件篇幅不做任何限制，文件大小不做任何限制，要求详细（宁可详细冗长，不可简化省略；文件太大可拆多文件）

## 处理流程

1. 确认问题类型（协议讲解 / 规范查询 / 文献综述 / 网络架构）
2. 路由到对应子技能（先读 `modules/<id>/GUIDE.md`），或直接按下方铁律作答
3. 涉及文件识别（doc/docx 提取、公式核实）时，与 files_skill 联动（`files_skill&3gpp_skill：...` 或本技能内直接引用其方法）

## 路由表（modules 下子技能）

| 任务 | 子技能 | 说明 |
|---|---|---|
| 3GPP 全世代专家（2G-6G、Rel-99~21、协议栈、架构、部署，触发词含 TS 23/24/25/36/38 全系列） | `lugasia-3gpp-skill-3gpp-skill-main`（首选入口） | skillsmp 来源，覆盖 GSM/UMTS/LTE/NR/6G/NTN/O-RAN |
| 3GPP 规范体系（TS/TR 编号、系列划分、FTP 目录结构、规范访问） | `ramihollings-mr.technology-3gpp-specifications` | 21-38 系列、TS vs TR、WG 归属 |
| 5G NR RLC 协议（TS 38.322 v19.1.0） | `kharlamenkodev-5g-nr-3gpp-skills-5g-nr-rlc` | TM/UM/AM 模式、PDU 格式、状态变量、ARQ、NTN/sidelink/MBS |
| 5G NR MAC 调度（TS 38.321 v19.1.0） | `kharlamenkodev-5g-nr-3gpp-skills-5g-nr-mac-scheduling` | 信道映射、DCI、HARQ、LCP、BSR/PHR/SR、RACH、NTN 适配 |
| 电信系统专家（OSS/BSS/NMS、计费、5G 网络管理、电信基础设施） | `personamanagmentlayer-pcl-telecommunications-expert` | skills.sh 来源，安全审计通过 |
| 电信工程师画像（RAN/回传/核心网、链路预算、传播建模、频谱合规） | `stanfish06-skillquarium-telecommunications-engineer` | skillsmp 来源 |
| 通信工程师画像（香农容量、OFDM/MIMO、LDPC/polar、TR 38.901、ns-3） | `stanfish06-skillquarium-communications-engineer` | skillsmp 来源 |
| 射频微波工程师画像（S 参数、噪声级联、VNA 验证、FCC/ETSI/3GPP 掩模） | `stanfish06-skillquarium-rf-microwave-engineer` | skillsmp 来源 |
| NTN 工程师（Rel-17/18 卫星、LEO/MEO/GEO/HAPS 链路、传播损伤） | `nobodyonlyc-skills-ntn-engineer` | skillsmp 来源 |
| 无线电 SDR（软件定义无线电、射频实验规则） | `zhaoxuya520-reverse-skill-radio-sdr` | 含 references/sdr-lab-rules.md |
| WiFi 无线（802.11 逆向与无线实验规则） | `zhaoxuya520-reverse-skill-wifi-wireless` | 含 references/wireless-lab-rules.md |
| 通信领域文献综述（Zotero/Obsidian/IEEE/ScienceDirect/ACM 检索） | `wanshuiyin-auto-claude-code-research-in-sleep-comm-lit-review` | 论文、综述、landscape 总结 |
| 现代网络架构（5G/SDN/NFV/边缘/QUIC/安全） | `dmitrijtitarenko-tech-rd-networking-telecom` | 吞吐/时延/可靠性/标准符合性评估 |

## 回答协议问题的铁律（NR-f40 验证，最高优先级）

1. **忠于原文**：标注规范号+章节（如 "38.213 §10.1"），先引用原文（英文原文+逐句中文翻译），再逐条解释+深入解析；原文公式必须列出并逐符号解析（配数值例题），不得用文字归纳代替
   - 字段名、等式、公式（含内嵌变量）必须原样列出再剖析
   - 自己推导的等式必须标注【解读/推导】并列出依据，不得冒充原文
2. **多文档关联**：回答前遍历本机全部相关 3GPP 文档，把各文档内容串成一条线（定义→配置→用法→流程→注意点），不遗漏要素
3. **版本差异明示**：同一数值在不同版本文档中不一致时，并列列出并标注各自版本，不得只取其一；官网分析默认覆盖各版本与最新版本（见「版本范围规则」）
4. **参数讲解**：出处（规范号+章节/表格号）+ 含义（原文语义翻译）+ 用法（怎么配/取值约束/注意点），用 `参数 | 出处 | 含义 | 用法/注意点` 四列表格
5. **RRC 配置链**：ASN.1 原文 + 变量完整结构，嵌套递归展开到叶子字段；从 MIB 源头开始遍历配置链，多条链分别列出
6. **流程串联**：功能讲解最后必须串起端到端全流程（SSB→MIB→SIB1→RACH→Msg4→专用配置→业务），不得各节孤立
7. **讲解风格**：老师视角（课堂引入→原理→原文→公式→例题→注意点→小结），小白能懂；中文讲解，关键英文术语保留
   - <b>每个知识点"先详细解析、最后才提炼"（用户两次点名"过于简单"）</b>：任何点（不限于公式——基图选择、资源映射、功率控制……）一律按顺序写：原文引用 → 逐句翻译 → 逐项/逐符号解析 → 公式 → 数值例题 → 注意点 → <b>末尾才给提炼总结</b>；提炼表放章节最后；禁止"一句话提炼"带过（LDPC 基图选择曾被一句话带过的教训）
8. **主线串联结构（专题级，NR-f40 实战归纳）**：多讲次专题必须有一条贯穿主线，禁止各讲孤立堆料（用户实测反馈"没逻辑、没串起来"）：
   - 主线 = 功能的生命周期问题链（如 CSI：为什么需要 → 用什么测 → 怎么配 → 报什么 → 怎么算 → 怎么交付 → 时限多少 → 全流程回顾）
   - 每讲只回答主线一个问题；每讲开头用"设问（承接第 X 讲）"、结尾用"小结（把球交给下一讲）"显式桥接（可用 CSS .bridge 块）
   - 最后一讲做"九步全程回顾（每步标注对应讲次）"+ 主线收口一句话
   - <b>主线不能脱离目的——必须落实到"基站-UE 如何使用"（双视角落地，NR-f40 实战打磨）</b>：
     - 每个专题第 1 讲必须给"四问定位"表：含义（是什么）/ 作用（承载什么）/ 目的（为什么存在）/ 应用场景（eMBB/URLLC/mMTC/广播接入等 + 场景决定参数）
     - 机制讲次之后必须有"双视角落地讲次"：① 双端流程对照表（基站 N 步 ↔ UE N 步逐步对应）；② <b>参数双端使用总表</b>（每参数四列：配置方→配置给谁 | 基站如何使用 | UE 如何使用）；③ 基站内部决策（调度器/MCS 外环/预编码选择/波束选择/功率分配——规范不规定但原理必须讲，标注【解读/推导】）；④ 核心网参与的参数（QoS/5QI/GBR → 调度权重）
   - 拆多文件时保留主线：导航页给学习地图（讲次递进关系）+ 每文件顶部导航条
   - **旧文件/机械拼接文件的改造法**（BWP/PDCCH 整合教训：只物理拼接 ≠ 串起来）：机械拼接后必须补"主线三件套"——① 文首主线导览块（问题链总览，.mainline 橙色框）；② 每讲 h2 前"承接"桥接块（点明承接第 X 讲 + 本讲回答主线哪个问题）；③ 练习册/总结前"主线收口"块（一句话全貌、各步指向讲次）
   - 改造插入技巧：桥接块要插在"每讲第一个 h2 前"；但"1. 课堂引入"这类标题在多讲重复，<b>不能用重复标题做锚点</b>——用每讲第二个 h2（主题标题，唯一）定位，再向前找最近的 `<h2>` 插入
9. **专题收尾自查（交付前必做）**：
   - 遍历该专题涉及的<b>全部相关规范</b>，维护"讲次 ↔ 规范章节贡献矩阵"（如 CSI：38.211/38.212/38.213/38.214/38.215/38.321/38.331 各章贡献），逐条核对是否覆盖，防止"某规范整块遗漏"（38.213/38.215 曾被遗漏的教训）
   - 任务清单标记 completed 前必须确认每项有<b>实质内容落地</b>，禁止"机制相同/同构扩展"带过——带过 = 未完成；用户会抽查
   - 原文公式核实后必须展开讲解 + 配数值例题，不得只列公式
   - <b>正文表述禁止"与 XX 同构/完全相同/同源"式带过</b>（用户两次点名）：两个专题内容相似时（如 PDSCH↔PUSCH），后续专题必须把被引用专题的公式/表格/流程<b>原样展开重列</b>（如 PUSCH 讲 SLIV/RIV/MCS/TBS 时把公式全文再列一遍），差异点显式标注；表格中"同"列改为逐行写具体内容
10. **配图数量原则（越多越好，不做数量限制）**：配图可直观呈现抽象关系，凡能配图处尽量配图——除五类必画图外，公式分解图（功率公式各项贡献条形图）、对比图（双方案/双表对比）、走势图（谱效阶梯）、流程四步图等均鼓励配图；单专题 6~10 张为常态，不设上限

## 配置链梳理输出模板（NR-f40 实战打磨，后续 3GPP 参数配置梳理一律照此输出）

**梳理目的（先向学生言明）**：① 目的一——知道"怎么配置的"：该功能所有参数分别在哪条链、哪一级、由哪个字段配置；② 目的二——知道"为什么这么配置"：每个参数的目的、场景、功能、配置要求（Cond 条件/取值约束）、特殊说明。

### 章节标准结构（第 2 节"配置链"）

**2.1 链 A：广播链（服务于初始接入）**
1. 标题下紧跟<b>链条概览</b>（box 样式）：用 `→` 箭头串起每一级，格式 `消息 → 类型（字段名）→ 类型（字段名）→ … → 终点参数`；有分支时每条分支单独一行概览（如"上行：…"、"分支① HO：…"）
2. <b>ASN.1 溯源块</b>（chain 样式）：从源头开始逐级列出 38.331 原文 ASN.1 截取——
   - 每一级用 `<span class="lv">第N级</span>` 标注
   - 级标题句式："【类型】由上一级【父类型】的【字段名】字段配置"
   - 相关字段完整列出（变量名红色 `<span class="rv">`、类型蓝色 `<span class="rt">`、结构体名紫色 `<span class="asn">`、行尾绿色注释 `<span class="rc">` 说明与目标功能的关系）；无关字段一律灰色 `...`
   - 其他功能的 IE 只列"变量名 : 类型"一行并标"XX 功能，不展开"——禁止本末倒置展开无关内容
3. 链尾<b>溯源结论</b>：一句话读法（PBCH→MIB（字段）→SIB1（字段）→…→参数），学生照着念即会

**2.2 链 B：专用链（服务于业务运行）**：同 2.1 结构；注意容器归属必须准确（例：PCell 配置在 RRCReconfiguration 的 nonCriticalExtension→masterCellGroup，而非 secondaryCellGroup——后者是 EN-DC 时 NR 作 SCG 用）；HO/SCell 等场景分支在概览与结论中分别点明

**2.3 链 C（兜底/隐式链）**：简式（原文引用 + 一句结论）

**2.4 三链对比表**：`链 | 作用 | 应用场景 | 关键特征` 四列

**2.5 相同变量在不同链中的对比（重点模板）**
1. 开头<b>总原则</b> box：一句话讲透"为什么同一类型出现在多条链"（两阶段/两种送达手段）
2. 按类型分块（每块一个 chain div）：标题格式 `① 类型名（说明）——出现在 N 处`
   - 每处用 `【处N】链X：父结构.字段名（类型、必选性/条件）` 开头
   - 每处必须完整展开三行三要素，禁止"见某处"引用代替内容；标注"同某处"可以，但后续仍须完整列出内容：
     - `场景：`（何时何地谁在用：阶段、事件、信道/流程，2~4 句）
     - `目的：`（为什么在这里配：设计意图、约束来源与后果、必选/OPTIONAL 的原因，2~4 句）
     - `用途：`（拿它做什么：具体行为、关联流程与规范出处、长期角色，2~4 句）
   - 同名不同型的字段必须点明区别（如 initialDownlinkBWP 三现：Common=公共半块、Dedicated=专用半块）并给判断技巧
3. 末尾<b>全变量分布地图</b>表：`变量 | 链A位置 | 链B位置 | 必选性`，附读图结论（哪条链配底线、哪条链配其余）

### HTML 实现（CSS 类名固定）
```
.rv { color:#c00000; font-weight:bold; }   /* 变量名（相关字段）红色加粗 */
.rt { color:#005a9c; font-weight:bold; }   /* 类型蓝色加粗 */
.asn { color:#6b3fa0; font-weight:bold; }  /* 结构体名紫色 */
.rc { color:#4a7020; }                     /* 行尾绿色注释 */
.dot { color:#999; }                       /* 无关字段省略号灰色 */
.lv { color:#c55a11; font-weight:bold; }   /* 第N级标注橙色 */
.chain { 黄底边框块 } .box { 蓝底边框块 }   /* 概览/总原则容器 */
```
ASN.1 一律放 `<pre>` 内用 span 着色；禁止自创伪 ASN.1 结构，全部贴 38.331 原文。

### ASN.1 着色自查与规则化着色（交付前必查）
- **自查**：扫描全部 `<pre>` 块——含 `::=`/`SEQUENCE {`/`ENUMERATED {` 特征但无 `class="rv"` 的即为遗漏块，必须补着色（历史文件曾整专题 10 块无着色未察觉）
- **规则化自动着色**（正则，按序执行）：① 行尾 `-- 注释` → `.rc`；② `Name ::=` 结构名 → `.asn`；③ 行首缩进的 `字段名 类型`（字段名小写开头、类型大写开头或关键词）→ `.rv`+`.rt`；④ 独立 `...` 行 → `.dot`
- **坑**：多词类型（`BIT STRING`、`OCTET STRING`）必须放在类型交替的**前面**，否则 `[A-Z][A-Za-z0-9-]*` 先匹配 `BIT` 把类型拆成两半；着色后必须复查 `"BIT</span> STRING` 类拆分残留
- 自动着色后抽查 1~2 块确认无误伤（枚举值行、嵌套字段行）

### 配置总结章节模板（配置链之后的独立章节，NR-f40 实战打磨）

在配置链章节之后新增"配置总结"章节，采用"一页看清"格式（每条链四个子节 + 三个全局小节）：
1. **链条总览表**：`链条 | 信令载体 | 核心IE | 配置内容 | 应用场景`——按 UE 接入阶段递进划分链条（如 PDCCH：MIB 隐式链 / SIB1 广播公共链 / 专用公共链（切换·辅小区）/ 专用专属链；划分粒度可多于溯源节的链数，需说明对应关系）
2. **每条链四个子节**：
   - 配置层级结构：pre 树形图（`└──`/`├──`），从信令载体一路画到叶子字段，行尾 `←` 注释字段含义/约束
   - 各字段详解表：`字段 | 类型 | 作用 | 约束条件`（约束列写 Cond 条件/ID 规则/配额/缺省语义，逐条按 38.331 原文）
   - 应用场景与作用表：`场景/UE状态 | 作用`（如 RRC_IDLE/INACTIVE/初始接入/CONNECTED 或 PCell切换/PSCell添加/SCell添加）
   - 关键特征：编号要点列表 3~5 条（小区级/缺省语义/配额/设计目的）
3. **三个全局小节**：
   - 参数合并规则：合并公式（如"初始 BWP 完整配置 = Common（链1/2）+ Dedicated（链3）"）+ 参数类别来源表 + 优先级规则编号列表（互补/替代/同义/复用，逐条按原文）
   - 场景使用矩阵表：`场景 | 使用的链条 | 说明`（覆盖开机→接入→连接→切换→SCell→BWP切换→省电全部场景）
   - 易混淆点澄清表：`误区 | 纠正`（同名不同型、字段出现位置 vs 确定路径、ID 保留规则、类型归属等 5~6 组）

### 参考外部总结文档的处理方法
- 用户提供他人总结的 docx（如"XX配置链条全梳理.docx"）时：提取文本（文件被占用先 Copy 再解压提取）→ 吸收其<b>格式优点</b>（层级树、字段详解表、易混淆点等）补进输出 → 但<b>内容一律以 38.331 原文核对为准，不照搬参考文档的错误</b>（如参考文档写"controlResourceSetZero 在 SIB1 中下发"，原文 Cond InitialBWP-Only 明确 "absent when sent in system information"，必须按原文纠正）

### 质量要求
- **详细化优先**：框架被认可后，按用户要求持续详细化——每个出现位置的场景/目的/用途从一句话展开为完整段落（含规范出处、约束原因、长期角色）；HTML 篇幅与文件大小零限制
- **禁止引用代替内容**：不得出现"见某处X"；对称处标注"同某处"后仍完整列出三要素
- **两个维度必须分清并讲明（易错点）**：① "某资源/参数"的<b>确定路径（配置来源）</b>——可能有多条（如 CORESET#0 由 MIB 查表 + 专用信令 controlResourceSetZero 字段两处确定）；② "某个字段"的<b>出现位置</b>——字段本身只出现在一处（如 controlResourceSetZero 字段只在专用信令的初始 BWP）。两者不得混为一谈，正文结论必须与分布地图表<b>前后一致</b>（不一致 = 错误）
- **先核对原文再写 Cond 条件与出现位置**：所有 OPTIONAL/必选/Cond 条件、字段出现位置必须以 38.331 原文为准（grep 核对原文后再落笔），禁止凭记忆写
- **交付前校验**：公式零伪排版（无 ⌈⌉/N_RB^/log2(）、headless 无 JS 错误、SVG 无重叠、浏览器打开

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

## HTML 大文件操作安全守则（通用工程经验，NR-f40 连环事故教训）

适用于对已有大型 HTML 的批量修改/插图/去重，任何专题通用：

1. **禁止非贪婪跨块正则定位删除/替换**：`<figure[\s\S]*?<b>图 N</b>[\s\S]*?</figure>` 这类写法会从文档第一处 `<figure>` 一直匹配到第一个"图 N"，吞掉中间全部正文（两次事故：吞 1.3~2.8 节、吞图 1~图 8）。正确做法：
   - 定位单个段落：先 `find('<b>图 N</b>')` 拿位置，再向前找最近的 `<figure`、向后找最近的 `</figure>` 取精确边界
   - 批量增删图：**"全清 + 按唯一锚点重插"**——`subn(r'<figure[\s\S]*?</figure>', '', h)` 清空（每个 figure 独立匹配是安全的），再按唯一锚点 `insert` 九图
2. **批量字符串替换必须范围限定与排序**：`A→B、B→C` 替换链会污染 SVG 段/标题，且先替换产物可能被后续规则误伤（"链 C"→"链条4"→反向修复错乱的教训）。正确做法：替换前切分保护段（`re.split(r'(<svg[\s\S]*?</svg>)')` 只替换偶数段）；替换规则长词先、带上下文先；替换后全文残留扫描（比喻词/裸变量/伪公式清单计数=0）
3. **脚本异常不得半写回**：PowerShell 中 Substring 异常后 `$seg` 变 null，`prefix + $null + suffix` 拼接吞掉中间整段并写回——写回必须放在所有可能异常的操作之后，或用 Python 写脚本（异常即不写）。每次写回后立即校验：h2/h3 序列完整、关键锚点存在、段落份数=1（防重复插入累积）、标签配对、大小无骤降（骤降=吞段）
4. **改动前备份/素材留痕**：大文件操作前 copy 到 `.bak`；分片内容写独立片段文件（如 si-r1~r4.html）再合并，事故后可单片恢复，避免"全文从会话记录重打"
5. **插入锚点必须唯一且实际存在**：用 `find` 验证（返回 -1 即报错停手，不继续）；锚点文本含引号时注意中英文引号差异（`"两层结构` 用中文引号 vs ASCII 引号导致 find 失败，脚本继续执行后静默缺图）；<b>锚点必须用完整标签/完整标题文本，禁止部分匹配</b>（锚点 '&lt;h2&gt;8. 第 8 讲' 部分匹配导致 after 插入点落在 h2 标题文字中间、图插进标题内部的事故）；after 插入前确认锚点是完整闭合标签（如 `</h2>`）
6. **片段写作与拼装约定**：分片写 HTML 时，插图与正文分离——图只在最终拼装阶段按锚点插入合并文件；拆分重组时记住片段不含图，须从合并文件按 h2 边界切分（保证图随段走）
7. **写片段时的闭合标签校对**：orig 原文块、翻译段、讲解块各自的闭合标签（`</div>`/`</p>`）最易写混（"翻译段以 </div> 收尾"笔误发生两次），拼装后必须跑标签配对检测兜底
8. **残留扫描的误报排除**：伪公式/裸变量扫描必须排除 `<script>` 段与 `<svg>` 段——计算器 JS 的 `Math.log2` 是合法代码、Mermaid/matplotlib 图内文字的 Unicode 数学符号（⌊⌋⌈⌉ 等）是图内合法写法（图内禁 foreignObject 嵌 MathJax，Unicode 符号/tspan 上下标是规范做法）；凡误报必须核实（排除后归零才算通过），不得对误报视而不见

## 文档提取双轨要求（文字 + 图片识别，必须同步执行）

- **3GPP 文档中公式、符号、记号大量为图片式（OLE 对象/截图）**：纯文本提取必然不完整，任何资料读取任务**必须同步用图片识别工具（p2t）核实**，不得只用文本提取结果
- 双轨流程：
  1. 文本轨：docx/doc 提取文本（extract-docx.ps1 / extract-doc.ps1 或 python-docx）→ 得正文框架
  2. 图片轨：**同步** soffice 转 PDF → PyMuPDF 定位并渲染页面/公式区域 PNG（`get_pixmap(dpi=300)`）→ `& "<Python脚本目录>\p2t.exe" predict --file-type formula/page` 识别公式、符号、记号 → 与文本轨合并核对
  3. 两轨结果有差异时以图片识别结果为准（图片是原文原貌）
- 公式识别后与规范知识核对（交叉验证，多模式跑 p2t），已核实的标注【公式已核实】；未核实的标注【待核实】，不得无标注使用
- 输出公式一律 MathJax/LaTeX 标准排版（禁止 ⌈⌉、N_RB^、log2( 等纯文本伪公式）

## 本机资源（仅当用户明确要求分析本地资料时启用）

> 默认分析走官网/FTP（覆盖各版本与最新版本）；本目录文档多为 V15.4.0（f40）版本，**非默认依据**。

- **3GPP 文档库**：`<用户桌面目录>\NR-f40\`（PHY 38.104/133/201/202/211/212/213/214/215；L2/L3 38.300/304/321/322/323/331/37.324；接口/架构 38.401/410/413/415/425/473；系统/核心网 21.900/23.501/502/24.501/29.274/281/295.002/295.018/33.501/29.060/38.533）
- **纯文本索引**：`<用户临时目录>\opencode\specs\*.txt`（全文搜索用；公式字符缺失需 p2t 核实）
- **3GPP 权威下载**：官网 FTP `https://www.3gpp.org/ftp/Specs/archive/`（38 系列=5G NR，36 系列=4G LTE，23 系列=核心网；完整目录地图与代际划分见「官网权威信息 → 存档 FTP 结构」章节；直链模板 `https://www.3gpp.org/ftp/Specs/archive/38_series/38211/38211-h40.zip`）
- **官网权威查询入口**：DynaReport（`https://www.3gpp.org/dynareport/<规范号>.htm`，最新版本信息）与 3GU Portal（portal.3gpp.org，含各 Release 规格清单）
- **docx/doc 提取脚本**：`extract-docx.ps1` / `extract-doc.ps1`（Temp\opencode）

## 环境注意

- 中文输出优先；文件编码 UTF-8
- 与 files_skill 分工：文件/图片/公式的识别与格式转换走 files_skill；协议内容讲解与规范查询走本技能
- 需要新规范文档时优先 3GPP FTP 下载（doc 格式，用 soffice 转 docx 后处理）
