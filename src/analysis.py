"""
CovidScope — COVID-19 Data Visualization & Analysis
---------------------------------------------------
Load, clean, analyse and visualise the project CSV datasets.
Produces a rich set of charts in the visualizations/ folder.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import seaborn as sns

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "visualizations"

# Consistent visual style
sns.set_theme(style="whitegrid", palette="colorblind", font_scale=1.05)
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#cbd5e1",
    "axes.labelcolor": "#0f172a",
    "xtick.color": "#475569",
    "ytick.color": "#475569",
    "text.color": "#0f172a",
    "axes.titleweight": "bold",
    "axes.titlesize": 14,
    "axes.labelsize": 11,
    "legend.frameon": True,
    "legend.fancybox": True,
    "figure.dpi": 120,
})


# ---------------------------------------------------------------------------
# Data loading & cleaning
# ---------------------------------------------------------------------------
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the three source CSVs and parse dates."""
    cases = pd.read_csv(DATA_DIR / "covid_cases.csv", parse_dates=["date"])
    deaths = pd.read_csv(DATA_DIR / "covid_deaths.csv", parse_dates=["date"])
    vaccinations = pd.read_csv(
        DATA_DIR / "covid_vaccinations.csv", parse_dates=["date"]
    )
    return cases, deaths, vaccinations


def clean_and_merge(
    cases: pd.DataFrame,
    deaths: pd.DataFrame,
    vaccinations: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge the three tables, clean missing values, sort chronologically
    and create useful derived columns.
    """
    # Standardise column names & merge on date + country
    df = (
        cases.merge(deaths, on=["date", "country"], how="outer")
        .merge(vaccinations, on=["date", "country"], how="outer")
        .sort_values(["country", "date"])
        .reset_index(drop=True)
    )

    # Fill missing numeric values with 0 (sample data is complete, but safe)
    numeric_cols = ["cases", "deaths", "people_vaccinated_pct"]
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # Remove any accidental duplicates
    df = df.drop_duplicates(subset=["date", "country"])

    # Derived metrics (per country, ordered by date)
    df["new_cases"] = df.groupby("country")["cases"].diff().fillna(df["cases"])
    df["new_deaths"] = df.groupby("country")["deaths"].diff().fillna(df["deaths"])

    # Rolling averages (window=3 because sample has monthly points)
    df["cases_ma"] = (
        df.groupby("country")["cases"]
        .transform(lambda s: s.rolling(window=3, min_periods=1).mean())
    )
    df["deaths_ma"] = (
        df.groupby("country")["deaths"]
        .transform(lambda s: s.rolling(window=3, min_periods=1).mean())
    )

    # Simple case-fatality rate (deaths / cases * 100) – avoid division by zero
    df["cfr"] = np.where(
        df["cases"] > 0,
        (df["deaths"] / df["cases"]) * 100,
        0.0,
    )

    return df


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------
def country_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Latest snapshot + totals per country."""
    latest = (
        df.sort_values("date")
        .groupby("country", as_index=False)
        .last()
        [["country", "date", "cases", "deaths", "people_vaccinated_pct", "cfr"]]
    )
    totals = (
        df.groupby("country", as_index=False)
        .agg(
            total_cases=("cases", "sum"),
            total_deaths=("deaths", "sum"),
            peak_cases=("cases", "max"),
            peak_deaths=("deaths", "max"),
        )
    )
    summary = latest.merge(totals, on="country")
    summary = summary.sort_values("total_cases", ascending=False).reset_index(drop=True)
    summary["rank"] = summary.index + 1
    return summary


def detect_peaks(df: pd.DataFrame, value_col: str = "cases", top_n: int = 3) -> pd.DataFrame:
    """Return the top-N peak months per country for the chosen metric."""
    peaks = (
        df.loc[df.groupby("country")[value_col].idxmax()]
        [["country", "date", value_col]]
        .rename(columns={value_col: "peak_value"})
        .sort_values("peak_value", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    return peaks


# ---------------------------------------------------------------------------
# Chart helpers
# ---------------------------------------------------------------------------
def save_chart(filename: str) -> None:
    """Save current figure and close it."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close()


def style_date_axis(ax) -> None:
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")


# ---------------------------------------------------------------------------
# Visualisations
# ---------------------------------------------------------------------------
def plot_cases_trend(df: pd.DataFrame) -> None:
    """Line chart – reported cases over time by country."""
    fig, ax = plt.subplots(figsize=(11, 5.5))
    sns.lineplot(
        data=df, x="date", y="cases", hue="country",
        marker="o", linewidth=2.2, markersize=7, ax=ax
    )
    ax.set_title("COVID-19 Reported Cases Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cases")
    style_date_axis(ax)
    ax.legend(title="Country", loc="upper left", framealpha=0.95)
    save_chart("cases_trend.png")


def plot_deaths_by_country(df: pd.DataFrame) -> None:
    """Bar chart – total deaths per country."""
    totals = df.groupby("country", as_index=False)["deaths"].sum()
    totals = totals.sort_values("deaths", ascending=False)

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(
        data=totals, x="country", y="deaths",
        hue="country", palette="Reds_r", legend=False, ax=ax
    )
    ax.set_title("Total Reported COVID-19 Deaths by Country")
    ax.set_xlabel("Country")
    ax.set_ylabel("Total Deaths")
    for i, row in totals.reset_index(drop=True).iterrows():
        ax.text(i, row["deaths"] + 80, f"{int(row['deaths']):,}", ha="center", fontsize=9)
    save_chart("deaths_by_country.png")


def plot_vaccination_progress(df: pd.DataFrame) -> None:
    """Line chart – % people vaccinated over time."""
    fig, ax = plt.subplots(figsize=(11, 5.5))
    sns.lineplot(
        data=df, x="date", y="people_vaccinated_pct", hue="country",
        marker="o", linewidth=2.2, markersize=7, ax=ax
    )
    ax.set_title("Vaccination Progress (% of Population)")
    ax.set_xlabel("Date")
    ax.set_ylabel("People Vaccinated (%)")
    ax.set_ylim(0, 70)
    style_date_axis(ax)
    ax.legend(title="Country", loc="upper left", framealpha=0.95)
    save_chart("vaccination_progress.png")


def plot_country_comparison(df: pd.DataFrame) -> None:
    """Bar chart – latest reported cases by country."""
    latest = (
        df.sort_values("date")
        .groupby("country", as_index=False)
        .last()
        .sort_values("cases", ascending=False)
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(
        data=latest, x="country", y="cases",
        hue="country", palette="Blues_r", legend=False, ax=ax
    )
    ax.set_title("Country Comparison – Latest Reported Cases")
    ax.set_xlabel("Country")
    ax.set_ylabel("Cases")
    max_val = latest["cases"].max()
    for i, row in latest.reset_index(drop=True).iterrows():
        ax.text(i, row["cases"] + max_val * 0.02,
                f"{int(row['cases']):,}", ha="center", fontsize=9)
    save_chart("country_comparison.png")


def plot_new_cases_trend(df: pd.DataFrame) -> None:
    """Line chart – month-over-month change in cases (new cases)."""
    fig, ax = plt.subplots(figsize=(11, 5.5))
    sns.lineplot(
        data=df, x="date", y="new_cases", hue="country",
        marker="o", linewidth=2.0, markersize=6, ax=ax
    )
    ax.axhline(0, color="#94a3b8", linestyle="--", linewidth=1)
    ax.set_title("New Cases Trend (Month-over-Month Change)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Change in Cases")
    style_date_axis(ax)
    ax.legend(title="Country", loc="best", framealpha=0.95)
    save_chart("new_cases_trend.png")


def plot_deaths_vs_cases(df: pd.DataFrame) -> None:
    """Scatter + regression – relationship between cases and deaths."""
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.scatterplot(
        data=df, x="cases", y="deaths", hue="country",
        s=90, alpha=0.85, ax=ax
    )
    sns.regplot(
        data=df, x="cases", y="deaths",
        scatter=False, color="#64748b",
        line_kws={"linewidth": 1.5, "linestyle": "--"}, ax=ax
    )
    ax.set_title("Deaths vs Cases (All Observations)")
    ax.set_xlabel("Cases")
    ax.set_ylabel("Deaths")
    ax.legend(title="Country", loc="upper left", framealpha=0.95)
    save_chart("deaths_vs_cases.png")


def plot_cfr_by_country(df: pd.DataFrame) -> None:
    """Bar chart – average case-fatality rate per country."""
    cfr = (
        df.groupby("country", as_index=False)["cfr"]
        .mean()
        .sort_values("cfr", ascending=False)
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(
        data=cfr, x="country", y="cfr",
        hue="country", palette="Oranges_r", legend=False, ax=ax
    )
    ax.set_title("Average Case-Fatality Rate (CFR) by Country")
    ax.set_xlabel("Country")
    ax.set_ylabel("CFR (%)")
    for i, row in cfr.reset_index(drop=True).iterrows():
        ax.text(i, row["cfr"] + 0.05, f"{row['cfr']:.2f}%", ha="center", fontsize=9)
    save_chart("cfr_by_country.png")


def plot_cases_by_country_facet(df: pd.DataFrame) -> None:
    """Faceted line charts – cases trajectory per country."""
    g = sns.relplot(
        data=df, x="date", y="cases",
        col="country", col_wrap=2,
        kind="line", marker="o",
        height=3.2, aspect=1.4,
        color="#0f766e", linewidth=2
    )
    g.set_titles("{col_name}")
    g.set_axis_labels("Date", "Cases")
    g.fig.suptitle("Cases Trajectory by Country", y=1.02, fontsize=14, fontweight="bold")
    for ax in g.axes.flat:
        style_date_axis(ax)
    g.fig.tight_layout()
    g.savefig(OUTPUT_DIR / "cases_by_country_facet.png", dpi=160, bbox_inches="tight")
    plt.close()


def plot_heatmap_correlation(df: pd.DataFrame) -> None:
    """Correlation heatmap of key numeric metrics."""
    numeric = df[["cases", "deaths", "people_vaccinated_pct", "new_cases", "cfr"]].corr()

    fig, ax = plt.subplots(figsize=(8, 6.5))
    sns.heatmap(
        numeric, annot=True, fmt=".2f", cmap="YlGnBu",
        vmin=-1, vmax=1, square=True, linewidths=0.5,
        cbar_kws={"shrink": 0.8}, ax=ax
    )
    ax.set_title("Correlation Between Key Metrics")
    save_chart("correlation_heatmap.png")


def plot_ranking_table(summary: pd.DataFrame) -> None:
    """Horizontal bar ranking of countries by total cases."""
    fig, ax = plt.subplots(figsize=(9, 4.5))
    data = summary.sort_values("total_cases")
    colors = sns.color_palette("viridis", n_colors=len(data))
    ax.barh(data["country"], data["total_cases"], color=colors)
    ax.set_title("Country Ranking by Total Reported Cases")
    ax.set_xlabel("Total Cases")
    ax.set_ylabel("")
    max_val = data["total_cases"].max()
    for i, (val, rank) in enumerate(zip(data["total_cases"], data["rank"])):
        ax.text(val + max_val * 0.01, i,
                f"#{int(rank)}  {int(val):,}", va="center", fontsize=9)
    save_chart("country_ranking.png")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def generate_visualizations() -> pd.DataFrame:
    """
    Full pipeline: load → clean → analyse → create all charts.
    Returns the cleaned merged DataFrame for further interactive use.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)

    cases, deaths, vaccinations = load_data()
    df = clean_and_merge(cases, deaths, vaccinations)
    summary = country_summary(df)

    # Core charts (original set, improved)
    plot_cases_trend(df)
    plot_deaths_by_country(df)
    plot_vaccination_progress(df)
    plot_country_comparison(df)

    # Additional insightful charts
    plot_new_cases_trend(df)
    plot_deaths_vs_cases(df)
    plot_cfr_by_country(df)
    plot_cases_by_country_facet(df)
    plot_heatmap_correlation(df)
    plot_ranking_table(summary)

    print(f"✓ All charts written to {OUTPUT_DIR}")
    print("\nCountry summary (latest snapshot + totals):")
    print(summary.to_string(index=False))

    peaks = detect_peaks(df, "cases")
    print("\nPeak case months:")
    print(peaks.to_string(index=False))

    return df


if __name__ == "__main__":
    generate_visualizations()
