"""
Segment analysis: when does the ad work best?

Run from the project folder:
    python -m src.segments

Computes conversion for both groups inside segments (number of ads seen,
weekday, hour) and plots the uplift (ad - psa) with 95% confidence intervals.

Caution: many segments means many comparisons, so some differences can
appear by chance. Treat the results as hypotheses, not proof.
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.data import load_data

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday",
             "Friday", "Saturday", "Sunday"]

# Buckets for the number of ads seen
ADS_BINS = [0, 5, 10, 20, 50, 100, np.inf]
ADS_LABELS = ["1-5", "6-10", "11-20", "21-50", "51-100", "100+"]


def segment_uplift(df, column):
    """
    For each value of `column`, compute conversion in both groups, the
    uplift (ad - psa, in percentage points) and an approximate 95% CI.
    """
    rows = []
    for value, part in df.groupby(column, observed=True):
        ad = part.loc[part["group"] == "ad", "converted"]
        psa = part.loc[part["group"] == "psa", "converted"]
        if len(psa) == 0:
            continue
        p_ad, p_psa = ad.mean(), psa.mean()
        # Standard error of a difference between two proportions
        se = np.sqrt(p_ad * (1 - p_ad) / len(ad) + p_psa * (1 - p_psa) / len(psa))
        rows.append({
            column: value,
            "n_ad": len(ad),
            "n_psa": len(psa),
            "conv_ad_%": p_ad * 100,
            "conv_psa_%": p_psa * 100,
            "uplift_pp": (p_ad - p_psa) * 100,
            "ci_pp": 1.96 * se * 100,
        })
    return pd.DataFrame(rows)


def plot_uplift(table, column, title, filename):
    """Bar chart of the uplift per segment, with 95% CI whiskers."""
    plt.figure(figsize=(9, 5))
    labels = table[column].astype(str)
    plt.bar(labels, table["uplift_pp"], yerr=table["ci_pp"],
            capsize=4, color="#4c72b0")
    plt.axhline(0, color="red", linewidth=1)
    plt.ylabel("Uplift (ad - psa), percentage points")
    plt.title(title)
    plt.xticks(rotation=45 if len(table) > 8 else 0)
    plt.tight_layout()
    plt.savefig(f"assets/{filename}", dpi=150)
    plt.close()


def main():
    os.makedirs("assets", exist_ok=True)
    df = load_data()

    df["ads_bucket"] = pd.cut(df["total_ads"], bins=ADS_BINS,
                              labels=ADS_LABELS, right=True)
    df["most_ads_day"] = pd.Categorical(df["most_ads_day"],
                                        categories=DAY_ORDER, ordered=True)

    analyses = [
        ("ads_bucket", "Uplift by number of ads seen", "uplift_by_ads.png"),
        ("most_ads_day", "Uplift by weekday", "uplift_by_day.png"),
        ("most_ads_hour", "Uplift by hour of day", "uplift_by_hour.png"),
    ]

    for column, title, filename in analyses:
        table = segment_uplift(df, column)
        print(f"\n=== {title} ===")
        print(table.round(2).to_string(index=False))
        plot_uplift(table, column, title, filename)

    print("\nPlots saved to assets/")


if __name__ == "__main__":
    main()