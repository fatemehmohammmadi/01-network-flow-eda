"""Generate synthetic NetFlow-like samples for EDA / anomaly demos."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
OUT = Path(__file__).parent / "data" / "sample_flows.csv"


def _benign(n: int) -> pd.DataFrame:
    protocols = RNG.choice(["TCP", "UDP", "ICMP"], size=n, p=[0.7, 0.25, 0.05])
    return pd.DataFrame(
        {
            "src_ip": [f"10.0.{RNG.integers(0, 5)}.{RNG.integers(1, 254)}" for _ in range(n)],
            "dst_ip": [f"192.168.{RNG.integers(0, 10)}.{RNG.integers(1, 254)}" for _ in range(n)],
            "src_port": RNG.integers(1024, 65535, n),
            "dst_port": RNG.choice([80, 443, 53, 22, 445, 3389], size=n, p=[0.35, 0.35, 0.15, 0.05, 0.05, 0.05]),
            "protocol": protocols,
            "bytes": RNG.lognormal(mean=8.5, sigma=0.8, size=n).astype(int),
            "packets": RNG.integers(1, 120, n),
            "duration_ms": RNG.integers(10, 5000, n),
            "label": "benign",
        }
    )


def _anomalous(n: int) -> pd.DataFrame:
    """High-volume / rare-port style outliers."""
    return pd.DataFrame(
        {
            "src_ip": [f"10.0.{RNG.integers(0, 5)}.{RNG.integers(1, 254)}" for _ in range(n)],
            "dst_ip": [f"203.0.113.{RNG.integers(1, 50)}" for _ in range(n)],
            "src_port": RNG.integers(1024, 65535, n),
            "dst_port": RNG.choice([4444, 31337, 6667, 23, 445], size=n),
            "protocol": RNG.choice(["TCP", "UDP"], size=n),
            "bytes": RNG.lognormal(mean=14.0, sigma=0.5, size=n).astype(int),
            "packets": RNG.integers(500, 8000, n),
            "duration_ms": RNG.integers(50, 800, n),
            "label": "anomaly",
        }
    )


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = pd.concat([_benign(900), _anomalous(100)], ignore_index=True)
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    df.insert(0, "flow_id", [f"F{i:05d}" for i in range(len(df))])
    df.to_csv(OUT, index=False)
    print(f"Wrote {len(df)} flows -> {OUT}")


if __name__ == "__main__":
    main()
