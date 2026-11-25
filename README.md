# India Agricultural Commodity Price Analysis

An end-to-end analysis of historical wholesale agricultural prices reported by markets across India. The project combines Python and Jupyter data work, MySQL queries, and an interactive dashboard preview to explore price trends, seasonal movement, regional differences, market volatility, and grade premiums.

## Project overview

The analysis uses yearly market price CSV files from 2001 through 2025. The streaming summary scanned **75,390,478 rows across 25 CSV files**. The partial 2026 file was excluded so comparisons use the same complete year range. Prices are reported in rupees per quintal.

Questions explored include:

- How have prices for major commodities changed over time?
- Which months and commodity groups show stronger year-over-year movement?
- How do prices vary between states, districts, and markets?
- Where are observed price spreads and FAQ-versus-Medium grade premiums largest?
- How do row counts differ from distinct observed market dates for high-price events?

See [analysis_results.md](analysis_results.md) for the data-backed findings, methodology notes, and differences from older saved notebook outputs.

## What is included

- **Jupyter notebooks** — `data_cleaning.ipynb`, `analysis.ipynb`, and `data_visualization.ipynb` document cleaning, analysis, and visual exploration.
- **Python scripts** — chunked CSV cleaning and bounded-memory dataset summarization.
- **SQL** — a MySQL 8 schema and queries for commodity trends, seasonal changes, market comparisons, price spreads, and grade premiums.
- **Dashboard** — `dashboard/index.html` is an interactive snapshot, with compact chart data in `dashboard/data.json` and screenshots in `dashboard/screenshots/`.
- **Power BI materials** — Power Query mapping, DAX measures, and a report build guide are in `powerbi/`. A `.pbix` file is not included; Power BI Desktop is required to build and save that report.

## Data and reproducibility

The source dataset is not included in this repository because it is large. Place the yearly CSV files in a folder such as `dataset/csv/`, or pass your own folder path to the scripts. The scripts select files named by year and the analysis script uses years 2001–2025.

Install the Python dependency used by the scripts:

```bash
python -m pip install pandas
```

Summarize the source data:

```bash
python scripts/analyze_dataset.py \
  --input-dir "/path/to/dataset/csv" \
  --output analysis_summary.json
```

Clean yearly CSV files for downstream use:

```bash
python scripts/clean_data.py \
  --input-dir "/path/to/dataset/csv" \
  --output-dir "/path/to/cleaned-csv"
```

The scripts process files in chunks to limit memory use. The dashboard JSON is a saved aggregate snapshot; rerunning the analysis script creates a new summary file and does not automatically rebuild the dashboard data.

## SQL and Power BI

For MySQL, create the table with `sql/schema.sql`, load cleaned CSV data using the template notes in that file, and run selected analyses from `sql/analysis_queries.sql`.

For Power BI Desktop on Windows, follow `powerbi/DASHBOARD_BUILD.md` to load Parquet or cleaned CSV data, configure the model, and assemble the report pages. The guide covers price trends, market comparisons, volatility, and grade premiums.

## Data notes

- Category assignment is based on keyword rules and may need review for unusual commodity names.
- A qualifying high-price row is not always a distinct market date; the results report both measures where relevant.
- Some extreme regional comparisons come from small samples. Consult the observation counts in `analysis_results.md` before interpreting them.
- Notebook outputs are saved snapshots and may use older counts or assumptions; the results report describes the current dataset-backed calculations.

## Author

**Devanshu Kumar** — [@devanshu1513](https://github.com/devanshu1513)
