# India Agricultural Commodity Price Analysis

Python and Jupyter analysis of historical wholesale agricultural prices in India. This package now includes the original notebooks, MySQL analysis queries, and materials for building the interactive Power BI report described in the resume.

## What is included

- `data_cleaning.ipynb`, `analysis.ipynb`, `data_visualization.ipynb`: original notebooks with saved outputs.
- `scripts/clean_data.py`: chunked CSV cleaning script with input/output folder options.
- `scripts/analyze_dataset.py`: bounded-memory analysis of yearly CSV files.
- `analysis_results.md`: results calculated from the supplied local dataset.
- `sql/schema.sql`, `sql/analysis_queries.sql`: MySQL 8 table setup and queries for long-term trends, monthly changes, regional spreads, grade premiums, and high-price markets.
- `powerbi/`: Power Query import template, DAX measures, and report layout guide.
- `dashboard/index.html`: interactive preview populated from the supplied dataset; `dashboard/data.json` holds its compact result data.
- `dashboard/screenshots/`: PNG captures of the price trends, market comparison, and volatility & quality dashboard views.

## Get the data

The large source data stays outside this project package. The supplied folder is `Desktop/Projects/dataset/`, with yearly files in `csv/` and `parquet/`. The analysis used 25 CSVs covering 2001–2025 (75,390,478 rows); the partial 2026 CSV was excluded. To rerun the scan:

```bash
python scripts/analyze_dataset.py --input-dir "/path/to/Projects/dataset/csv" --output analysis_summary.json
```

If you need cleaned CSVs for SQL or Power BI, run `python scripts/clean_data.py --input-dir "/path/to/Projects/dataset/csv" --output-dir "/path/to/cleaned-csv"`. See `powerbi/DASHBOARD_BUILD.md` for data loading and the report pages.

## SQL setup

Run `sql/schema.sql` in MySQL 8, load each cleaned CSV into `commodity_prices` using its commented `LOAD DATA` template, and run sections from `sql/analysis_queries.sql`.

## Evidence and limits

The notebooks demonstrate Python-based cleaning, exploratory analysis, and saved Matplotlib/Seaborn charts. SQL analysis queries and Power BI setup assets are included. A `.pbix` file is not included: this environment is macOS, while Power BI Desktop requires Windows. The HTML dashboard is an interactive snapshot based on the supplied full dataset; `dashboard/data.json` contains its compact source data. Rerunning `scripts/analyze_dataset.py` creates a fresh aggregate JSON for updating the dashboard. See `analysis_results.md` for methodology, sample-size notes, and differences between current data results and saved notebook outputs.
