# 01 — Network Flow EDA & Anomaly Scoring

Exploratory analysis on NetFlow-like traffic and unsupervised anomaly scoring with Isolation Forest.

## Learning goals

- Work with tabular network flow data
- Engineer simple statistical features
- Detect outliers without labels
- Produce SOC-friendly summary artifacts

## Layout

```
01-network-flow-eda/
├── README.md
├── requirements.txt
├── generate_sample_data.py
├── eda_anomaly.py
├── data/sample_flows.csv
└── outputs/                 # sample run artifacts
    ├── top_anomalies.csv
    └── eda_plots.png
```

## Setup & run

```bash
cd 01-network-flow-eda
pip install -r requirements.txt
python generate_sample_data.py
python eda_anomaly.py
```

## Sample run (committed)

| Artifact | Description |
|----------|-------------|
| `outputs/top_anomalies.csv` | Top-20 flows by anomaly score |
| `outputs/eda_plots.png` | Bytes histogram + score boxplot |
| `outputs/run_summary.json` | Shape, outlier count, label overlap |

Expected console highlights: ~1000 flows, ~10% flagged as outliers, strong overlap with synthetic `anomaly` labels.
