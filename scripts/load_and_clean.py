import pandas as pd
import os

# 1) Load OWID COVID-19 CSV
url = "https://catalog.ourworldindata.org/garden/covid/latest/compact/compact.csv"
df = pd.read_csv(url, low_memory=False)
print(f" Downloaded {len(df)} rows, {len(df.columns)} columns")
print("Columns available:", list(df.columns)[:20])

# 2) Save raw copy
os.makedirs("data/raw", exist_ok=True)
raw_path = "data/raw/owid_covid_raw.csv"
df.to_csv(raw_path, index=False)
print(f"Raw data saved to {raw_path}")

# 3) Filter for UK
uk_df = df[df["country"] == "United Kingdom"].copy()
if uk_df.empty:
    print(" No UK data found!")
    exit(1)

# 4) Keep columns for insight
cols = [
    "date", "total_cases", "new_cases", "total_deaths", "new_deaths",
    "total_vaccinations", "new_vaccinations",
    "people_vaccinated", "people_fully_vaccinated", "population"
]
cols_present = [c for c in cols if c in uk_df.columns]
uk_df = uk_df[cols_present]

# 5) Clean date column and sort
uk_df["date"] = pd.to_datetime(uk_df["date"], errors="coerce")
uk_df = uk_df.sort_values("date")
uk_df = uk_df[uk_df["date"].notna()]


# 6) Check missing values
daily_cols = ["new_cases", "new_deaths", "new_vaccinations"]
cum_cols = ["total_cases", "total_deaths", "total_vaccinations",
            "people_vaccinated", "people_fully_vaccinated"]

# Just check missing values
print("Missing values (daily counts):")
print(uk_df[daily_cols].isna().sum())
print("Missing values (cumulative counts):")
print(uk_df[cum_cols].isna().sum())


# 7) Save cleaned CSV
os.makedirs("data/clean", exist_ok=True)
clean_path = "data/clean/uk_covid_clean.csv"
uk_df.to_csv(clean_path, index=False)
print(f" Cleaned UK data saved to {clean_path}")
print(uk_df.head())
