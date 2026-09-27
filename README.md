# United Kingdom Top 50 Playlist Market Structure, Artist Diversity & Content Localization Analysis

## Project objective

Analyze the UK Top 50 playlist structure for:
- Artist dominance and diversity
- Artist concentration
- Collaboration behavior
- Explicit vs clean content
- Single vs album release structure
- Album size
- Track duration
- Popularity
- UK localization indicators

## Dataset

The supplied CSV contains 27,800 rows and 10 columns:
`date, position, song, artist, popularity, duration_ms, album_type, total_tracks, is_explicit, album_cover_url`

There are no missing values in the supplied file.



## Data validation

The source file contains one duplicated daily Top 50 snapshot:
`01-03-2025` contains 100 rows, with duplicate date-position combinations.

The analysis pipeline validates the Top 50 structure and keeps one record per
`date + position` before calculating KPIs. This prevents duplicated ranks from
inflating artist appearances, explicit-content share, collaboration ratio and
other metrics.

## Important localization limitation

The dataset does not include artist nationality/country. The project therefore does NOT infer whether an artist is British from their name.

For a defensible UK-vs-international analysis, create:

`data/artist_country_mapping.csv`

Example:

```csv
artist,country
Loreen,Sweden
David Kushner,United States
```

Use verified sources to populate the mapping.

## Project structure

```text
UK_Top50_Market_Analysis/
│
├── data/
│   └── Atlantic_United_Kingdom.csv
│
├── analysis.py
├── eda.py
├── app.py
├── requirements.txt
└── README.md
```

## Step 1 — Create environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

## Step 2 — Install packages

```bash
pip install -r requirements.txt
```

## Step 3 — Run EDA

```bash
python eda.py
```

## Step 4 — Run Streamlit

```bash
streamlit run app.py
```

## Main dashboard modules

### Overview
- Entries
- Unique artists
- Top-5 artist share
- Collaboration ratio
- Explicit share
- Daily diversity

### Artist Dominance
- Artist leaderboard
- Appearance count
- Unique songs
- Average position
- Best position
- Popularity
- Appearance share

### Collaboration
- Solo vs collaboration
- Collaboration ratio by rank group
- Top collaboration pairs

### Explicit Content
- Explicit share
- Explicit distribution by rank
- Popularity comparison

### Album & Release
- Single vs album
- Album size
- Popularity by album size

### Duration & Popularity
- Duration buckets
- Popularity buckets
- Average position/popularity by duration

### Localization
- Uses verified artist-country mapping if supplied
- Does not guess nationality

## KPI formulas

### Diversity Score

`Unique Artists / Total Playlist Entries`

### Top-5 Artist Share

`Appearances of top 5 artists / Total playlist entries`

### Artist Concentration HHI

`sum(artist appearance share²)`

Higher HHI means appearances are more concentrated among fewer artists. This is a descriptive concentration measure, not a judgment about market quality.

### Collaboration Ratio

`Collaborative entries / Total entries`

### Explicit Content Share

`Explicit entries / Total entries`

### Single Ratio

`Single entries / Total entries`

## Research paper recommendation

Structure the paper as:
1. Abstract
2. Introduction
3. Problem Statement
4. Objectives
5. Dataset Description
6. Data Cleaning
7. Feature Engineering
8. Exploratory Data Analysis
9. Artist Diversity Analysis
10. Collaboration Analysis
11. Explicit Content Analysis
12. Album/Release Analysis
13. Duration & Popularity Analysis
14. Localization Analysis
15. KPI Framework
16. Findings
17. Business Implications
18. Limitations
19. Conclusion
20. References

## Caution about interpretation

This dataset describes playlist/chart presence, not all UK listeners or the entire UK music market. Observed associations should not be presented as causal effects.

The project also cannot establish UK-vs-international artist shares without a separate verified country mapping.
