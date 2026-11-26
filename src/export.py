"""
Export small aggregated tables for the dashboard.

Run from the project folder:
    python -m src.export

Writes data/summary.csv: users and conversions per group, segment and
value of (ads bucket, weekday, hour). The dashboard needs only this file,
not the original 588k-row CSV.
"""

import numpy as np
import pandas as pd

from src.data import load_data

ADS_BINS = [0, 5, 10, 20, 50, 100, np.inf]
ADS_LABELS = ["1-5", "6-10", "11-20", "21-50", "51-100", "100+"]


def main():
    df = load_data()
    df["ads_bucket"] = pd.cut(df["total_ads"], bins=ADS_BINS, labels=ADS_LABELS)

    parts = []
    for column, name in [("ads_bucket", "Ads seen"), ("most_ads_day", "Weekday"),
                         ("most_ads_hour", "Hour")]:
        grouped = (df.groupby([column, "group"], observed=True)["converted"]
                     .agg(users="size", conversions="sum").reset_index())
        grouped = grouped.rename(columns={column: "value"})
        grouped["value"] = grouped["value"].astype(str)
        grouped.insert(0, "segment", name)
        parts.append(grouped)

    summary = pd.concat(parts, ignore_index=True)
    summary.to_csv("data/summary.csv", index=False)
    print(f"Saved {len(summary)} rows to data/summary.csv")


if __name__ == "__main__":
    main()