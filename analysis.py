import pandas as pd
import numpy as np

DATA = "data/Atlantic_United_Kingdom.csv"

def load_data():
    df = pd.read_csv(DATA)
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    # A valid daily Top 50 should have one row per date + position.
    # The supplied file contains duplicate ranks on 01-03-2025.
    df = (
        df.sort_values(["date", "position"])
          .drop_duplicates(subset=["date", "position"], keep="first")
          .reset_index(drop=True)
    )

    df["duration_min"] = df["duration_ms"] / 60000

    # Collaboration rule. Adjust if your source uses another convention.
    pattern = r"\s[&]\s|\sfeat\.?\s|\swith\s|,"
    df["is_collaboration"] = df["artist"].str.contains(
        pattern, case=False, regex=True, na=False
    )
    df["track_type"] = np.where(
        df["is_collaboration"], "Collaboration", "Solo"
    )

    # Approximate number of credited artists.
    df["artist_count"] = (
        df["artist"].str.count(r"\s[&]\s")
        + df["artist"].str.count(r"\sfeat\.?\s")
        + df["artist"].str.count(r"\swith\s")
        + df["artist"].str.count(",")
        + 1
    )

    df["rank_group"] = pd.cut(
        df["position"],
        bins=[0, 10, 25, 50],
        labels=["Top 10", "11–25", "26–50"]
    )

    df["popularity_bucket"] = pd.cut(
        df["popularity"],
        bins=[-1, 40, 60, 80, 100],
        labels=["Low", "Medium", "High", "Very High"]
    )

    df["duration_bucket"] = pd.cut(
        df["duration_min"],
        bins=[0, 2.5, 3.5, 5, 100],
        labels=["Short (<2.5m)", "Medium (2.5–3.5m)",
                "Long (3.5–5m)", "Very Long (>5m)"]
    )
    return df

def market_kpis(df):
    total_entries = len(df)
    unique_artists = df["artist"].nunique()
    unique_songs = df["song"].nunique()

    artist_appearances = df["artist"].value_counts()
    top5_share = artist_appearances.head(5).sum() / total_entries

    # Herfindahl-style concentration index based on artist appearances.
    shares = artist_appearances / total_entries
    hhi = (shares ** 2).sum()

    return {
        "total_entries": total_entries,
        "unique_artists": unique_artists,
        "unique_songs": unique_songs,
        "diversity_score": unique_artists / total_entries,
        "top5_artist_share": top5_share,
        "artist_concentration_hhi": hhi,
        "collaboration_ratio": df["is_collaboration"].mean(),
        "explicit_share": df["is_explicit"].mean(),
        "single_ratio": (df["album_type"].str.lower() == "single").mean(),
        "avg_duration_min": df["duration_min"].mean(),
        "avg_popularity": df["popularity"].mean()
    }

def artist_leaderboard(df):
    out = (
        df.groupby("artist")
        .agg(
            Appearances=("song", "size"),
            Unique_Songs=("song", "nunique"),
            Avg_Position=("position", "mean"),
            Best_Position=("position", "min"),
            Avg_Popularity=("popularity", "mean"),
            Collaboration_Appearances=("is_collaboration", "sum")
        )
        .reset_index()
    )
    out["Appearance_Share"] = out["Appearances"] / len(df)
    return out.sort_values(
        ["Appearances", "Avg_Position"],
        ascending=[False, True]
    )

def daily_kpis(df):
    return (
        df.groupby("date")
        .agg(
            Entries=("song", "size"),
            Unique_Artists=("artist", "nunique"),
            Collaboration_Ratio=("is_collaboration", "mean"),
            Explicit_Share=("is_explicit", "mean"),
            Avg_Popularity=("popularity", "mean"),
            Avg_Duration=("duration_min", "mean")
        )
        .reset_index()
    )

def collaboration_summary(df):
    return (
        df.groupby(["rank_group", "track_type"], observed=False)
        .agg(
            Tracks=("song", "size"),
            Avg_Popularity=("popularity", "mean"),
            Avg_Position=("position", "mean"),
            Avg_Duration=("duration_min", "mean")
        )
        .reset_index()
    )

def explicit_summary(df):
    return (
        df.groupby(["rank_group", "is_explicit"], observed=False)
        .agg(
            Tracks=("song", "size"),
            Avg_Popularity=("popularity", "mean"),
            Avg_Position=("position", "mean")
        )
        .reset_index()
    )

def album_summary(df):
    return (
        df.groupby("album_type", dropna=False)
        .agg(
            Tracks=("song", "size"),
            Avg_Popularity=("popularity", "mean"),
            Avg_Position=("position", "mean"),
            Avg_Album_Size=("total_tracks", "mean")
        )
        .reset_index()
    )

if __name__ == "__main__":
    df = load_data()
    print("\nMARKET KPIs")
    for k, v in market_kpis(df).items():
        print(f"{k}: {v:.4f}" if isinstance(v, float) else f"{k}: {v}")

    print("\nTOP ARTISTS")
    print(artist_leaderboard(df).head(20).to_string(index=False))

    print("\nCOLLABORATION SUMMARY")
    print(collaboration_summary(df).to_string(index=False))
