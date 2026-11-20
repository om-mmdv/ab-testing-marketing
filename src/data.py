"""
Data loading for the marketing A/B test project.

Every other script gets its data from load_data(),
so the loading and cleaning logic lives in one place.
"""

import os

import pandas as pd

DATA_PATH = os.path.join("data", "marketing_AB.csv")


def load_data():
    """
    Read the CSV file and return a clean pandas DataFrame.

    Cleaning steps:
      - drop the useless index column "Unnamed: 0"
      - give columns simple snake_case names
      - make sure "converted" is a real boolean
    """
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"File not found: {DATA_PATH}\n"
            "Download marketing_AB.csv from Kaggle "
            "(search: 'Marketing A/B Testing') and put it into the data/ folder."
        )

    df = pd.read_csv(DATA_PATH)

    df = df.drop(columns=["Unnamed: 0"], errors="ignore")
    df = df.rename(columns={
        "user id": "user_id",
        "test group": "group",
        "total ads": "total_ads",
        "most ads day": "most_ads_day",
        "most ads hour": "most_ads_hour",
    })
    df["converted"] = df["converted"].astype(bool)

    return df


if __name__ == "__main__":
    # Quick self-check: run `python -m src.data`
    df = load_data()
    print(f"Shape: {df.shape}")
    print(df.head())
    print("\nUsers per group:")
    print(df["group"].value_counts())