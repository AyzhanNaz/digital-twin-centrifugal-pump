#!/usr/bin/env python3
"""
plot_figures.py
---------------
Reproduces the paper's Figure 2 (H-Q / eta-Q characteristics, pump P1) and
Figure 3a (surrogate-twin accuracy against CFD) directly from the CSV data,
as a reproducibility check.  Figures are written to ../figures/.

Run:  python scripts/plot_figures.py
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "..", "figures")
os.makedirs(OUT, exist_ok=True)


def fig2(pump="P1"):
    curve = pd.read_csv(os.path.join(DATA, "performance_curves",
                                     f"{pump}_twin_curves.csv"))
    exp = pd.read_csv(os.path.join(DATA, "performance_curves",
                                   f"{pump}_experiment_points.csv"))
    duty = pd.read_csv(os.path.join(DATA, "duty_specifications.csv")).set_index("pump")
    Qb = duty.loc[pump, "Q_m3h"]

    fig, ax1 = plt.subplots(figsize=(7, 4.5), dpi=150)
    ax2 = ax1.twinx()
    ax1.plot(curve.Q_m3h, curve.H_cfd_twin_m, "-", color="#c0392b",
             label="CFD digital twin (H)")
    ax1.plot(curve.Q_m3h, curve.H_surrogate_twin_m, "--", color="#2e7d5b",
             label="Surrogate twin (H)")
    ax1.plot(exp.Q_m3h, exp.H_exp_m, "o", color="#1f3b5b", label="Experiment (H)")
    ax2.plot(curve.Q_m3h, curve.eta_cfd_twin_pct, "-", color="#e08b7a")
    ax2.plot(curve.Q_m3h, curve.eta_surrogate_twin_pct, "--", color="#8fbf9f")
    ax2.plot(exp.Q_m3h, exp.eta_exp_pct, "s", color="#1f3b5b")
    ax1.axvline(Qb, ls=":", color="grey")
    ax1.set_xlabel("Flow rate  Q  (m$^3$/h)")
    ax1.set_ylabel("Head  H  (m)")
    ax2.set_ylabel("Efficiency  $\\eta$  (%)")
    ax1.set_title(f"Fig. 2 reproduction — pump {pump}")
    ax1.legend(loc="lower left", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"figure2_{pump}.png"))
    plt.close(fig)


def fig3a(pump="P1"):
    acc = pd.read_csv(os.path.join(DATA, "surrogate_accuracy",
                                   f"{pump}_surrogate_vs_cfd.csv"))
    x = acc.eta_cfd_pct.to_numpy()
    y = acc.eta_hybrid_surrogate_pct.to_numpy()
    rmse = np.sqrt(np.mean((y - x) ** 2))
    r2 = 1 - np.sum((y - x) ** 2) / np.sum((x - x.mean()) ** 2)
    lo, hi = min(x.min(), y.min()) - 1, max(x.max(), y.max()) + 1

    fig, ax = plt.subplots(figsize=(5, 5), dpi=150)
    ax.plot([lo, hi], [lo, hi], "-", color="black", lw=1)
    ax.plot([lo, hi], [lo + 1, hi + 1], "--", color="grey", lw=0.8)
    ax.plot([lo, hi], [lo - 1, hi - 1], "--", color="grey", lw=0.8)
    ax.scatter(x, y, s=40, color="#3a9d6e", edgecolor="white", zorder=3)
    ax.text(0.05, 0.9, f"$R^2$ = {r2:.3f}\nRMSE = {rmse:.2f} %",
            transform=ax.transAxes,
            bbox=dict(boxstyle="round", fc="#eaf6ef", ec="#3a9d6e"))
    ax.set_xlabel("CFD efficiency  $\\eta$  (%)")
    ax.set_ylabel("Surrogate efficiency  $\\eta$  (%)")
    ax.set_title(f"Fig. 3a reproduction — pump {pump}")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"figure3a_{pump}.png"))
    plt.close(fig)


if __name__ == "__main__":
    for p in ("P1", "P2", "P3"):
        fig2(p)
        fig3a(p)
    print("Figures written to", os.path.normpath(OUT))
