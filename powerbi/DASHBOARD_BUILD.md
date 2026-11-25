# Power BI report build

This folder contains the Power Query import template and DAX measures for the report described in the resume. A `.pbix` file is not included because this workspace is on macOS and Power BI Desktop requires Windows. The supplied data is at `Desktop/Projects/dataset/`; its `parquet/` folder contains the compressed yearly files, while `csv/` contains the source CSVs.

## Prepare the data

1. In Power BI Desktop on Windows, choose **Get data > Folder** and connect to the directory containing the Parquet files. Filter to `.parquet`, then use **Combine & Transform**. Power Query's Parquet connector supports local files; see [Microsoft's Parquet connector guide](https://learn.microsoft.com/en-us/power-query/connectors/parquet).
2. Exclude the partial 2026 file to match the 2001–2025 analysis. If you use the CSV source instead, run `scripts/clean_data.py --input-dir <csv-folder> --output-dir <cleaned-folder>` first.
3. Rename the imported table to `Prices` and load it. The supplied Parquet files contain the source price fields; add `Year` and `Month` from `Arrival_Date` in Power Query. Use the keyword mapping in `Power_Query_M.m` to create the optional `Category` field.
4. Create a calendar table with `Calendar = CALENDAR(MIN(Prices[Arrival_Date]), MAX(Prices[Arrival_Date]))`, mark it as the date table, and relate `Calendar[Date]` to `Prices[Arrival_Date]`.
5. Add measures from `Measures.dax` (create them in a `_Measures` table if desired).

## Page 1 — Price trends

- Slicers: Year, Commodity, Category, State.
- Cards: Average Modal Price, Observation Count, Year-over-Year Change %.
- Line chart: Calendar month on the X axis; Average Modal Price on the Y axis; Commodity as legend.
- Column chart: Average Modal Price by Commodity, filtered by selected year.
- Matrix: Commodity rows, Year columns, Average Modal Price values.

## Page 2 — Market comparison

- Slicers: Commodity, State, Year.
- Bar chart: Average Modal Price by Market, sorted descending; Top N filter for the leading markets.
- Map (optional): State or District with Average Modal Price as the value.
- Detail table: State, District, Market, Commodity, Average Modal Price, Observation Count.
- For the screenshot's tomato view, set Commodity = Tomato and Year = 2024; use High Price Days as a card and Market as the axis.

## Page 3 — Volatility and grade premiums

- Slicers: Year, State, Commodity.
- Bar chart: Price Spread % by District, descending.
- Scatter chart: Average Modal Price versus Price Spread %, with Market as details and Commodity as legend.
- Clustered columns: FAQ Average Price and Medium Average Price by Commodity; add FAQ Premium to tooltip.

## Data caveats

Category labels are assigned by the Power Query keyword rules and can be adjusted. Use both `High Price Observations` and `High Price Days` for tomato threshold reporting: the supplied data has multiple qualifying rows on some market dates, so these measures differ. `High Price Days` counts distinct observed dates and does not fill dates with no records.
