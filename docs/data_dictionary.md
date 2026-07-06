# Data dictionary

All files are UTF-8 CSV with a header row. Units are SI unless noted.
`pct` = percent, `deg` = degrees.

## `data/duty_specifications.csv` (Table 1)

| Column          | Type   | Description                                  |
|-----------------|--------|----------------------------------------------|
| `pump`          | string | Pump identifier (P1, P2, P3)                 |
| `application`   | string | Service / duty class                         |
| `Q_m3h`         | float  | Design flow rate (m³/h)                       |
| `H_m`           | float  | Design head (m)                              |
| `n_rpm`         | int    | Rotational speed (rpm)                       |
| `nq`            | int    | Dimensionless specific speed                 |
| `impeller_type` | string | Impeller archetype                           |

## `data/design_vector_bounds.csv` (Table 2)

| Column     | Type   | Description                                   |
|------------|--------|-----------------------------------------------|
| `variable` | string | Design-variable name                          |
| `symbol`   | string | Symbol used in the paper                       |
| `baseline` | float  | Baseline (seed) value                          |
| `lower`    | float  | Lower optimization bound                       |
| `upper`    | float  | Upper optimization bound                       |

## `data/doe/P*_doe_cfd_samples.csv`

One row per Latin-hypercube design sample evaluated by CFD.

| Column                      | Type  | Description                              |
|-----------------------------|-------|------------------------------------------|
| `sample_id`                 | string| Unique sample id (e.g. P1-007)           |
| `beta2_deg`                 | float | Outlet blade angle β₂ (deg)              |
| `Z_blades`                  | int   | Number of blades Z                        |
| `b2_D2`                     | float | Outlet width ratio b₂/D₂                  |
| `D1_D2`                     | float | Inlet diameter ratio D₁/D₂                |
| `phi_deg`                   | float | Blade wrap angle φ (deg)                  |
| `A8_mm2`                    | int   | Volute throat area A₈ (mm²)               |
| `eta_cfd_pct`               | float | Efficiency from high-fidelity RANS CFD    |
| `eta_physics_pct`           | float | Physics-only (1D) efficiency prediction   |
| `eta_hybrid_surrogate_pct`  | float | Hybrid twin (physics + GP) prediction     |
| `H_cfd_m`                   | float | CFD head at the design point (m)          |
| `NPSHr_m`                   | float | Required net positive suction head (m)    |

## `data/surrogate_accuracy/P*_surrogate_vs_cfd.csv` (Fig 3a)

| Column                     | Type   | Description                          |
|----------------------------|--------|--------------------------------------|
| `sample_id`                | string | Matches the DoE sample id            |
| `eta_cfd_pct`              | float  | CFD efficiency (reference / x-axis)  |
| `eta_physics_pct`          | float  | Physics-only prediction              |
| `eta_hybrid_surrogate_pct` | float  | Hybrid-twin prediction (y-axis)      |

`R² = 1 − Σ(ŷ−y)² / Σ(y−ȳ)²` and `RMSE = sqrt(mean((ŷ−y)²))` computed on
`eta_hybrid_surrogate_pct` vs `eta_cfd_pct` reproduce Table 5.

## `data/performance_curves/P*_twin_curves.csv` (Fig 2 — model lines)

| Column                    | Type  | Description                              |
|---------------------------|-------|------------------------------------------|
| `Q_m3h`                   | float | Flow rate (m³/h)                          |
| `H_cfd_twin_m`            | float | Head from the CFD digital twin (m)        |
| `H_surrogate_twin_m`      | float | Head from the surrogate twin (m)          |
| `eta_cfd_twin_pct`        | float | Efficiency from the CFD twin (%)          |
| `eta_surrogate_twin_pct`  | float | Efficiency from the surrogate twin (%)    |
| `is_bep`                  | bool  | True at the best-efficiency-point row     |

## `data/performance_curves/P*_experiment_points.csv` (Fig 2 — rig points)

| Column        | Type  | Description                     |
|---------------|-------|---------------------------------|
| `Q_m3h`       | float | Measured flow rate (m³/h)        |
| `H_exp_m`     | float | Measured head (m), ISO 9906      |
| `eta_exp_pct` | float | Measured efficiency (%)          |

## `data/bep_validation.csv` (Table 4)

| Column          | Type  | Description                                |
|-----------------|-------|--------------------------------------------|
| `pump`          | string| Pump identifier                            |
| `H_exp_m`       | float | Rig head at BEP (m)                        |
| `H_twin_m`      | float | Calibrated-twin head at BEP (m)            |
| `epsH_pct`      | float | Relative head error (%)                    |
| `eta_exp_pct`   | float | Rig efficiency at BEP (%)                  |
| `eta_twin_pct`  | float | Calibrated-twin efficiency at BEP (%)      |
| `epseta_pct`    | float | Relative efficiency error (%)              |

## `data/twin_metrics.csv` (Table 5)

| Column           | Type  | Description                               |
|------------------|-------|-------------------------------------------|
| `pump`           | string| Pump identifier                           |
| `cfd_samples`    | int   | Number of CFD training samples            |
| `R2`             | float | Coefficient of determination (surrogate)  |
| `RMSE_eta_pct`   | float | RMSE of surrogate efficiency (%)          |
| `core_hours`     | int   | CFD compute budget (core-hours)           |
| `twin_query_ms`  | float | Mean surrogate query time (ms)            |
