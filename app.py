import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from analysis import (
    load_data, market_kpis, artist_leaderboard,
    daily_kpis, collaboration_summary,
    explicit_summary, album_summary
)

st.set_page_config(
    page_title="UK Top 50 Market Intelligence",
    page_icon="🎵",
    layout="wide"
)

@st.cache_data
def get_data():
    return load_data()

df = get_data()

st.sidebar.title("🎵 UK Top 50")
st.sidebar.caption("Market Structure, Artist Diversity & Content Localization")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

artists = sorted(df["artist"].dropna().unique())
artist_filter = st.sidebar.multiselect(
    "Artist filter",
    artists,
    default=[]
)

track_filter = st.sidebar.radio(
    "Track type",
    ["All", "Solo", "Collaboration"]
)

album_filter = st.sidebar.multiselect(
    "Album type",
    sorted(df["album_type"].dropna().unique()),
    default=[]
)

mask = (
    (df["date"].dt.date >= start_date) &
    (df["date"].dt.date <= end_date)
)

if artist_filter:
    mask &= df["artist"].isin(artist_filter)

if track_filter != "All":
    mask &= df["track_type"].eq(track_filter)

if album_filter:
    mask &= df["album_type"].isin(album_filter)

filtered = df.loc[mask].copy()

st.title("🇬🇧 United Kingdom Top 50 Playlist Market Intelligence")
st.caption(
    "Artist diversity, market concentration, collaboration, explicit content, "
    "release format and track-duration analysis"
)

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

k = market_kpis(filtered)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Entries", f"{k['total_entries']:,}")
c2.metric("Unique Artists", f"{k['unique_artists']:,}")
c3.metric("Top 5 Artist Share", f"{k['top5_artist_share']:.1%}")
c4.metric("Collaboration Ratio", f"{k['collaboration_ratio']:.1%}")
c5.metric("Explicit Share", f"{k['explicit_share']:.1%}")

tabs = st.tabs([
    "📊 Overview",
    "🏆 Artist Dominance",
    "🤝 Collaborations",
    "🔞 Explicit Content",
    "💿 Album & Release",
    "⏱ Duration & Popularity",
    "🌍 Localization"
])

with tabs[0]:
    st.subheader("Market Overview")

    daily = daily_kpis(filtered)

    col1, col2 = st.columns(2)

    with col1:
        st.write("Unique artists by date")
        st.line_chart(daily.set_index("date")["Unique_Artists"])

    with col2:
        st.write("Collaboration ratio by date")
        st.line_chart(daily.set_index("date")["Collaboration_Ratio"])

    st.subheader("Market KPI Details")
    kpi_df = pd.DataFrame({
        "KPI": [
            "Artist Concentration HHI",
            "Diversity Score",
            "Top 5 Artist Share",
            "Collaboration Ratio",
            "Explicit Content Share",
            "Single Ratio",
            "Average Duration (min)",
            "Average Popularity"
        ],
        "Value": [
            k["artist_concentration_hhi"],
            k["diversity_score"],
            k["top5_artist_share"],
            k["collaboration_ratio"],
            k["explicit_share"],
            k["single_ratio"],
            k["avg_duration_min"],
            k["avg_popularity"]
        ]
    })
    st.dataframe(kpi_df, use_container_width=True)

with tabs[1]:
    st.subheader("🏆 Artist Dominance Leaderboard")

    leaderboard = artist_leaderboard(filtered)
    st.dataframe(
        leaderboard.head(50).style.format({
            "Avg_Position": "{:.2f}",
            "Avg_Popularity": "{:.2f}",
            "Appearance_Share": "{:.2%}"
        }),
        use_container_width=True
    )

    top_n = st.slider("Number of artists to display", 5, 30, 15)
    chart = leaderboard.head(top_n).set_index("artist")["Appearances"]
    st.bar_chart(chart)

with tabs[2]:
    st.subheader("🤝 Collaboration Analysis")

    collab = collaboration_summary(filtered)
    st.dataframe(
        collab.style.format({
            "Avg_Popularity": "{:.2f}",
            "Avg_Position": "{:.2f}",
            "Avg_Duration": "{:.2f}"
        }),
        use_container_width=True
    )

    ratio = filtered.groupby("rank_group", observed=False)["is_collaboration"].mean()
    st.write("Collaboration ratio by rank group")
    st.bar_chart(ratio)

    st.info(
        "The collaboration network is represented by credited artist names. "
        "For a true network graph, use the Network Graph section below after "
        "ensuring the artist delimiter matches your source data."
    )

    # Simple network edge table
    collab_rows = filtered[filtered["is_collaboration"]].copy()
    edges = []
    for _, row in collab_rows.iterrows():
        parts = [p.strip() for p in str(row["artist"]).replace(" feat. ", "&").split("&")]
        parts = [p for p in parts if p]
        if len(parts) >= 2:
            for i in range(len(parts)):
                for j in range(i + 1, len(parts)):
                    edges.append((parts[i], parts[j]))

    if edges:
        edge_df = (
            pd.DataFrame(edges, columns=["Artist_1", "Artist_2"])
            .value_counts()
            .reset_index(name="Collaboration_Count")
            .sort_values("Collaboration_Count", ascending=False)
        )
        st.subheader("Top Collaboration Pairs")
        st.dataframe(edge_df.head(30), use_container_width=True)

with tabs[3]:
    st.subheader("🔞 Explicit vs Clean Content")

    exp = explicit_summary(filtered)
    st.dataframe(exp, use_container_width=True)

    explicit_ratio_rank = filtered.groupby(
        "rank_group", observed=False
    )["is_explicit"].mean()

    st.write("Explicit content share by rank group")
    st.bar_chart(explicit_ratio_rank)

    st.write("Explicit vs clean average popularity")
    pop = filtered.groupby("is_explicit")["popularity"].mean()
    pop.index = ["Clean" if x is False else "Explicit" for x in pop.index]
    st.bar_chart(pop)

with tabs[4]:
    st.subheader("💿 Album & Release Strategy")

    alb = album_summary(filtered)
    st.dataframe(
        alb.style.format({
            "Avg_Popularity": "{:.2f}",
            "Avg_Position": "{:.2f}",
            "Avg_Album_Size": "{:.2f}"
        }),
        use_container_width=True
    )

    st.write("Single vs album presence")
    st.bar_chart(filtered["album_type"].value_counts())

    st.write("Album size vs popularity")
    album_scatter = (
        filtered.groupby("total_tracks", as_index=False)
        .agg(Avg_Popularity=("popularity", "mean"),
             Tracks=("song", "size"))
        .sort_values("total_tracks")
    )
    st.line_chart(
        album_scatter.set_index("total_tracks")["Avg_Popularity"]
    )

with tabs[5]:
    st.subheader("⏱ Track Duration & Popularity")

    c1, c2 = st.columns(2)

    with c1:
        st.write("Duration distribution")
        st.bar_chart(filtered["duration_bucket"].value_counts())

    with c2:
        st.write("Popularity buckets")
        st.bar_chart(filtered["popularity_bucket"].value_counts())

    duration_summary = (
        filtered.groupby("duration_bucket", observed=False)
        .agg(
            Tracks=("song", "size"),
            Avg_Popularity=("popularity", "mean"),
            Avg_Position=("position", "mean")
        )
        .reset_index()
    )

    st.dataframe(
        duration_summary.style.format({
            "Avg_Popularity": "{:.2f}",
            "Avg_Position": "{:.2f}"
        }),
        use_container_width=True
    )

with tabs[6]:
    st.subheader("🌍 UK Content Localization")

    st.warning(
        "The supplied dataset does not contain artist nationality/country. "
        "Therefore this dashboard does not infer UK vs international artists. "
        "Add a separate artist-country mapping to perform a defensible localization analysis."
    )

    st.write("Available localization proxies:")
    st.markdown("""
    - Collaboration prevalence
    - Explicit-content share
    - Release-format mix
    - Artist concentration
    - Content variety
    - Rank distribution
    """)

    st.subheader("Optional Artist Country Mapping")

    mapping_file = Path("data/artist_country_mapping.csv")
    if mapping_file.exists():
        mapping = pd.read_csv(mapping_file)
        st.dataframe(mapping.head(100), use_container_width=True)

        merged = filtered.merge(mapping, on="artist", how="left")
        known = merged.dropna(subset=["country"])

        if len(known):
            country_share = known["country"].value_counts(normalize=True)
            st.write("Artist-country share among mapped entries")
            st.bar_chart(country_share)
    else:
        st.code(
            "artist,country\n"
            "Artist Name,United Kingdom\n"
            "Another Artist,United States\n"
        )
        st.caption(
            "Create data/artist_country_mapping.csv with verified artist-country "
            "information if you need a UK vs international comparison."
        )

st.divider()
st.caption(
    "Source: supplied Atlantic United Kingdom Top 50 dataset. "
    "Artist nationality is not inferred from artist names."
)
