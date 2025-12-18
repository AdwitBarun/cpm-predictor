import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("data/data_input.csv")

TARGET = "Del Cpm/\nBidvid  cpm"

print(df[TARGET].describe())

sns.histplot(df[TARGET], bins=30, kde=True)
plt.title("Delivered CPM Distribution")
plt.show()
num_cols = [
    "Planned Reach 1+",
    "Planned Freq",
    "Planned Budget",
    "Planned Impressions",
    "Pacing Rate",
    "Pacing Amount",
    "Frequency Exposures",
    "TrueView View Frequency Exposures",
    "Partner Revenue Amount",
    "campaign_duration_days"
]

for col in num_cols:
    if col in df.columns:
        sns.scatterplot(x=df[col], y=df[TARGET])
        plt.title(f"{col} vs Delivered CPM")
        plt.show()
cat_cols = [
    "Device", "TG", "Inventory Mode", "Video Ad Format",
    "TrueView Video Ad Formats", "month_range"
]

for col in cat_cols:
    if col in df.columns:
        plt.figure(figsize=(8,4))
        sns.boxplot(x=col, y=TARGET, data=df)
        plt.xticks(rotation=45)
        plt.title(f"Delivered CPM by {col}")
        plt.show()
