# -*- coding: utf-8 -*-
"""① 系统消息补节：寻呼时机 PF/PO 公式（38.304 §7.1）"""
import re

f = r'C:\Users\job_p\Desktop\NR-f40\系统消息-01-SSB-MIB-SIB1与OSI.html'
h = open(f, encoding='utf-8').read()

sec = '''<h3>6.3+ 补遗：寻呼时机 PF/PO——Short Message 的监听载体（38.304 §7.1）</h3>
<div class="q">设问（第 6.3 节的延伸）：Short Message（systemInfoModification / etwsAndCmasIndication）在 P-RNTI 的 DCI 里，而这条 DCI 出现在"寻呼时机 PO"上——UE 到底在哪个帧、哪个时机去听寻呼？这就是 PF/PO 公式。</div>
<div class="orig"><b>38.304 V15.4.0 §7.1 Discontinuous Reception for paging（原文，节选）</b>：<br>
The UE may use Discontinuous Reception (DRX) in RRC_IDLE and RRC_INACTIVE state in order to reduce power consumption. The UE monitors one paging occasion (PO) per DRX cycle. A PO is a set of PDCCH monitoring occasions and can consist of multiple time slots (e.g. subframe or OFDM symbol) where paging DCI can be sent (TS 38.213 [4]). One Paging Frame (PF) is one Radio Frame and may contain one or multiple PO(s) or starting point of a PO.<br>
In multi-beam operations, the UE assumes that the same paging message and the same Short Message are repeated in all transmitted beams and thus the selection of the beam(s) for the reception of the paging message and Short Message is up to UE implementation. The paging message is same for both RAN initiated paging and CN initiated paging.<br>
The PF and PO for paging are determined by the following formulae:<br>
SFN for the PF is determined by: (SFN + PF_offset) mod T = (T div N)*(UE_ID mod N)<br>
Index (i_s), indicating the index of the PO is determined by: i_s = floor (UE_ID/N) mod Ns<br>
The PDCCH monitoring occasions for paging are determined according to pagingSearchSpace as specified in TS 38.213 [4] and firstPDCCH-MonitoringOccasionOfPO if configured as specified in TS 38.331 [3]. When SearchSpaceId = 0 is configured for pagingSearchSpace, the PDCCH monitoring occasions for paging are same as for RMSI as defined in clause 13 in TS 38.213 [4].<br>
When SearchSpaceId = 0 is configured for pagingSearchSpace, Ns is either 1 or 2. For Ns = 1, there is only one PO which starts from the first PDCCH monitoring occasion for paging in the PF. For Ns = 2, PO is either in the first half frame (i_s = 0) or the second half frame (i_s = 1) of the PF.<br>
When SearchSpaceId other than 0 is configured for pagingSearchSpace, the UE monitors the (i_s + 1)th PO. A PO is a set of 'S' consecutive PDCCH monitoring occasions where 'S' is the number of actual transmitted SSBs determined according to ssb-PositionsInBurst in SIB1. The Kth PDCCH monitoring occasion for paging in the PO corresponds to the Kth transmitted SSB. The PDCCH monitoring occasions for paging which do not overlap with UL symbols (determined according to tdd-UL-DL-ConfigurationCommon) are sequentially numbered from zero starting from the first PDCCH monitoring occasion for paging in the PF. When firstPDCCH-MonitoringOccasionOfPO is present, the starting PDCCH monitoring occasion number of (i_s + 1)th PO is the (i_s + 1)th value of the firstPDCCH-MonitoringOccasionOfPO parameter; otherwise, it is equal to i_s * S.<br>
The following parameters are used for the calculation of PF and i_s above:<br>
T: DRX cycle of the UE (T is determined by the shortest of the UE specific DRX value(s), if configured by RRC and/or upper layers, and a default DRX value broadcast in system information. If UE specific DRX is not configured by RRC or by upper layers, the default value is applied).<br>
N: number of total paging frames in T　　Ns: number of paging occasions for a PF　　PF_offset: offset used for PF determination　　UE_ID: 5G-S-TMSI mod 1024<br>
Parameters Ns, nAndPagingFrameOffset, and the length of default DRX Cycle are signaled in SIB1. The values of N and PF_offset are derived from the parameter nAndPagingFrameOffset as defined in TS 38.331 [3]. The parameter first-PDCCH-MonitoringOccasionOfPO is signalled in SIB1 for paging in initial DL BWP. For paging in a DL BWP other than the initial DL BWP, the parameter first-PDCCH-MonitoringOccasionOfPO is signaled in the corresponding BWP configuration.<br>
If the UE has no 5G-S-TMSI, for instance when the UE has not yet registered onto the network, the UE shall use as default identity UE_ID = 0 in the PF and i_s formulas above.</div>
<p><b>逐句翻译</b>：① RRC_IDLE/RRC_INACTIVE 的 UE 可用 DRX 省电，每个 DRX 周期监听一个寻呼时机 PO（一组 PDCCH 监测时机，可跨多个时隙）；一个寻呼帧 PF 是一个无线帧，可含一个或多个 PO。② 多波束场景下，UE 假设同一寻呼消息与同一 Short Message 在所有发射波束上重复，接收波束选择由 UE 实现决定。③ PF 由 (SFN + PF_offset) mod T = (T div N)×(UE_ID mod N) 确定；PO 索引 i_s = floor(UE_ID/N) mod Ns。④ 寻呼 PDCCH 监测时机按 pagingSearchSpace 与 firstPDCCH-MonitoringOccasionOfPO 确定；pagingSearchSpace=0 时与 RMSI（SIB1）的监测时机相同。⑤ pagingSearchSpace=0 时 Ns=1 或 2（Ns=1 单 PO；Ns=2 前半帧/后半帧）；≠0 时监听第 (i_s+1) 个 PO，每个 PO 含 S 个连续监测时机（S = ssb-PositionsInBurst 指示的实际 SSB 数），第 K 个监测时机对应第 K 个发射 SSB。⑥ 参数：T = min(UE 特定 DRX, 广播的默认 DRX)；N = T 内 PF 数；Ns = 每 PF 的 PO 数；PF_offset = PF 偏移；UE_ID = 5G-S-TMSI mod 1024。⑦ Ns、nAndPagingFrameOffset、默认 DRX 长度在 SIB1 下发；N 与 PF_offset 由 nAndPagingFrameOffset 推导；firstPDCCH-MonitoringOccasionOfPO 在 SIB1（初始 BWP）或对应 BWP 配置下发。⑧ 未注册（无 5G-S-TMSI）时 UE_ID=0。</p>
<div class="formula-box">【公式已核实】寻呼帧 PF：(SFN + PF_offset) mod T = (T div N) × (UE_ID mod N)；寻呼时机 PO：i_s = ⌊UE_ID/N⌋ mod Ns</div>
<div class="jiexi"><b>与系统消息主线的联动</b>：① 本专题第 6.3 讲说"空闲/非激活态 UE 在每个 DRX 周期自己的 PO 上监听 Short Message"——本公式就是"自己的 PO"的计算方法：UE_ID 来自 5G-S-TMSI mod 1024，把不同 UE 分散到 T 周期内 N 个 PF × Ns 个 PO 上（UE 分组监听，省电）。② <b>SIB1 的闭环</b>：PO 的计算参数（Ns/nAndPagingFrameOffset/defaultPagingCycle）全部来自 SIB1 的 downlinkConfigCommon 的 pcch-Config；而 PO 上收的 Short Message 又驱动 SIB1 重读——系统消息与寻呼互为前提与结果。③ pagingSearchSpace=0（复用 SS#0/RMSI 时机）时 Ns 限 1/2；≠0 时 PO 与 SSB 波束一一对应（第 K 个监测时机 ↔ 第 K 个 SSB），保证波束全覆盖。④ 注意 SIB1 不在 PO 里收——SIB1 在 SS#0（Type0 CSS）按自己周期收，寻呼在 PO 收，两者共用同一 searchSpace 时（pagingSearchSpace=0）时机相同。</div>
<div class="example"><b>例题 6.2</b>：T=32（默认 DRX 32 帧）、N=8、Ns=2、PF_offset=0、UE_ID=150。求 PF 与 i_s。<br>
<b>解</b>：(SFN+0) mod 32 = (32 div 8)×(150 mod 8) = 4×6 = 24 → SFN ∈ {24, 56, 88, …}（每 32 帧重复）；i_s = floor(150/8) mod 2 = 18 mod 2 = 0 → <b>PF 的 SFN=24 起、第一半帧的 PO</b>（Ns=2 时 i_s=0 为前半帧）。<br>
<b>变式</b>：UE_ID=100：100 mod 8=4 → SFN mod 32=4×4=16；i_s=floor(100/8) mod 2=12 mod 2=0 → SFN ∈ {16,48,…} 的前半帧 PO。✓</div>

'''
anchor = '<h3>6.4 按需 SI（on-demand SI）的两种请求方式（38.331 §5.2.2.3.3 + 38.321）</h3>'
i = h.find(anchor)
assert i > 0, '锚点缺失'
h = h[:i] + sec + '\n' + h[i:]
open(f, 'w', encoding='utf-8').write(h)
print('系统消息补节完成 | 大小:', len(h))
