# CovidScope

**COVID-19 Data Visualization & Analysis**

CovidScope turns raw COVID-19 datasets into clear, actionable visual insights.  
It demonstrates the full data-analysis workflow — cleaning, feature engineering, exploratory analysis and professional visualisation — using Python, Pandas, NumPy, Matplotlib and Seaborn.

> *Understand the Data. Protect Your Health.*

---

## Features

- **Data cleaning & merging** of cases, deaths and vaccination records
- **Derived metrics**
  - Month-over-month new cases / new deaths
  - 3-period rolling averages
  - Case-fatality rate (CFR)
- **Country ranking** and peak detection
- **10 high-quality charts** covering trends, comparisons, correlations and rankings
- Reusable analysis module + interactive Jupyter notebook

---

## Project Structure

```
CovidScope/
├── data/
│   ├── covid_cases.csv
│   ├── covid_deaths.csv
│   └── covid_vaccinations.csv
├── notebooks/
│   └── covid_analysis.ipynb
├── src/
│   └── analysis.py
├── visualizations/          ← generated charts
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Quick Start

```bash
# 1. Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate all visualisations
python src/analysis.py
```

Charts are written to the `visualizations/` folder.

### Interactive exploration

```bash
jupyter notebook notebooks/covid_analysis.ipynb
```

---

## Generated Visualisations

| Chart | Description |
|-------|-------------|
| `cases_trend.png` | Reported cases over time by country |
| `deaths_by_country.png` | Total deaths ranking |
| `vaccination_progress.png` | % of population vaccinated |
| `country_comparison.png` | Latest reported cases comparison |
| `new_cases_trend.png` | Month-over-month change in cases |
| `deaths_vs_cases.png` | Scatter + trend of deaths vs cases |
| `cfr_by_country.png` | Average case-fatality rate |
| `cases_by_country_facet.png` | Individual country trajectories |
| `correlation_heatmap.png` | Correlation matrix of key metrics |
| `country_ranking.png` | Horizontal ranking by total cases |

---

## Key Analysis Questions Answered

- Which countries recorded the highest number of cases and deaths?
- How did infections and vaccinations evolve over time?
- What is the relationship between cases and deaths?
- During which periods did new cases rise or fall most sharply?
- How do case-fatality rates compare across countries?
- Which metrics are most strongly correlated?

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core language |
| Pandas | Data cleaning, merging, aggregation |
| NumPy | Numerical calculations & safe division |
| Matplotlib | Chart rendering & fine control |
| Seaborn | Statistical visualisations & theming |
| Jupyter | Interactive exploration |

---

## Sample Data

The included CSVs contain monthly observations (Jan–Jun 2021) for four countries:

- India
- United States
- Brazil
- United Kingdom

Metrics: reported cases, deaths, and % of people vaccinated.

The analysis pipeline is designed to scale to larger real-world datasets (e.g. Our World in Data) with minimal changes.

---

## Extending the Project

Ideas for further work:

- Add population data → compute infection rate & vaccination coverage per capita
- Replace sample CSVs with live OWID or JHU CSSE feeds
- Build a Flask / Streamlit dashboard on top of `analysis.py`
- Add recovery data and recovery-rate calculations
- Implement automated peak / anomaly detection with more sophisticated methods

---

## License

Educational / demonstration project. Feel free to adapt for learning or portfolios.

---

## Web UI

A clean, responsive frontend is included in the `web/` folder.

```
web/
├── index.html          ← Landing / dashboard
├── analytics.html      ← All 10 charts
├── countries.html      ← Country explorer cards
├── about.html
├── css/style.css
└── js/main.js
```

### View the UI

Simply open `web/index.html` in any modern browser (or serve the folder with a local server).

The design uses the medical-tech teal palette, card-based layout, and works on desktop, tablet and mobile.
