## Data and Code Availability

**Dataset:** *Mapping the Invisible Internet: Framework and Dataset*  
**Latest version DOI:** [10.5281/zenodo.15369068](https://doi.org/10.5281/zenodo.15369068) (v2, April 25, 2025)  
**All-versions DOI (concept DOI):** [10.5281/zenodo.15278912](https://doi.org/10.5281/zenodo.15278912) (always resolves to the latest version)  
**License:** CC BY 4.0

**Code & Notebooks:** https://github.com/abksiddique/swarmi2p  
- `notebooks/` — figure notebooks  
- `scripts/` — data-processing utilities  
- `analysis/` — optional pipeline helpers

**Zenodo files used in the paper (by analysis):**
- **FastSet** (Top-20 & timeline): `4-Fastset-Nodes-By-Time.txt`, `5-Fastset-Frequency.txt`
- **High-capacity** (Top-20 by frequency): `6-High-Capacity-Set.txt`, `7-High-Capacity-Set-Freq.txt`
- **Profiles & geography** (Top-10 countries; speed/capacity dists; scatter): `9-Profile-By-Country.csv`, `10-Profiles-By-Country-anonymized.csv`
- **Exploratory/participatory/client tunnels:** `1-Client-Tunnel.csv`, `23-Exploratory-Tunnel.csv`, plus FF/non-FF logs (`11–15`)
- **Multi-tunnel nodes & traffic:** `16-Nodes-Multiple-Tunnels.csv`, `17-Nodes-In-MultiTunnels.csv`, `18-Nodes-In-MultiTunnels2.csv`

---

## Reproducible Figure Map (data ↔ code ↔ figure)

| Manuscript figure | What it shows | Zenodo file(s) *(DOI: [10.5281/zenodo.15369068](https://doi.org/10.5281/zenodo.15369068))* | Notebook / script (GitHub) | Output(s) (written by notebook) |
|---|---|---|---|---|
| **Fig. 5 — FastSet (Top-20 + timeline)** | Selection frequency & time trend | `4-Fastset-Nodes-By-Time.txt`, `5-Fastset-Frequency.txt` | `notebooks/Fastset_Nodes.ipynb` | `docs/figures/fig5_fastset_top20.png`, `docs/figures/fig5_fastset_timeline.png` |
| **Fig. 6 — High-capacity (Top-20 by frequency)** | Most-selected high-capacity peers | `6-High-Capacity-Set.txt`, `7-High-Capacity-Set-Freq.txt` | `notebooks/High_Capacity.ipynb` | `docs/figures/fig6_high_capacity_top20.png` |
| **Fig. 7 — Profiles overview (2×2)** | Top-10 countries; speed & capacity histograms; speed–capacity scatter | `9-Profile-By-Country.csv`, `10-Profiles-By-Country-anonymized.csv` | `notebooks/Profiles_Country.ipynb` | `docs/figures/fig7_profiles_overview_2x2.png` |
| **Fig. 8 — Nodes in multiple tunnels** | Nodes co-appearing across tunnel types | `16-Nodes-Multiple-Tunnels.csv` | `notebooks/Peers_Multiple_Tunnels.ipynb` | `docs/figures/fig8_multi_tunnel_nodes.png` |
| **Fig. 9 — Multi-tunnel traffic patterns** | Aggregate patterns for multi-tunnel nodes | `17-Nodes-In-MultiTunnels.csv`, `18-Nodes-In-MultiTunnels2.csv` | `notebooks/Nodes_MultiTunnels.ipynb` | `docs/figures/fig9_multi_tunnel_traffic.png` |
| *(If included)* **Fig. 10 — Entropy/Gini** | Diversity / concentration of peer selection | `4-Fastset-Nodes-By-Time.txt`, `6-High-Capacity-Set.txt`, `7-High-Capacity-Set-Freq.txt` | `notebooks/Entropy_Gini.ipynb` | `docs/figures/fig10_entropy_gini.png` |

**Run (minimal):**
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
# or: pip install pandas numpy matplotlib   # + pyarrow (optional, faster CSV)

requirements.txt
pandas>=2.0
numpy>=1.25
matplotlib>=3.8
# optional (large CSV performance)
pyarrow>=14.0

from pathlib import Path
import numpy as np

DATA = Path("data")               # change if your files are elsewhere
FIGS = Path("docs/figures"); FIGS.mkdir(parents=True, exist_ok=True)

np.random.seed(0)                 # deterministic plotting if any jitter/sampling is used

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

# in the repo root
pip install -r requirements.txt
jupyter notebook notebooks/Fastset_Nodes.ipynb
# open the notebook, adjust DATA path if needed, run all cells

pip install -r requirements.txt jupyter
jupyter nbconvert --to notebook --execute notebooks/Fastset_Nodes.ipynb --output /tmp/fastset_executed.ipynb
jupyter nbconvert --to notebook --execute notebooks/High_Capacity.ipynb --output /tmp/highcap_executed.ipynb
jupyter nbconvert --to notebook --execute notebooks/Profiles_Country.ipynb --output /tmp/profiles_executed.ipynb
jupyter nbconvert --to notebook --execute notebooks/Peers_Multiple_Tunnels.ipynb --output /tmp/peers_executed.ipynb
jupyter nbconvert --to notebook --execute notebooks/Nodes_MultiTunnels.ipynb --output /tmp/multitunnels_executed.ipynb
# (optional)
jupyter nbconvert --to notebook --execute notebooks/Entropy_Gini.ipynb --output /tmp/entropy_gini_executed.ipynb

import numpy as np
# freq = pandas.Series produced by value_counts() over peer IDs (selection counts)
p = (freq / freq.sum()).to_numpy()
entropy = -(p * np.log2(p)).sum()

sorted_p = np.sort(p)
cum = np.cumsum(sorted_p)
n = len(p)
gini = 1 - 2*np.sum(cum)/n + 1/n

## Citation

If you use the framework or data, please cite the dataset and this repository:

**Dataset (latest specific version):**

> Muntaka, S. A., Bou Abdo, J., Akanbi, K., Oluwadare, S., Hussein, F., Konyo, O., & Asante, M. (2025). *Mapping the Invisible Internet: Framework and Dataset* (v2) \[Data set]. Zenodo. [https://doi.org/10.5281/zenodo.15369068](https://doi.org/10.5281/zenodo.15369068)

**Dataset (all‑versions DOI, resolves to latest):**

> [https://doi.org/10.5281/zenodo.15278912](https://doi.org/10.5281/zenodo.15278912)

**BibTeX**

```bibtex
@dataset{muntaka2025mapping,
  title        = {Mapping the Invisible Internet: Framework and Dataset},
  author       = {Muntaka, Siddique A. and Bou Abdo, Jacques and Akanbi, Kemi and Oluwadare, Sunkanmi and Hussein, Faiza and Konyo, Oliver and Asante, Michael},
  year         = {2025},
  publisher    = {Zenodo},
  version      = {v2},
  doi          = {10.5281/zenodo.15369068},
  url          = {https://
```
