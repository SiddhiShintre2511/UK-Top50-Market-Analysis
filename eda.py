import pandas as pd
import matplotlib.pyplot as plt

DATA = "data/Atlantic_United_Kingdom.csv"

df = pd.read_csv(DATA)
df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

print("\nDAILY TOP-50 VALIDATION")
daily_counts = df.groupby("date").size()
print("Dates with more than 50 rows:")
print(daily_counts[daily_counts > 50])

print("\nDuplicate date-position records:")
print(df.duplicated(subset=["date", "position"]).sum())

# Keep one record per date + rank for downstream analysis.
df = (
    df.sort_values(["date", "position"])
      .drop_duplicates(subset=["date", "position"], keep="first")
      .reset_index(drop=True)
)

df["duration_min"] = df["duration_ms"] / 60000
df["is_collaboration"] = df["artist"].str.contains(r"\s[&]\s|\sfeat\.?\s|\swith\s|,", case=False, regex=True)

print("Dataset shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isna().sum())

print("\nDate range:")
print(df["date"].min(), "to", df["date"].max())

print("\nDaily entry counts:")
print(df.groupby("date").size().describe())

print("\nAlbum type distribution:")
print(df["album_type"].value_counts())

print("\nExplicit share:")
print(df["is_explicit"].value_counts(normalize=True))

print("\nCollaboration share:")
print(df["is_collaboration"].value_counts(normalize=True))

print("\nTop 20 artists:")
print(df["artist"].value_counts().head(20))

print("\nTop 20 songs by average position:")
print(
    df.groupby(["song", "artist"], as_index=False)
      .agg(Appearances=("position", "count"),
           Avg_Position=("position", "mean"),
           Avg_Popularity=("popularity", "mean"))
      .sort_values(["Avg_Position", "Appearances"])
      .head(20)
)

# Basic chart
daily = df.groupby("date").size()
daily.plot(figsize=(12, 4), title="Daily UK Top 50 Entry Count")
plt.ylabel("Rows")
plt.tight_layout()
plt.show()
