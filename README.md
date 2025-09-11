# Mapping the Invisible Internet (SWARM-I2P)

<p align="center">
  <img src="docs/Framework_SWARMI2P-4.jpg" alt="SWARM-I2P Framework Overview" width="850">
</p>

Large-scale deployment framework, data-collection scripts, and links to the publicly released dataset that maps the **network layer** of the Invisible Internet Project (I2P).

---

<p align="center">
  <a href="https://doi.org/10.5281/zenodo.15369068"><img alt="DOI" src="https://img.shields.io/badge/DOI-10.5281%2Fzenodo.15369068-blue"></a>
  <a href="#license"><img alt="Data License" src="https://img.shields.io/badge/Data%20License-CC%20BY%204.0-black"></a>
  <a href="#citation"><img alt="Cite" src="https://img.shields.io/badge/Cite-Please%20cite%20the%20dataset-green"></a>
</p>

## TL;DR

* **What:** Scripts + framework (SWARM-I2P) for deploying hundreds of I2P routers and collecting **network-layer** telemetry at scale.
* **Data:** >50k nodes observed; **FastSet**: 2,077; **High-capacity**: 2,331; latency \~121.21±48.50 ms; capacity \~8.57±1.20; multi-million traffic records.
* **Why:** Enable studies of tunnel peer selection, network resilience, centrality, and adversarial modeling at the router layer (not just eepsites).
* **Where:** Open dataset on Zenodo; collection scripts and reproducible configs here.

---

## Table of contents

1. [Overview](#overview)
2. [Repository layout](#repository-layout)
3. [Prerequisites](#prerequisites)
4. [Quick start](#quick-start)
5. [Configuration](#configuration)
6. [Collecting data](#collecting-data)
7. [What’s in the dataset](#whats-in-the-dataset)
8. [Analysis starters](#analysis-starters)
9. [Reproducibility & ethics](#reproducibility--ethics)
10. [Citing & DOI](#citation)
11. [Acknowledgments](#acknowledgments)
12. [License](#license)

---

## Overview

**SWARM-I2P** is a deployment and measurement framework that uses Docker-containerized I2P routers—optionally elevated to **floodfill**—to observe tunnel formation and peer selection across the I2P network.

Key ideas:

* **Dynamic port mapping (30,000–50,000)** to run many routers on one host while exposing standard I2P internals (e.g., 7657 web console, 4444 HTTP proxy) inside each container.
* **Hybrid lab/field setup:** local VMs (e.g., OCRI/University resources) bridged with cloud VPS through **SoftEther VPN**, enabling controlled measurement with Internet realism.
* **Minute-level polling** of each router’s console (`/tunnels`) + profile directories (`hosts.txt`, `.i2p/netDb`) to track active tunnels, roles, and peer performance.
* **Passive traffic capture** (Wireshark/tcpdump) on the VPN interface for metadata only (no content), plus router-computed performance metrics.

> The accompanying **Zenodo dataset** contains CSV/TXT exports ready for Pandas/R and includes country, speed, capacity, roles, and selection frequencies for peer nodes.

---
