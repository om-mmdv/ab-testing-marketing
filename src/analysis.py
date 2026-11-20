"""
Main A/B test: does the ad increase the conversion rate?

Run from the project folder:
    python -m src.analysis

Compares conversion in the "ad" (treatment) and "psa" (control) groups
with a two-proportion z-test and a 95% confidence interval.
"""

import os

import matplotlib.pyplot as plt
import numpy as np
from statsmodels.stats.proportion import (
    confint_proportions_2indep,
    proportions_ztest,
)

from src.data import load_data

ALPHA = 0.05  # significance level: p-values below this count as "significant"


def conversion_by_group(df):
    """Return (conversions, users) for the treatment and the control group."""
    ad = df[df["group"] == "ad"]["converted"]
    psa = df[df["group"] == "psa"]["converted"]
    return (ad.sum(), len(ad)), (psa.sum(), len(psa))


def main():
    os.makedirs("assets", exist_ok=True)
    df = load_data()

    (ad_conv, ad_n), (psa_conv, psa_n) = conversion_by_group(df)
    ad_rate, psa_rate = ad_conv / ad_n, psa_conv / psa_n

    print("=== Conversion rates ===")
    print(f"  ad  (treatment): {ad_conv:6d} / {ad_n:6d} = {ad_rate * 100:.3f}%")
    print(f"  psa (control):   {psa_conv:6d} / {psa_n:6d} = {psa_rate * 100:.3f}%")

    # Two-proportion z-test.
    # Null hypothesis: both groups have the same true conversion rate.
    z_stat, p_value = proportions_ztest(
        count=[ad_conv, psa_conv], nobs=[ad_n, psa_n]
    )
    print("\n=== Z-test ===")
    print(f"  z = {z_stat:.2f}, p-value = {p_value:.2e}")
    verdict = "SIGNIFICANT" if p_value < ALPHA else "NOT significant"
    print(f"  At alpha = {ALPHA}: {verdict}")

    # 95% confidence interval for the difference (ad - psa)
    low, high = confint_proportions_2indep(
        ad_conv, ad_n, psa_conv, psa_n, compare="diff", alpha=ALPHA
    )
    diff = ad_rate - psa_rate
    print("\n=== Effect size ===")
    print(f"  Absolute difference: {diff * 100:.3f} percentage points")
    print(f"  95% CI of the difference: [{low * 100:.3f}, {high * 100:.3f}] pp")
    print(f"  Relative lift: {diff / psa_rate * 100:.1f}%")

    # Plot: conversion rates with error bars (95% CI of each group)
    rates = np.array([psa_rate, ad_rate])
    ns = np.array([psa_n, ad_n])
    errors = 1.96 * np.sqrt(rates * (1 - rates) / ns)

    plt.figure(figsize=(6, 5))
    plt.bar(["psa (control)", "ad (treatment)"], rates * 100,
            yerr=errors * 100, capsize=8, color=["#dd8452", "#4c72b0"])
    plt.ylabel("Conversion rate, %")
    plt.title("Conversion rate by group (with 95% CI)")
    plt.tight_layout()
    plt.savefig("assets/conversion_by_group.png", dpi=150)
    plt.close()
    print("\nPlot saved to assets/conversion_by_group.png")


if __name__ == "__main__":
    main()