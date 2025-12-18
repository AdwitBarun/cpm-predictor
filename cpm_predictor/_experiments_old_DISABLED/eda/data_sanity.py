import pandas as pd

# Read CSV
df = pd.read_csv("data/data_input.csv")

# Normalize column names
df.columns = (
    df.columns
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

# Dynamically find target
TARGET = [c for c in df.columns if "Del Cpm" in c and "Bidvid" in c][0]
print("Target column:", TARGET)

# 🔥 CRITICAL FIX: convert target to numeric
df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")

# Now numeric operations are safe
print("Total rows:", len(df))
print("NaN CPM rows:", df[TARGET].isna().sum())
print("Negative or zero CPM rows:", (df[TARGET] <= 0).sum())

# Date sanity
df["Start Date_1"] = pd.to_datetime(df["Start Date_1"], errors="coerce")
df["End Date_1"] = pd.to_datetime(df["End Date_1"], errors="coerce")

print(
    "Negative duration rows:",
    ((df["End Date_1"] - df["Start Date_1"]).dt.days < 0).sum()
)
