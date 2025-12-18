import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
def clean_cpm(series):
    return (
        series
        .astype(str)
        .str.replace(",", "", regex=False)   # remove commas
        .str.replace("₹", "", regex=False)   # remove currency
        .str.replace("#REF!", "", regex=False)
        .str.replace("NA", "", regex=False)
        .str.strip()
        .pipe(pd.to_numeric, errors="coerce")
    )

df = pd.read_csv("data/data_input.csv")

df.columns = (
    df.columns
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

TARGET = [c for c in df.columns if "Del Cpm" in c and "Bidvid" in c][0]
df[TARGET] = clean_cpm(df[TARGET])
print(df[TARGET].describe())

sns.histplot(df[TARGET].dropna(), bins=50, kde=True)
plt.title("Delivered CPM Distribution")
plt.show()
