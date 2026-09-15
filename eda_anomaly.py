"""EDA + Isolation Forest anomaly scoring on network flows."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder

DATA = Path(__file__).parent / "data" / "sample_flows.csv"
OUT_DIR = Path(__file__).parent / "outputs"


def load_flows() -> pd.DataFrame:
    if not DATA.exists():
        raise SystemExit("Run generate_sample_data.py first.")
    return pd.read_csv(DATA)


def engineer(df: pd.DataFrame) -> pd.DataFrame:
    # cheap ratios that usually separate bulk transfers from chatty scans
    out = df.copy()
    out["bytes_per_packet"] = out["bytes"] / out["packets"].clip(lower=1)
    # clip duration so we don't blow up on 0ms rows from broken exporters
    out["packets_per_sec"] = out["packets"] / (out["duration_ms"] / 1000).clip(lower=0.001)
    return out


def run_eda(df: pd.DataFrame) -> None:
    print("\n=== Shape ===")
    print(df.shape)
    print("\n=== Protocol counts ===")
    print(df["protocol"].value_counts())
    print("\n=== Top destination ports ===")
    print(df["dst_port"].value_counts().head(10))
    print("\n=== Numeric describe ===")
    print(df[["bytes", "packets", "duration_ms", "bytes_per_packet"]].describe().round(2))


def score_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    features = ["bytes", "packets", "duration_ms", "src_port", "dst_port", "bytes_per_packet", "packets_per_sec"]
    X = df[features].copy()
    X["protocol_enc"] = LabelEncoder().fit_transform(df["protocol"])

    # contamination=0.1 is just a demo default; on real traffic I'd threshold on score instead
    model = IsolationForest(n_estimators=200, contamination=0.1, random_state=42)
    df = df.copy()
    df["anomaly_raw"] = model.fit_predict(X)
    # sklearn returns higher = more normal, flip so "big number = weird"
    df["anomaly_score"] = -model.score_samples(X)
    df["is_outlier"] = df["anomaly_raw"] == -1
    return df


def save_reports(df: pd.DataFrame) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    top = df.nlargest(20, "anomaly_score")
    top.to_csv(OUT_DIR / "top_anomalies.csv", index=False)
    print(f"\nSaved top anomalies -> {OUT_DIR / 'top_anomalies.csv'}")

    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    sns.histplot(df["bytes"], bins=40, ax=axes[0], log_scale=True)
    axes[0].set_title("Bytes distribution (log scale)")
    sns.boxplot(data=df, x="is_outlier", y="anomaly_score", ax=axes[1])
    axes[1].set_title("Anomaly score by outlier flag")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "eda_plots.png", dpi=140)
    plt.close(fig)
    print(f"Saved plots -> {OUT_DIR / 'eda_plots.png'}")

    summary = {
        "n_flows": int(len(df)),
        "n_outliers": int(df["is_outlier"].sum()),
        "outlier_rate": round(float(df["is_outlier"].mean()), 4),
        "mean_anomaly_score": round(float(df["anomaly_score"].mean()), 4),
    }
    if "label" in df.columns:
        overlap = pd.crosstab(df["label"], df["is_outlier"])
        print("\n=== Label vs outlier flag ===")
        print(overlap)
        summary["label_vs_outlier"] = {
            str(idx): {str(c): int(overlap.loc[idx, c]) for c in overlap.columns}
            for idx in overlap.index
        }
    (OUT_DIR / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Saved summary -> {OUT_DIR / 'run_summary.json'}")


def main() -> None:
    df = engineer(load_flows())
    run_eda(df)
    scored = score_anomalies(df)
    save_reports(scored)
    print("\nDone.")


if __name__ == "__main__":
    main()
