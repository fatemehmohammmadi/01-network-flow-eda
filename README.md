# Network Flow EDA & Anomaly Scoring

Small project for poking at NetFlow-style records and finding weird flows with Isolation Forest.

I mostly use this as a starting point when I get a new CSV dump from a lab or a SIEM export. Nothing fancy — just enough EDA to know what the traffic looks like before jumping into supervised models.

## What's in here

| Path | What it does |
|------|----------------|
| `generate_sample_data.py` | Builds a synthetic flow table (benign + planted outliers) |
| `eda_anomaly.py` | Prints basic stats, scores anomalies, writes plots/CSVs |
| `data/sample_flows.csv` | Sample dataset already generated |
| `outputs/` | Results from the last local run |

## Quick start

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python generate_sample_data.py   # optional if data/ already exists
python eda_anomaly.py
```

## How the scoring works

1. Load flows and add a couple derived columns (`bytes_per_packet`, `packets_per_sec`).
2. Encode protocol and feed numeric features into `IsolationForest`.
3. Rank by anomaly score and dump the top rows + a simple plot.

Contamination is fixed at `0.1` so you get a stable demo. On real data you'll want to tune that (or switch to a score threshold from a quiet baseline week).

## Sample results

From the committed run:

- ~1000 flows
- ~10% flagged
- Most planted `anomaly` rows show up in the outlier set (see `outputs/run_summary.json`)

Files worth opening:

- `outputs/top_anomalies.csv`
- `outputs/eda_plots.png`
- `outputs/run_summary.json`

## Notes / limits

- Data is synthetic on purpose. Don't treat the F1-looking overlap as production proof.
- No time-window features yet (rolling rates per `src_ip` help a lot in practice).
- Plots need a normal desktop backend; headless servers may need `Agg`.

## Ideas if you fork this

- Swap the CSV for anonymized NetFlow / Zeek `conn.log` aggregates
- Add per-host rolling stats
- Push top-N outliers into a webhook / Slack alert

## License

MIT
