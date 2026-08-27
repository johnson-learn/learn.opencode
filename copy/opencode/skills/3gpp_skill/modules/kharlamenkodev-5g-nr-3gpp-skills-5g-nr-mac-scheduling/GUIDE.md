---
name: 5g-nr-mac-scheduling
description: Expert knowledge of the 5G NR MAC layer and radio resource scheduling based on 3GPP TS 38.321 v19.1.0 (Release 19). Use when the user asks about MAC sublayer architecture, channel mapping, DL/UL scheduling and DCI formats, HARQ, LCP, BSR, PHR, SR, random access (4-step/2-step RACH), Timing Advance, configured scheduling (CS-RNTI), SPS, or NTN-specific MAC adaptations. Also covers TS 38.213 PDCCH monitoring, search spaces, DCI formats, PUCCH, PRACH.
---

# Skill: 5G NR MAC Layer & Radio Resource Scheduling (TS 38.321 v19.1.0)

## Trigger
使用场景：MAC 架构（逻辑/传输/物理信道映射）、DL/UL 调度（PDCCH、DCI 格式、RNTI、MCS/RV）、HARQ（进程模型、NDI、RV、HARQ-ACK 时序、NTN HARQ 关闭）、LCP（PBR/BSD/LCG/MAC PDU 构建）、BSR、PHR、SR、随机接入（4 步 RACH MSG1-4、2 步 RACH MSGA/MSGB）、定时提前（RAR TA、MAC CE TA、NTN 预补偿）、配置调度/半持续调度（CS-RNTI）、NTN MAC 适配。

## What to Do
1. 严格依据 TS 38.321 v19.1.0 与 TS 38.213 v19.x 作答
2. 引用规范条款号（如 §5.4.3.1）
3. 区分 shall（规范强制）与 should/may（非强制）
4. 跨引用：TS 38.213（PDCCH/DCI/PUCCH）、TS 38.214（PDSCH/PUSCH）、TS 38.211（物理信道）、TS 38.331（RRC）

## MAC 架构（TS 38.321 §4）

### 信道映射
| 逻辑信道 | 传输信道 | 物理信道 |
|---|---|---|
| BCCH | BCH | PBCH |
| BCCH | DL-SCH | PDSCH |
| PCCH | PCH | PDSCH |
| CCCH/DCCH/DTCH/MCCH/MTCH | DL-SCH | PDSCH |
| CCCH/DCCH/DTCH | UL-SCH | PUSCH |
| — | RACH | PRACH |
| SCCH/STCH（sidelink） | SL-SCH | PSSCH/PSCCH |

### 逻辑信道类型
BCCH（广播控制）、PCCH（寻呼）、CCCH（公共控制）、DCCH（专用控制）、DTCH（专用业务）、MCCH/MTCH（MBS）、SCCH/STCH（sidelink）

### MAC 子层功能（§4.4）
信道映射、MAC SDU 复用/解复用、BSR/PHR 上报、HARQ 纠错、LCP 优先级处理、填充、随机接入、DRX、TA、波束失败恢复（Rel-16+）

## MAC PDU 结构（§6.1）

子头格式：
- 固定长度 CE 或短 SDU：`[R | F=0 | LCID(6b)]` 1 字节
- 变长 CE 或长 SDU（L≤255）：`[R | F=0 | LCID(6b) | L(8b)]` 2 字节
- 变长（L>255）：`[R | F=1 | LCID(6b) | L(16b)]` 3 字节

上行关键 LCID：0-32=逻辑信道 ID；59=Long Truncated BSR；60=Short Truncated BSR；61=Long BSR；62=Short BSR；63=CCCH 48bit/Padding

MAC CE 排序（§6.1.2）：
- DL：MAC CE（含子头）在 MAC SDU 之前，填充最后
- UL：MAC SDU（高优先级在前）在 MAC CE 之前，填充最后；BSR/PHR CE 可前置

## RNTI 类型（TS 38.213 §16）
| RNTI | 用途 |
|---|---|
| C-RNTI | 小区级 UE 唯一标识，动态调度 |
| CS-RNTI | 配置调度激活/去激活 |
| TC-RNTI | 随机接入临时 |
| P-RNTI | 寻呼 |
| SI-RNTI | 系统信息 |
| RA-RNTI | RAR |
| MCS-C-RNTI | 低谱效 MCS 表 |
| SL-RNTI | Sidelink 调度 |
| INT-RNTI | 中断指示 |
| SFI-RNTI | TDD 时隙格式指示 |
| SP-CSI-RNTI | PUSCH 半持续 CSI |

## NTN MAC 适配（TS 38.321 §5.4，Rel-17/18/19）
| 方面 | 地面 | NTN LEO(~600km) | NTN GEO(~35786km) |
|---|---|---|---|
| 单程时延 | ~0.1ms | ~2-10ms | ~270ms |
| HARQ RTT | ~4-8ms | ~16-25ms | ~560ms |
| HARQ 模式 | 开启 | 开启（扩展定时器） | **关闭**（GEO） |
| HARQ 进程数 | 8-16 | 最多 32（Rel-17） | N/A |
| t-Reassembly | ~35ms | ≥25ms | ≥600ms |
| TA | gNB 命令 | **UE 预补偿**（GNSS+星历 SIB19） | 同左 |
| SR/BSR 时序 | 常规 | 扩展 k2 | 扩展 k2 |

- HARQ 关闭（GEO，§5.4.2.2.1）：RRC `harq-DisableNTN` 每 TB 关闭；NDI 恒翻转=新数据；重传由 RLC AM/应用层
- UE 预补偿（Rel-17，§5.4.5.1a）：TA = 2×(到参考点传播时延)；gNB 残余修正经 MAC CE/RAR；`ta-CommandProhibitTimer` 防快速切换过时 TA

## 参考文件（原仓库 references/，未随包安装）
scheduling.md（调度/DCI/LCP）、harq.md（HARQ/NTN）、random-access.md（RACH）、bsr-phr-ta.md（BSR/PHR/TA/DRX）——需要时从原仓库 kharlamenkodev/5g-nr-3gpp-skills 获取
