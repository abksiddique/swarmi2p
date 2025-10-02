# Mapping the Invisible Internet (SWARM-I2P)

<p align="center">
  <img src="docs/Framework_SWARMI2P-4.jpg" alt="SWARM-I2P Framework Overview" width="100%">
</p>

Large-scale deployment framework, data-collection scripts, and links to the publicly released dataset that maps the **network layer** of the Invisible Internet Project (I2P).

---

<p align="center">
  <a href="https://doi.org/10.5281/zenodo.15369068"><img alt="DOI" src="https://img.shields.io/badge/DOI-10.5281%2Fzenodo.15369068-blue"></a>
  <a href="#license"><img alt="Data License" src="https://img.shields.io/badge/Data%20License-CC%20BY%204.0-black"></a>
  <a href="#citation"><img alt="Cite" src="https://img.shields.io/badge/Cite-Please%20cite%20the%20dataset-green"></a>
</p>

1. Please cite the primary research paper

## Citation

If you use the framework or dataset, please cite the primary research paper and the dataset archive as follows:

1.  **Primary Research Paper:**
    Muntaka, S. A., Abdo, J. B., Akanbi, K., Oluwadare, S., Hussein, F., Konyo, O., & Asante, M. (2025). Mapping the Invisible Internet: Framework and Dataset. *arXiv preprint* arXiv:2506.18159.

2.  **Dataset Archive:**
    Muntaka, S. A., Bou Abdo, J., Akanbi, K., Oluwadare, S., Hussein, F., Konyo, O., & Asante, M. (2025). *Mapping the Invisible Internet: Framework and Dataset* [Data set]. Zenodo. **<https://doi.org/10.5281/zenodo.15369068>**


## TL;DR

* **What:** Scripts + framework (SWARM-I2P) for deploying hundreds of I2P routers and collecting **network-layer** telemetry at scale.
* **Data:** >50k nodes observed; **FastSet**: 2,077; **High-capacity**: 2,331; latency ≈ **121.21 ± 48.50 ms**; capacity ≈ **8.57 ± 1.20**; multi-million traffic records.
* **Why:** Enable studies of tunnel peer selection, network resilience, centrality, and adversarial modeling at the router layer (not just eepsites).
* **Where:** Open dataset on Zenodo; collection scripts and reproducible notebooks here.

---

## Table of contents

1. [Overview](#overview)
2. [Repository layout](#repository-layout)
3. [Prerequisites](#prerequisites)
4. [Quick start](#quick-start)
5. [Configuration](#configuration)
6. [Collecting data](#collecting-data)
7. [What’s in the dataset](#whats-in-the-dataset)
8. [Data and Code Availability](#data-and-code-availability)
9. [Reproducible Figure Map](#reproducible-figure-map)
10. [Environment & Paths](#environment--paths)
11. [Checksum Verification](#checksum-verification)
12. [Reproducing the Figures](#reproducing-the-figures)
13. [Analysis starters](#analysis-starters)
14. [Entropy & Gini (clarification)](#entropy--gini-clarification)
15. [Reproducibility & ethics](#reproducibility--ethics)
16. [Acknowledgments](#acknowledgments)
17. [License](#license)
18. [Citation](#citation)

---

## Overview

**SWARM-I2P** is a deployment and measurement framework that uses Docker-containerized I2P routers—optionally elevated to **floodfill**—to observe tunnel formation and peer selection across the I2P network.

**Key ideas:**

* **Dynamic port mapping (30,000–50,000)** to run many routers on one host while exposing standard I2P internals (e.g., 7657 web console, 4444 HTTP proxy) inside each container.
* **Hybrid lab/field setup:** local VMs (e.g., university resources) bridged with cloud VPS through **SoftEther VPN**, enabling controlled measurement with Internet realism.
* **Minute-level polling** of each router’s console (`/tunnels`) + profile directories (`hosts.txt`, `.i2p/netDb`) to track active tunnels, roles, and peer performance.
* **Passive traffic capture** (Wireshark/tcpdump) on the VPN interface for metadata only (no content), plus router-computed performance metrics.

> The accompanying **Zenodo dataset** contains CSV/TXT exports ready for Pandas/R and includes country, speed, capacity, roles, and selection frequencies for peer nodes.

---

## Repository layout

> *If your folder names differ, keep this section as a guide and adjust paths in examples.*

```
.
├─ docker/                # Dockerfile(s), docker-compose.yml, Portainer templates
├─ config/                # .env samples, router.config snippets, ufw rules, SoftEther notes
├─ scripts/               # Python & Bash data collectors and utilities
├─ notebooks/             # Jupyter notebooks for EDA & figures
├─ analysis/              # Reproducible pipelines (e.g., Make/Invoke)
├─ data/                  # (optional) small samples; full data lives on Zenodo
└─ docs/                  # Figures, UML, methodology notes
```

---

## Prerequisites

* Linux host (tested on **Ubuntu 24.04 LTS**)
* **Docker** + **Docker Compose** (Portainer optional but handy)
* (Optional) **SoftEther VPN** server/bridge if you’re reproducing the hybrid lab–cloud topology
* `ufw` (or equivalent) to allow and persist port ranges you map to containers

---

## Quick start

1. **Clone**

```bash
git clone https://github.com/abksiddique/swarmi2p.git
cd swarmi2p
```

2. **Copy and edit environment**

```bash
cp config/.env.sample .env
# set ROUTER_COUNT, PORT_RANGE_START=30000, PORT_RANGE_END=50000, etc.
```

3. **Launch the swarm**

```bash
docker compose up -d
```

4. (Optional) **Portainer**: import `docker/portainer-template.json` and deploy stacks visually.
5. **Verify routers**

* Inside a router container, startup is typically automated. If needed: `./i2prouter start`
* Access a container’s console via forwarded web port (e.g., `http://localhost:<mapped>/`)

### Minimal `docker-compose.yml` (excerpt)

```yaml
services:
  i2p-router:
    build: ./docker/i2p
    deploy:
      replicas: ${ROUTER_COUNT:-10}
    environment:
      I2P_FLOODFILL: "${FLOODFILL:-false}"
    ports:
      # example: programmatically allocate host ports 30000–50000 to container internals
      - "${HTTP_CONSOLE_PORT:-40137}:7657"   # I2P console
      - "${HTTP_PROXY_PORT:-40444}:4444"    # HTTP proxy
    volumes:
      - i2pdata:/home/i2p/.i2p
    restart: unless-stopped
volumes:
  i2pdata:
```

---

## Configuration

* **Dynamic port mapping:** allocate a unique host port per router instance from **30,000–50,000** and map to standard internals (e.g., 7657, 4444) in each container.
* **Floodfill elevation:** append the recommended parameters to `router.config` for selected instances (see `config/router.config.floodfill.example`).
* **Firewall (ufw):** open only the host port ranges you actually use.
* **SoftEther VPN:** create a site-to-site bridge if combining on-prem resources and VPS; capture on the VPN NIC for traffic metadata.

---

## Collecting data

### Console & profiles polling

Run the collector at a 60-second interval against each containerized router:

```bash
python scripts/collect_tunnels.py \
  --interval 60 \
  --console http://127.0.0.1:<HTTP_CONSOLE_PORT>/tunnels \
  --profiles /home/i2p/.i2p
```

The collector extracts: tunnel type (client/exploratory/participatory), direction, expiration, bytes, and **node roles** (gateway/participant/endpoint), along with abbreviated & full router IDs, country, and IP (v4/v6) when available.

### Traffic metadata capture (optional)

```bash
sudo tcpdump -i <vpn_nic> -w captures/swarmi2p.pcap
```

Use custom display filters in Wireshark during analysis; do **not** attempt to decrypt or intercept content.

---

## What’s in the dataset

Public release on Zenodo (see DOI badge above). **Key files include:**

* **1-Client-Tunnel.csv / 2-Client-Tunnel-anonymized.csv** — Client tunnel peers with timestamps, directions, roles, bytes.
* **3-Fastset-Nodes.txt; 4-Fastset-Nodes-By-Time.txt; 5-Fastset-Frequency.txt** — 2,077 unique FastSet peers and selection frequency over time.
* **6-High-Capacity-Set.txt; 7-High-Capacity-Set-Freq.txt; 8-High-Capaity-Freq2.txt** — 2,331 high-capacity peers; backbone selection patterns.
* **9-Profile-By-Country.csv; 10-Profiles-By-Country-anonymized.csv** — ~3,444 peer profiles with country, version, speed, capacity, caps.
* **11–15 FF/non-FF tunnel logs** — Floodfill vs. standard router observations (client/exploratory/participatory).
* **16–18 Multi-tunnel node tables** — Nodes that appear in several tunnels concurrently; top talkers/destinations.
* **21–22 TrafficMetadata*.csv** — High-volume traffic metadata (packets/bytes; multi-million rows) for aggregate patterns.
* **23-Exploratory-Tunnel.csv** — 24-hour exploratory tunnel sessions.

**Headline stats (from the release):**

* > **50,000** nodes observed overall
* **FastSet:** **2,077**; **High-capacity:** **2,331**
* **Latency:** mean ≈ **121.21 ms** (± 48.50)
* **Capacity:** mean ≈ **8.57** (± 1.20)
* **Traffic records:** ~1,997 (≈ 1,003,032 packets/bytes) and ~4,222,793 (≈ 2,147,585,625 packets/bytes)

---

## Data and Code Availability

**Dataset:** *Mapping the Invisible Internet: Framework and Dataset*
**Latest version DOI:** [10.5281/zenodo.15369068](https://doi.org/10.5281/zenodo.15369068) (v2, April 25, 2025)
**All-versions DOI (concept DOI):** [10.5281/zenodo.15278912](https://doi.org/10.5281/zenodo.15278912) (always resolves to the latest version)
**License:** CC BY 4.0

**Code & Notebooks:** [https://github.com/abksiddique/swarmi2p](https://github.com/abksiddique/swarmi2p)

* `notebooks/` — figure notebooks
* `scripts/` — data-processing utilities
* `analysis/` — optional pipeline helpers

**Zenodo files used in the paper (by analysis):**

* **FastSet** (Top-20 & timeline): `4-Fastset-Nodes-By-Time.txt`, `5-Fastset-Frequency.txt`
* **High-capacity** (Top-20 by frequency): `6-High-Capacity-Set.txt`, `7-High-Capacity-Set-Freq.txt`
* **Profiles & geography** (Top-10 countries; speed/capacity dists; scatter): `9-Profile-By-Country.csv`, `10-Profiles-By-Country-anonymized.csv`
* **Exploratory/participatory/client tunnels:** `1-Client-Tunnel.csv`, `23-Exploratory-Tunnel.csv`, plus FF/non-FF logs (`11–15`)
* **Multi-tunnel nodes & traffic:** `16-Nodes-Multiple-Tunnels.csv`, `17-Nodes-In-MultiTunnels.csv`, `18-Nodes-In-MultiTunnels2.csv`

---

## Reproducible Figure Map

| Manuscript figure                                | What it shows                                                         | Zenodo file(s) *(DOI: [10.5281/zenodo.15369068](https://doi.org/10.5281/zenodo.15369068))* | Notebook / script (GitHub)               | Output(s) (written by notebook)                                                 |
| ------------------------------------------------ | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ---------------------------------------- | ------------------------------------------------------------------------------- |
| **Fig. 5 — FastSet (Top-20 + timeline)**         | Selection frequency & time trend                                      | `4-Fastset-Nodes-By-Time.txt`, `5-Fastset-Frequency.txt`                                   | `notebooks/Fastset_Nodes.ipynb`          | `docs/figures/fig5_fastset_top20.png`, `docs/figures/fig5_fastset_timeline.png` |
| **Fig. 6 — High-capacity (Top-20 by frequency)** | Most-selected high-capacity peers                                     | `6-High-Capacity-Set.txt`, `7-High-Capacity-Set-Freq.txt`                                  | `notebooks/High_Capacity.ipynb`          | `docs/figures/fig6_high_capacity_top20.png`                                     |
| **Fig. 7 — Profiles overview (2×2)**             | Top-10 countries; speed & capacity histograms; speed–capacity scatter | `9-Profile-By-Country.csv`, `10-Profiles-By-Country-anonymized.csv`                        | `notebooks/Profiles_Country.ipynb`       | `docs/figures/fig7_profiles_overview_2x2.png`                                   |
| **Fig. 8 — Nodes in multiple tunnels**           | Nodes co-appearing across tunnel types                                | `16-Nodes-Multiple-Tunnels.csv`                                                            | `notebooks/Peers_Multiple_Tunnels.ipynb` | `docs/figures/fig8_multi_tunnel_nodes.png`                                      |
| **Fig. 9 — Multi-tunnel traffic patterns**       | Aggregate patterns for multi-tunnel nodes                             | `17-Nodes-In-MultiTunnels.csv`, `18-Nodes-In-MultiTunnels2.csv`                            | `notebooks/Nodes_MultiTunnels.ipynb`     | `docs/figures/fig9_multi_tunnel_traffic.png`                                    |


**Run (minimal):**

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
# or: pip install pandas numpy matplotlib   # + pyarrow (optional, faster CSV)
```

**Data:** Download the files listed above from the Zenodo DOI and place them in a local `data/` directory (or edit the first cell in each notebook to point to your path).
**Outputs:** Each notebook writes figures to `docs/figures/`.

---

## Environment & Paths

Create a minimal environment (Python ≥ 3.10 recommended):

```
requirements.txt
pandas>=2.0
numpy>=1.25
matplotlib>=3.8
# optional (large CSV performance)
pyarrow>=14.0
```

Each notebook begins with stable paths and reproducibility settings:

```python
from pathlib import Path
import numpy as np

DATA = Path("data")               # change if your files are elsewhere
FIGS = Path("docs/figures"); FIGS.mkdir(parents=True, exist_ok=True)

np.random.seed(0)                 # deterministic plotting if any jitter/sampling is used
```

---

## Checksum Verification

Verify downloads against Zenodo MD5 checksums:

```bash
# FastSet
md5sum data/4-Fastset-Nodes-By-Time.txt      # expect: 7a11c3b5525603a7652a14bef294cf04
md5sum data/5-Fastset-Frequency.txt          # expect: 6c761dbbb9ee7352e424d196852bfb57

# High-capacity
md5sum data/6-High-Capacity-Set.txt          # expect: 3f866e5793a281a751d1a63a1c28413d
md5sum data/7-High-Capacity-Set-Freq.txt     # expect: 6ba67c113104bd9faf85e5baa878ac36

# Profiles & geography
md5sum data/9-Profile-By-Country.csv         # expect: 2eaed6ded040c970eabd7131bd311e3a
md5sum data/10-Profiles-By-Country-anonymized.csv  # expect: 21b45a84411fd458a760078f73cb5d3d

# Client / exploratory tunnels
md5sum data/1-Client-Tunnel.csv              # expect: 9e838ce7919e8308e7ba083ab75c19e9
md5sum data/23-Exploratory-Tunnel.csv        # expect: edad84685d18dc270da45ce7b5811187

# Multi-tunnel nodes & traffic
md5sum data/16-Nodes-Multiple-Tunnels.csv    # expect: 99b1bfaa6514e217be553a61a3595a5d
md5sum data/17-Nodes-In-MultiTunnels.csv     # expect: 9714c95c5749531f56d8b97875272fc8
md5sum data/18-Nodes-In-MultiTunnels2.csv    # expect: 139ebf40041e97819d6bf6f4b0f78a59
```

If a checksum differs, re-download from Zenodo.

---

## Reproducing the Figures

### Interactive (Jupyter)

```bash
# in the repo root
pip install -r requirements.txt
jupyter notebook notebooks/Fastset_Nodes.ipynb
# open the notebook, adjust DATA path if needed, run all cells
```

### Headless (non-interactive)

```bash
pip install -r requirements.txt jupyter
jupyter nbconvert --to notebook --execute notebooks/Fastset_Nodes.ipynb --output /tmp/fastset_executed.ipynb
jupyter nbconvert --to notebook --execute notebooks/High_Capacity.ipynb --output /tmp/highcap_executed.ipynb
jupyter nbconvert --to notebook --execute notebooks/Profiles_Country.ipynb --output /tmp/profiles_executed.ipynb
jupyter nbconvert --to notebook --execute notebooks/Peers_Multiple_Tunnels.ipynb --output /tmp/peers_executed.ipynb
jupyter nbconvert --to notebook --execute notebooks/Nodes_MultiTunnels.ipynb --output /tmp/multitunnels_executed.ipynb
# (optional)
jupyter nbconvert --to notebook --execute notebooks/Entropy_Gini.ipynb --output /tmp/entropy_gini_executed.ipynb
```

Each notebook reads the **exact** Zenodo files listed in the map above and writes its figures to `docs/figures/`.

---

## Analysis starters

**Load and peek in Python**

```python
import pandas as pd
ct = pd.read_csv('data/2-Client-Tunnel-anonymized.csv')
ct.head()
```

**Compute peer selection entropy & Gini (from empirical frequencies)**

```python
import numpy as np
freq = ct['peer_id'].value_counts()
p = (freq / freq.sum()).to_numpy()

# Shannon entropy (bits)
entropy = -(p * np.log2(p)).sum()

# Gini coefficient
sorted_p = np.sort(p)
cum = np.cumsum(sorted_p)
n = len(p)
gini = 1 - 2*np.sum(cum)/n + 1/n

print({'entropy': float(entropy), 'gini': float(gini)})
```

---

## Entropy & Gini (clarification)

When reported, **Shannon entropy** and **Gini** are computed from the empirical **peer-selection frequency distribution** derived from the dataset—**no hard-coded statistics**. The notebook `notebooks/Entropy_Gini.ipynb` reconstructs these values directly from the Zenodo inputs listed in the Figure Map.

---

## Reproducibility & ethics

* **No content interception.** Only router-level metadata and performance stats are collected.
* **Anonymization.** Released datasets strip direct identifiers where appropriate.
* **Rate limits.** Console polling and captures are tuned to avoid perturbing the network.
* **Geographic bias.** Initial nodes skewed to NA/EU; later expansions included other regions.

If you extend SWARM-I2P, please keep these practices and document any deviations.

---

## Acknowledgments

We thank collaborators and institutional resources that supported data collection and analysis infrastructure.

---

## License

* **Data:** Creative Commons **CC BY 4.0** (see Zenodo record).
* **Code:** See repository **LICENSE** file (if present). If absent, the authors retain the code’s copyright.

---

## Citation

If you use the framework or dataset, please cite the dataset and this repository.

**Dataset (latest specific version):**
Muntaka, S. A., Bou Abdo, J., Akanbi, K., Oluwadare, S., Hussein, F., Konyo, O., & Asante, M. (2025). *Mapping the Invisible Internet: Framework and Dataset* (v2) [Data set]. Zenodo. [https://doi.org/10.5281/zenodo.15369068](https://doi.org/10.5281/zenodo.15369068)

**Dataset (all-versions DOI, resolves to latest):**
[https://doi.org/10.5281/zenodo.15278912](https://doi.org/10.5281/zenodo.15278912)

**BibTeX**

```bibtex
@dataset{muntaka2025mapping,
  title        = {Mapping the Invisible Internet: Framework and Dataset},
  author       = {Muntaka, Siddique A. and Bou Abdo, Jacques and Akanbi, Kemi and Oluwadare, Sunkanmi and Hussein, Faiza and Konyo, Oliver and Asante, Michael},
  year         = {2025},
  publisher    = {Zenodo},
  version      = {v2},
  doi          = {10.5281/zenodo.15369068},
  url          = {https://doi.org/10.5281/zenodo.15369068}
}
```
