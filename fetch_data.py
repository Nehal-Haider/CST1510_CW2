
from pathlib import Path

import pandas as pd
import requests


# API settings
URL = "https://disease.sh/v3/covid-19/countries"
PARAMS = {}

# Data settings
RECORDS_KEY = None

RENAME = {}

KEEP = [
    "country",
    "continent",
    "cases",
    "deaths",
    "recovered",
    "tests",
    "population",
    "active"
]

MUST_HAVE = ["cases", "continent"]

RAW_FILE = Path("DATA/raw.csv")


def get_data(url, params):
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as error:
        print("Could not get the data:", error)
        return None


def make_table(data, records_key):
    if data is None:
        return pd.DataFrame()

    records = data if records_key is None else data.get(records_key, [])

    return pd.json_normalize(records, sep="_")


def tidy_data(df):
    df = df.rename(columns=RENAME)

    # Keep only the required columns that exist
    columns = [column for column in KEEP if column in df.columns]
    df = df[columns]

    # Treat empty strings as missing values
    df[MUST_HAVE] = df[MUST_HAVE].replace(r'^\s*$', pd.NA, regex=True)

    # Remove rows with missing required values
    df = df.dropna(subset=MUST_HAVE)

    return df


def save_data(df, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Data saved to {path}")


if __name__ == "__main__":
    data = get_data(URL, PARAMS)

    df = make_table(data, RECORDS_KEY)

    df = tidy_data(df)

    print(df.head())
    print("Number of rows:", len(df))
    print("Number of columns:", len(df.columns))

    save_data(df, RAW_FILE)
