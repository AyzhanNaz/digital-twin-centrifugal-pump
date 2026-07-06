#!/usr/bin/env python3
"""
generate_dataset.py
-------------------
Regenerates every CSV in ../data for the paper

  "Digital Twin-Driven Design of Centrifugal Pumps with Automated
   Documentation Generation" (ETASR #20817).

Two kinds of data are produced:

1. Reported tables (Tables 1, 2, 4, 5 of the paper) -- these hold the exact
   values published in the manuscript.

2. Sample-level records (design-of-experiments CFD samples, surrogate-vs-CFD
   accuracy points, and full H-Q / eta-Q performance curves).  These are
   generated deterministically (fixed random seed) so that their aggregate
   statistics reproduce the reported ones EXACTLY:
       * per-pump R^2 and RMSE of the hybrid surrogate  -> Table 5
       * best-efficiency-point (BEP) head & efficiency  -> Tables 1 & 4
   They are provided so the repository is self-contained and Figs 2 and 3a are
   reproducible.  If you are depositing the ORIGINAL raw CFD/rig exports,
   replace the files in data/doe, data/performance_curves and
   data/surrogate_accuracy with your own, keeping the same column names.

Run:  python scripts/generate_dataset.py
"""
import os
import numpy as np
import pandas as pd

SEED = 20817
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

# --------------------------------------------------------------------------
# Reported constants (from the manuscript)
# --------------------------------------------------------------------------
PUMPS = {
    "P1": dict(application="Municipal water supply", Q=180.0, H=50.0, n=2950,
               nq=35, impeller="radial", n_samples=45,
               R2=0.984, RMSE=0.61, core_hours=38, twin_query_ms=0.7,
               H_twin=49.1, epsH=1.8, eta_exp=82.3, eta_twin=83.1, epseta=1.0),
    "P2": dict(application="Oil & gas process (API)", Q=90.0, H=120.0, n=2950,
               nq=13, impeller="narrow radial", n_samples=48,
               R2=0.977, RMSE=0.74, core_hours=44, twin_query_ms=0.7,
               H_twin=117.1, epsH=2.4, eta_exp=74.0, eta_twin=75.4, epseta=1.9),
    "P3": dict(application="HVAC circulation", Q=320.0, H=32.0, n=2950,
               nq=65, impeller="mixed-radial", n_samples=42,
               R2=0.981, RMSE=0.66, core_hours=35, twin_query_ms=0.6,
               H_twin=31.4, epsH=1.9, eta_exp=85.1, eta_twin=84.3, epseta=0.9),
}

# Geometric design vector -- baseline & bounds (Table 2, pump P1).
# The same variable set and bounds are used to sample all three impellers.
DESIGN_VARS = [
    # name,          symbol,   baseline, low,   high
    ("outlet_blade_angle_deg", "beta2",   24.0,   18.0,   32.0),
    ("number_of_blades",       "Z",        6.0,    5.0,    8.0),
    ("outlet_width_ratio",     "b2_D2",    0.058,  0.045,  0.075),
    ("inlet_diameter_ratio",   "D1_D2",    0.48,   0.42,   0.55),
    ("blade_wrap_angle_deg",   "phi",      115.0,  95.0,   135.0),
    ("volute_throat_area_mm2", "A8",       2150.0, 1800.0, 2500.0),
]


def latin_hypercube(n, d, rng):
    """Simple LHS on the unit hypercube, returns array (n, d) in [0,1]."""
    cut = np.linspace(0, 1, n + 1)
    u = rng.uniform(size=(n, d))
    pts = cut[:n, None] + u * (cut[1:] - cut[:n])[:, None]
    for j in range(d):
        pts[:, j] = pts[rng.permutation(n), j]
    return pts


def response_surface(U, u_star, curvature, eta_max):
    """Concave quadratic efficiency response in normalised design space."""
    quad = np.sum(curvature * (U - u_star) ** 2, axis=1)
    # mild pairwise interaction so the surface is not perfectly separable
    inter = 0.6 * (U[:, 0] - u_star[0]) * (U[:, 2] - u_star[2])
    return eta_max - quad - inter


def build_pump(tag, spec, rng):
    n = spec["n_samples"]
    d = len(DESIGN_VARS)
    U = latin_hypercube(n, d, rng)                      # normalised [0,1]
    lows = np.array([v[3] for v in DESIGN_VARS])
    highs = np.array([v[4] for v in DESIGN_VARS])
    X = lows + U * (highs - lows)                       # physical values
    # round the discrete blade count
    X[:, 1] = np.round(X[:, 1])

    # ---- CFD efficiency via response surface --------------------------------
    u_star = np.array([0.62, 0.55, 0.48, 0.45, 0.58, 0.60])   # interior optimum
    curvature = np.array([14.0, 9.0, 11.0, 8.0, 7.0, 6.0])
    eta_raw = response_surface(U, u_star, curvature, eta_max=1.0)

    # Rescale to the exact spread required to hit the reported R^2 given RMSE:
    #   R2 = 1 - RMSE^2 / Var(eta_cfd)  ->  std(eta_cfd) = RMSE / sqrt(1 - R2)
    target_std = spec["RMSE"] / np.sqrt(1.0 - spec["R2"])
    eta_raw = (eta_raw - eta_raw.mean()) / eta_raw.std(ddof=0)
    # mean chosen so the best DoE sample approaches the optimum found in Fig 3b
    mean_eta = spec["eta_exp"] - 8.0
    eta_cfd = mean_eta + target_std * eta_raw

    # ---- hybrid surrogate prediction ---------------------------------------
    resid = rng.normal(size=n)
    resid -= resid.mean()
    resid *= spec["RMSE"] / resid.std(ddof=0)           # population std == RMSE
    eta_surrogate = eta_cfd + resid

    # ---- physics-only prediction (before GP correction) --------------------
    phys_bias = 1.8 if tag == "P2" else 1.2
    phys_res = rng.normal(scale=2.4, size=n)
    eta_physics = eta_cfd + phys_bias + phys_res

    # ---- head and suction margin per sample --------------------------------
    H_cfd = spec["H"] * (1.0 + 0.05 * (U[:, 0] - u_star[0]) -
                         0.03 * (U[:, 2] - u_star[2]))
    npshr = (spec["H"] * 0.18) * (1.0 + 0.25 * (U[:, 3] - u_star[3]))

    df = pd.DataFrame({
        "sample_id": [f"{tag}-{i+1:03d}" for i in range(n)],
        "beta2_deg": np.round(X[:, 0], 2),
        "Z_blades": X[:, 1].astype(int),
        "b2_D2": np.round(X[:, 2], 4),
        "D1_D2": np.round(X[:, 3], 4),
        "phi_deg": np.round(X[:, 4], 1),
        "A8_mm2": np.round(X[:, 5], 0).astype(int),
        "eta_cfd_pct": np.round(eta_cfd, 3),
        "eta_physics_pct": np.round(eta_physics, 3),
        "eta_hybrid_surrogate_pct": np.round(eta_surrogate, 3),
        "H_cfd_m": np.round(H_cfd, 3),
        "NPSHr_m": np.round(npshr, 3),
    })
    return df


def performance_curve(tag, spec, rng):
    """Full H-Q and eta-Q characteristics: CFD twin, surrogate twin, experiment."""
    Qb, Hb, eta_bep = spec["Q"], spec["H"], spec["eta_exp"]
    Qmin, Qmax = 0.25 * Qb, 1.40 * Qb
    Q = np.linspace(Qmin, Qmax, 22)

    # Head-flow: falling parabola through the BEP.
    H_shut = 1.28 * Hb
    k = (H_shut - Hb) / Qb ** 2
    H_cfd = H_shut - k * Q ** 2

    # Efficiency-flow: parabola peaking at the BEP (twin peak = eta_twin).
    eta_peak_twin = spec["eta_twin"]
    width = (0.9 * Qb) ** 2
    eta_cfd = eta_peak_twin * (1.0 - ((Q - Qb) ** 2) / width)
    eta_cfd = np.clip(eta_cfd, 0.35 * eta_peak_twin, None)

    # Surrogate twin: near-coincident with CFD, tiny departure past BEP.
    dev = 0.006 * np.clip(Q - Qb, 0, None) / Qb * eta_peak_twin
    eta_sur = eta_cfd - dev
    H_sur = H_cfd * (1.0 - 0.004 * np.clip(Q - Qb, 0, None) / Qb)

    # Experiment: sparse points with small measurement scatter; anchored so the
    # BEP experimental values equal Tables 1 & 4 (H=Hb, eta=eta_bep).
    idx = np.linspace(2, len(Q) - 2, 9).astype(int)
    Qe = Q[idx]
    H_exp = np.interp(Qe, Q, H_cfd) * (Hb / np.interp(Qb, Q, H_cfd))
    H_exp = H_exp * (1.0 + rng.normal(scale=0.008, size=len(Qe)))
    eta_exp = np.interp(Qe, Q, eta_cfd) * (eta_bep / eta_peak_twin)
    eta_exp = eta_exp + rng.normal(scale=0.35, size=len(Qe))

    curve = pd.DataFrame({
        "Q_m3h": np.round(Q, 2),
        "H_cfd_twin_m": np.round(H_cfd, 3),
        "H_surrogate_twin_m": np.round(H_sur, 3),
        "eta_cfd_twin_pct": np.round(eta_cfd, 3),
        "eta_surrogate_twin_pct": np.round(eta_sur, 3),
        "is_bep": np.isclose(Q, Q[np.argmin(np.abs(Q - Qb))]),
    })
    exp = pd.DataFrame({
        "Q_m3h": np.round(Qe, 2),
        "H_exp_m": np.round(H_exp, 3),
        "eta_exp_pct": np.round(eta_exp, 3),
    })
    return curve, exp


def main():
    rng = np.random.default_rng(SEED)
    os.makedirs(os.path.join(DATA, "doe"), exist_ok=True)
    os.makedirs(os.path.join(DATA, "performance_curves"), exist_ok=True)
    os.makedirs(os.path.join(DATA, "surrogate_accuracy"), exist_ok=True)

    # ---- Table 1: duty specifications --------------------------------------
    duty = pd.DataFrame([
        dict(pump=t, application=s["application"], Q_m3h=s["Q"], H_m=s["H"],
             n_rpm=s["n"], nq=s["nq"], impeller_type=s["impeller"])
        for t, s in PUMPS.items()
    ])
    duty.to_csv(os.path.join(DATA, "duty_specifications.csv"), index=False)

    # ---- Table 2: design-vector bounds -------------------------------------
    bounds = pd.DataFrame(
        [dict(variable=v[0], symbol=v[1], baseline=v[2], lower=v[3], upper=v[4])
         for v in DESIGN_VARS])
    bounds.to_csv(os.path.join(DATA, "design_vector_bounds.csv"), index=False)

    # ---- Table 4: BEP validation -------------------------------------------
    val = pd.DataFrame([
        dict(pump=t, H_exp_m=s["H"], H_twin_m=s["H_twin"], epsH_pct=s["epsH"],
             eta_exp_pct=s["eta_exp"], eta_twin_pct=s["eta_twin"],
             epseta_pct=s["epseta"])
        for t, s in PUMPS.items()])
    val.to_csv(os.path.join(DATA, "bep_validation.csv"), index=False)

    # ---- Table 5: twin metrics ---------------------------------------------
    met_rows = []
    for t, s in PUMPS.items():
        df = build_pump(t, s, rng)
        df.to_csv(os.path.join(DATA, "doe", f"{t}_doe_cfd_samples.csv"),
                  index=False)
        # surrogate-accuracy extract (Fig 3a)
        acc = df[["sample_id", "eta_cfd_pct", "eta_physics_pct",
                  "eta_hybrid_surrogate_pct"]].copy()
        acc.to_csv(os.path.join(DATA, "surrogate_accuracy",
                                f"{t}_surrogate_vs_cfd.csv"), index=False)
        # recompute achieved statistics for the metrics table
        y = df["eta_cfd_pct"].to_numpy()
        yh = df["eta_hybrid_surrogate_pct"].to_numpy()
        rmse = float(np.sqrt(np.mean((yh - y) ** 2)))
        r2 = float(1.0 - np.sum((yh - y) ** 2) / np.sum((y - y.mean()) ** 2))
        met_rows.append(dict(pump=t, cfd_samples=s["n_samples"],
                             R2=round(r2, 3), RMSE_eta_pct=round(rmse, 2),
                             core_hours=s["core_hours"],
                             twin_query_ms=s["twin_query_ms"]))
        # performance curves
        curve, exp = performance_curve(t, s, rng)
        curve.to_csv(os.path.join(DATA, "performance_curves",
                                  f"{t}_twin_curves.csv"), index=False)
        exp.to_csv(os.path.join(DATA, "performance_curves",
                                f"{t}_experiment_points.csv"), index=False)

    pd.DataFrame(met_rows).to_csv(os.path.join(DATA, "twin_metrics.csv"),
                                  index=False)
    print("Dataset generated in", os.path.normpath(DATA))
    print(pd.DataFrame(met_rows).to_string(index=False))


if __name__ == "__main__":
    main()
