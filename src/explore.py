"""
Exploratory data analysis for the marketing A/B test.

Run from the project folder:
    python -m src.explore

Checks data quality, compares the two groups on everything except the
outcome (to see whether the split looks fair), and saves plots to assets/.
"""

import os

import matplotlib.pyplot as plt

from src.data import load_data

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday",
             "Friday", "Saturday", "Sunday"]


def check_quality(df):
    """Print missing values, duplicates and group sizes."""
    print("=== Missing values per column ===")
    print(df.isna().sum())

    print("\n=== Duplicated user ids ===")
    print(df["user_id"].duplicated().sum())

    print("\n=== Group sizes ===")
    sizes = df["group"].value_counts()
    for group, count in sizes.items():
        print(f"  {group:4s} {count:7d} users ({count / len(df) * 100:.1f}%)")


def compare_groups(df):
    """
    Compare the groups on variables that were NOT affected by the ad
    (day, hour, number of ads seen). If the split is fair, they should
    look similar.
    """
    print("\n=== Total ads seen, by group ===")
    print(df.groupby("group")["total_ads"].describe().round(1))

    print("\n=== Share of users per weekday, by group (%) ===")
    days = (df.groupby("group")["most_ads_day"]
              .value_counts(normalize=True).unstack() * 100)
    print(days[DAY_ORDER].round(1))


def plot_group_sizes(df):
    """Bar chart of how many users are in each group."""
    sizes = df["group"].value_counts()
    plt.figure(figsize=(6, 4))
    plt.bar(sizes.index, sizes.values, color=["#4c72b0", "#dd8452"])
    plt.ylabel("Number of users")
    plt.title("Group sizes")
    plt.tight_layout()
    plt.savefig("assets/group_sizes.png", dpi=150)
    plt.close()


def plot_ads_distribution(df):
    """
    Histogram of total ads seen, per group.
    The scale is limited to 200 because a few users saw thousands of ads.
    """
    plt.figure(figsize=(8, 5))
    for group, color in [("ad", "#4c72b0"), ("psa", "#dd8452")]:
        values = df.loc[df["group"] == group, "total_ads"]
        # density=True: show shares instead of counts, since group sizes differ a lot
        plt.hist(values, bins=60, range=(0, 200), density=True,
                 alpha=0.6, label=group, color=color)
    plt.xlabel("Total ads seen (capped at 200 on the plot)")
    plt.ylabel("Share of users")
    plt.title("Ads seen per user, by group")
    plt.legend()
    plt.tight_layout()
    plt.savefig("assets/ads_distribution.png", dpi=150)
    plt.close()


def main():
    os.makedirs("assets", exist_ok=True)
    df = load_data()

    check_quality(df)
    compare_groups(df)
    plot_group_sizes(df)
    plot_ads_distribution(df)

    print("\nPlots saved to assets/")


if __name__ == "__main__":
    main()