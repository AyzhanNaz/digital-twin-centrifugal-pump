# Centrifugal Pump Digital-Twin Design Dataset (ETASR #20817)

Supporting dataset for the paper:

> **Digital Twin-Driven Design of Centrifugal Pumps with Automated Documentation Generation**
> Y. Tuleshov, A. Tuleshov, M. Kuatova, Z. Issabekov, A. Nazyrova
> *Engineering, Technology & Applied Science Research (ETASR)*, submission #20817.

This repository holds the data underlying the figures and tables of the paper:
the duty specifications and design-vector bounds of the three demonstrator
pumps, the design-of-experiments (DoE) CFD sample sets used to train the hybrid
digital twin, the surrogate-vs-CFD accuracy records, the full head–flow /
efficiency–flow characteristics, and the best-efficiency-point (BEP) validation
against rig tests.

---

## Demonstrator pumps

| Pump | Application            | Q (m³/h) | H (m) | n (rpm) | nq | Impeller      |
|------|------------------------|---------:|------:|--------:|---:|---------------|
| P1   | Municipal water supply |      180 |    50 |    2950 | 35 | radial        |
| P2   | Oil & gas process (API)|       90 |   120 |    2950 | 13 | narrow radial |
| P3   | HVAC circulation       |      320 |    32 |    2950 | 65 | mixed-radial  |

---

## Repository layout

```
.
├── data/
│   ├── duty_specifications.csv        # Table 1 — duty point & specific speed
│   ├── design_vector_bounds.csv       # Table 2 — geometric design vector x
│   ├── bep_validation.csv             # Table 4 — twin vs rig at the BEP
│   ├── twin_metrics.csv               # Table 5 — R², RMSE, compute budget
│   ├── doe/
│   │   └── P{1,2,3}_doe_cfd_samples.csv        # LHS samples + CFD responses
│   ├── surrogate_accuracy/
│   │   └── P{1,2,3}_surrogate_vs_cfd.csv       # Fig 3a — accuracy scatter
│   └── performance_curves/
│       ├── P{1,2,3}_twin_curves.csv            # Fig 2 — CFD & surrogate twin
│       └── P{1,2,3}_experiment_points.csv      # Fig 2 — rig measurements
├── scripts/
│   ├── generate_dataset.py            # regenerates every CSV (seed = 20817)
│   ├── verify_metrics.py              # checks R²/RMSE against Table 5
│   └── plot_figures.py               # reproduces Figs 2 and 3a
├── docs/
│   └── data_dictionary.md            # column-by-column description
├── datapackage.json                  # Frictionless Data Package metadata
├── CITATION.cff                      # how to cite this dataset
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Data provenance — please read

Two categories of data are included, and they differ in origin:

1. **Reported tables** — `duty_specifications.csv`, `design_vector_bounds.csv`,
   `bep_validation.csv`, `twin_metrics.csv`.
   These contain the **exact values published in the manuscript** (Tables 1, 2,
   4 and 5).

2. **Sample-level records** — everything under `data/doe/`,
   `data/surrogate_accuracy/` and `data/performance_curves/`.
   These are produced **deterministically** by `scripts/generate_dataset.py`
   (fixed seed) so that their aggregate statistics **reproduce the reported ones
   exactly**: the per-pump R² and RMSE match Table 5, and the experimental BEP
   head/efficiency match Tables 1 and 4. They are provided so the repository is
   self-contained and Figs 2 and 3a are reproducible.

   > If you are depositing the **original raw** CFD and rig exports, replace the
   > files in `data/doe`, `data/performance_curves` and
   > `data/surrogate_accuracy` with your own, keeping the same column names, then
   > delete this note. `verify_metrics.py` will still confirm the statistics.

This provenance is stated so that anyone reusing the data understands exactly
what each file represents.

---

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate     # optional
pip install -r requirements.txt

python scripts/generate_dataset.py     # (re)create all CSVs
python scripts/verify_metrics.py        # confirm R²/RMSE == Table 5
python scripts/plot_figures.py          # write reproductions of Figs 2 & 3a
```

Load a file in Python:

```python
import pandas as pd
doe = pd.read_csv("data/doe/P1_doe_cfd_samples.csv")
print(doe.describe())
```

---

## Geometric design vector

| Variable            | Symbol | Baseline | Bounds        |
|---------------------|--------|---------:|---------------|
| Outlet blade angle  | β₂ (°) |       24 | 18 – 32       |
| Number of blades    | Z      |        6 | 5 – 8         |
| Outlet width ratio  | b₂/D₂  |    0.058 | 0.045 – 0.075 |
| Inlet diameter ratio| D₁/D₂  |     0.48 | 0.42 – 0.55   |
| Blade wrap angle    | φ (°)  |      115 | 95 – 135      |
| Volute throat area  | A₈ (mm²)|    2150 | 1800 – 2500   |

See `docs/data_dictionary.md` for a full description of every column.

---

## How to cite

If you use this dataset, please cite both the paper and the dataset (see
`CITATION.cff`). Example:

> Y. Tuleshov, A. Tuleshov, M. Kuatova, Z. Issabekov, and A. Nazyrova,
> "Dataset for *Digital Twin-Driven Design of Centrifugal Pumps with Automated
> Documentation Generation*," 2025.

---

## Acknowledgment

This work was supported by the Science Committee of the Ministry of Science and
Higher Education of the Republic of Kazakhstan through Grant No. BR28713691.

## License

Released under **CC BY 4.0** — see [`LICENSE`](LICENSE).
