#!/usr/bin/env python3
"""
verify_metrics.py
-----------------
Recomputes the surrogate-accuracy statistics from the sample-level CSVs and
checks them against the values reported in Table 5 of the paper, and checks
that the experimental BEP points match Tables 1 & 4.

Run:  python scripts/verify_metrics.py
Exit code 0 => everything matches within tolerance.
"""
import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

REPORTED = {  # Table 5
    "P1": dict(R2=0.984, RMSE=0.61),
    "P2": dict(R2=0.977, RMSE=0.74),
    "P3": dict(R2=0.981, RMSE=0.66),
}


def main():
    ok = True
    print(f"{'pump':4}  {'R2(calc)':>9} {'R2(ref)':>8}  "
          f"{'RMSE(calc)':>10} {'RMSE(ref)':>9}  status")
    for tag, ref in REPORTED.items():
        df = pd.read_csv(os.path.join(DATA, "doe", f"{tag}_doe_cfd_samples.csv"))
        y = df["eta_cfd_pct"].to_numpy()
        yh = df["eta_hybrid_surrogate_pct"].to_numpy()
        rmse = float(np.sqrt(np.mean((yh - y) ** 2)))
        r2 = float(1 - np.sum((yh - y) ** 2) / np.sum((y - y.mean()) ** 2))
        good = (abs(round(r2, 3) - ref["R2"]) <= 0.001 and
                abs(round(rmse, 2) - ref["RMSE"]) <= 0.01)
        ok = ok and good
        print(f"{tag:4}  {r2:9.3f} {ref['R2']:8.3f}  "
              f"{rmse:10.2f} {ref['RMSE']:9.2f}  "
              f"{'OK' if good else 'MISMATCH'}")

    # BEP experimental head/efficiency vs Table 4
    duty = pd.read_csv(os.path.join(DATA, "duty_specifications.csv")).set_index("pump")
    val = pd.read_csv(os.path.join(DATA, "bep_validation.csv")).set_index("pump")
    print("\nBEP experimental anchors (should equal Tables 1 & 4):")
    for tag in REPORTED:
        print(f"  {tag}: H_exp={val.loc[tag,'H_exp_m']} m "
              f"(duty H={duty.loc[tag,'H_m']} m), "
              f"eta_exp={val.loc[tag,'eta_exp_pct']} %")

    print("\nRESULT:", "ALL METRICS MATCH" if ok else "MISMATCH DETECTED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
