"""
Practical significance and a robustness check.

Run from the project folder:
    python -m src.impact

1. Estimates how many extra purchases the ad produced.
2. Confirms the confidence interval with a bootstrap.
"""

import os

import matplotlib.pyplot as plt
import numpy as np

from src.data import load_data

N_BOOTSTRAP = 5000   # number of resampled "experiments"
RANDOM_SEED = 42     # fixed seed: results are reproducible


def estimate_extra_purchases(ad_rate, psa_rate, ad_n, diff_ci):
    """
    If the ad group had behaved like the control group, it would have
    converted at psa_rate. The difference is the purchases the ad added.
    """
    extra = (ad_rate - psa_rate) * ad_n
    extra_low, extra_high = diff_ci[0] * ad_n, diff_ci[1] * ad_n
    return extra, extra_low, extra_high


def bootstrap_difference(ad, psa, n_iter=N_BOOTSTRAP, seed=RANDOM_SEED):
    """
    Bootstrap the difference in conversion rates (ad - psa).

    Each iteration draws a random sample (with replacement) of the same
    size from each group and computes the difference. Since conversions are
    0/1, the number of purchases in a resample follows a binomial distribution,
    which lets us do this very fast without looping over users.
    """
    rng = np.random.default_rng(seed)
    ad_rate, psa_rate = ad.mean(), psa.mean()
    ad_sim = rng.binomial(len(ad), ad_rate, size=n_iter) / len(ad)
    psa_sim = rng.binomial(len(psa), psa_rate, size=n_iter) / len(psa)
    return ad_sim - psa_sim


def main():
    os.makedirs("assets", exist_ok=True)
    df = load_data()

    ad = df.loc[df["group"] == "ad", "converted"].astype(int).to_numpy()
    psa = df.loc[df["group"] == "psa", "converted"].astype(int).to_numpy()

    diffs = bootstrap_difference(ad, psa)
    low, high = np.percentile(diffs, [2.5, 97.5])

    print("=== Bootstrap check ===")
    print(f"  Mean difference:          {diffs.mean() * 100:.3f} pp")
    print(f"  95% bootstrap interval:   [{low * 100:.3f}, {high * 100:.3f}] pp")
    print(f"  Share of resamples with difference > 0: {(diffs > 0).mean() * 100:.2f}%")

    extra, extra_low, extra_high = estimate_extra_purchases(
        ad.mean(), psa.mean(), len(ad), (low, high)
    )
    print("\n=== Practical impact ===")
    print(f"  Extra purchases attributed to the ad: about {extra:,.0f}")
    print(f"  (plausible range: {extra_low:,.0f} to {extra_high:,.0f})")
    print(f"  Out of {int(ad.sum()):,} purchases in the ad group, "
          f"{extra / ad.sum() * 100:.0f}% are incremental")
    print(f"  Cost per extra purchase = ad budget / {extra:,.0f}")

    plt.figure(figsize=(8, 5))
    plt.hist(diffs * 100, bins=60, color="#4c72b0", edgecolor="white")
    plt.axvline(0, color="red", linewidth=1.5, label="No effect")
    plt.axvline(low * 100, color="black", linestyle="--", label="95% interval")
    plt.axvline(high * 100, color="black", linestyle="--")
    plt.xlabel("Difference in conversion rate (ad - psa), percentage points")
    plt.ylabel("Number of bootstrap samples")
    plt.title("Bootstrap distribution of the effect")
    plt.legend()
    plt.tight_layout()
    plt.savefig("assets/bootstrap_difference.png", dpi=150)
    plt.close()
    print("\nPlot saved to assets/bootstrap_difference.png")


if __name__ == "__main__":
    main()