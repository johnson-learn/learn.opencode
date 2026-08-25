---
name: networking-telecom
description: >
  Analyzes modern networking architectures including 5G, SDN (Software-Defined Networking),
  NFV (Network Function Virtualization), edge networking, QUIC, HTTP/3, and network security.
  Triggered by questions like "5G deployment", "SDN architecture", "QUIC protocol", "edge networking",
  or "network protocol" comparisons. Evaluates throughput, latency, reliability, standards compliance.
---

## Overview

This skill provides deep expertise in modern network infrastructure and protocols, from 5G mobile networks to advanced transport protocols and software-defined architectures. It helps teams evaluate network solutions for performance-critical applications, telco transformations, and edge computing strategies.

## Core Domains

### 5G & Cellular Networks
- **Architecture**: RAN (Radio Access Network), NSA (non-standalone) vs SA (standalone) deployments
- **Use Cases**: Low-latency (URLLC), massive IoT (mMTC), high throughput (eMBB)
- **Spectrum**: mmWave (28/39 GHz), Sub-6, mid-band considerations
- **Network Slicing**: Virtualized networks for different SLA requirements
- Deployment challenge: Infrastructure investment, legacy interop (4G fallback)

### Software-Defined Networking (SDN)
- **OpenFlow**: Control plane separation, programmable switches
- **Network Operating Systems**: ONF, ONAP, OpenDaylight
- **Virtual Overlays**: VLAN, VxLAN, Segment Routing (SR)
- Use case trigger: "network programmability", "multi-tenant isolation", "dynamic routing"
- Cost benefit: Commodity hardware + software control vs proprietary switches

### Network Function Virtualization (NFV)
- **vRAN**: Virtualized RAN for 5G deployments
- **vEPC**: Virtual Evolved Packet Core (mobile core network)
- **Service Function Chaining**: Load balancers, firewalls, DPI as VMs
- Challenge: Performance (latency), state management across replicas

### Edge Networking
- **Multi-access Edge Computing (MEC)**: Compute at network edge (5G base stations)
- **Content Delivery Networks (CDN)**: Akamai, Cloudflare, AWS CloudFront architecture
- **IP Anycast**: DNS-based steering to nearest edge location
- Trigger: "reducing latency", "DDoS mitigation", "content distribution at scale"

### Modern Transport Protocols
- **QUIC**: Multiplexed streams, connection migration, better mobile experience
- **HTTP/3**: Native QUIC, header compression (QPACK), 0-RTT
- **SCTP**: Ordered/unordered delivery, multi-streaming, failover
- **WireGuard**: Modern VPN protocol (simpler, auditable vs OpenVPN)
- Adoption signal: Browser support, CDN adoption (HTTP/3 now ~40% of web)

### Network Security
- **DDoS Mitigation**: Anycast scrubbing, rate limiting, behavioral analysis
- **Zero Trust**: Encrypted channels, micro-segmentation, continuous verification
- **TLS 1.3+**: Connection resumption, post-handshake auth, ESNI
- **DNSSEC**: DNS validation, TSIG, DNS-over-HTTPS (DoH)
- Challenge: Performance impact, management complexity at scale

### Mesh Networking
- **Service Mesh (Istio, Linkerd)**: Application network control
- **IoT Mesh (Thread, Zigbee, LoRaWAN)**: Low-power mesh topologies
- **Self-healing**: Automatic reroute on node failure, traffic balancing
- Use case: Distributed systems, low-power IoT, multi-tenancy isolation

## Evaluation Dimensions

**Throughput**: Gbps capacity; overprovisioning ratios for peak vs average

**Latency**: 5G URLLC targets (1ms); HTTP/3 0-RTT vs TCP 3-way handshake

**Reliability**: BGP convergence time, failover mechanisms, redundancy

**Standards Compliance**: 3GPP for 5G, IETF RFCs for protocols, IEEE 802.1X for security

**Deployment Complexity**: Vendor lock-in, skill requirements, operational tools

**Cost Model**: Spectrum (5G), hardware/software (SDN), traffic (bandwidth)

## When to Use This Skill

- **Evaluating 5G readiness** for mobile applications
- **Designing SDN/NFV architecture** for large-scale networks
- **Protocol selection**: REST, gRPC, QUIC for specific latency/throughput needs
- **Edge deployment strategy**: CDN, MEC, private networks
- **Network security assessment**: DDoS resilience, encryption, compliance
- **Telecom transformation**: Legacy network → cloud-native architecture

## Output Examples

- 5G deployment playbook (RAN architecture, spectrum strategy, timeline)
- SDN architecture diagram with OpenFlow flows and control plane design
- Protocol comparison matrix (latency, throughput, resource overhead)
- Edge deployment topology (CDN origins, regional caching, failover)
- Network security posture assessment (DDoS, encryption, zero trust readiness)

## Computational Workflows

### Pre-built Analysis Scripts

**5g_spectrum_planner.py**: Calculates coverage and capacity given spectrum allocation (sub-6 GHz vs mmWave), antenna configuration, and population density. Outputs: predicted coverage map, capacity per cell (Gbps), required base stations per region.

**latency_simulator.py**: Models end-to-end latency across 5G RAN, backhaul, and cloud (MEC vs central). Takes RTT, queueing model, processing overhead. Outputs: p50, p95, p99 latency distributions for URLLC (target 1ms) vs eMBB (50ms acceptable).

**sdxl_switch_cost_model.py**: Compares commodity hardware + OpenFlow controller vs proprietary switches. Input: switch count, ports, feature set. Output: TCO 5-year (hardware, licensing, training, power) and break-even point.

**cdn_edge_location_optimizer.py**: Takes user geography (IP-based), traffic patterns, and input edge locations (Akamai, Cloudflare). Outputs: optimal edge node placement, expected latency reduction, cost vs performance trade-off.

### Dynamic Computation Examples

1. **5G Deployment Cost Estimation**: Input site count, spectrum licenses, RAN equipment types (vRAN vs traditional). Compute: capex per site, opex (power, cooling, backhaul), years to RoI at subscriber growth rate.

2. **Protocol Overhead Analysis**: Compare HTTP/1.1 vs HTTP/3 on lossy networks (3G, satellite, 10% packet loss). Calculate throughput reduction, connection setup time, effective latency for real-world scenarios.

3. **Network Slicing Revenue Model**: Given network capacity (100 Gbps), allocate across slices (URLLC 1%, eMBB 50%, mMTC 49%). Compute: revenue per slice at market rates, capacity-demand balance, overcommit risk.

### Output Artifacts

- **5G Deployment Playbook**: Site list, spectrum strategy, RAN architecture choices, timeline Gantt chart
- **Protocol Comparison Matrix**: Throughput, latency, connection setup time, battery impact (for mobile) across HTTP/1.1, HTTP/2, HTTP/3, gRPC
- **Edge Computing Topology Map**: CDN origins, regional cache nodes, user distribution heatmap, latency contours
- **Network Security Posture Dashboard**: DDoS resilience score, encryption coverage (%), zero-trust readiness assessment

---

**Supercharged By**: Telecom/infrastructure connectors (OpenStack, Kubernetes for NFV); 5G vendor APIs (Ericsson, Nokia); network analytics (NetFlow, sFlow) for observability

## Data Sources

| Connector | Purpose |
|-----------|---------|
| ~~web research | IETF RFCs, 3GPP specifications, vendor white papers |
| ~~source control | Open-source networking projects, protocol implementations |
| ~~research | Academic papers on network protocols, 5G/6G standards |
