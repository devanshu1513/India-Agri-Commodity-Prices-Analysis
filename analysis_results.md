# Dataset-backed analysis results

## Data scanned

- **Rows scanned:** 75,390,478 across 25 yearly CSVs.
- **Coverage used:** 2001–2025. The folder also contains a 2026 file; it was excluded to match the project period.
- **Missing core fields:** no rows were skipped for missing date, commodity, or modal price in the streaming analysis. This does not imply every optional field is complete.
- The supplied folder also contains yearly Parquet files; this scan used the CSVs so the results are reproducible without adding a Parquet reader.

## Results

### Price trends

| Commodity | 2015 average (₹/quintal) | 2025 average (₹/quintal) | Change (₹) | Change (%) |
|---|---:|---:|---:|---:|
| Cardamoms | 75,053.35 | 216,851.63 | 141,798.28 | 188.9% |
| Almond (Badam) | 6,134.71 | 93,116.85 | 86,982.14 | 1,417.9% |
| Tube Flower | 6,400.00 | 64,473.69 | 58,073.69 | 907.4% |
| Kakada | 4,250.00 | 45,112.96 | 40,862.96 | 961.5% |
| Jasmine | 27,222.67 | 57,528.04 | 30,305.36 | 111.3% |

Rice average modal price rose **25.5%** from 2020 to 2024 (₹2,773.30 to ₹3,481.27). Wheat rose **37.5%** (₹1,860.52 to ₹2,558.25).

### Seasonal changes

Using keyword-based commodity categories and the mean monthly modal price, the highest average year-over-year change months were:

| Rank | Month | Average YoY change | Category/year-month comparisons |
|---:|---|---:|---:|
| 1 | April | 9.80% | 168 |
| 2 | January | 9.77% | 168 |
| 3 | May | 9.41% | 168 |
| 4 | December | 7.82% | 168 |
| 5 | August | 7.76% | 168 |

Category assignment is heuristic; use the same classification rules in the Power BI model when comparing this figure.

### Regional comparisons

**Tomato, 2024, modal price ≥ ₹3,000:**

| State | Market | Qualifying rows | Distinct observed dates |
|---|---|---:|---:|
| Kerala | Kottayam | 345 | 213 |
| Kerala | Kanjirappally | 326 | 322 |
| Kerala | Anchal | 296 | 296 |

The original notebook labels qualifying rows as ‘days’. The supplied 2024 file contains multiple qualifying rows on some market dates; the dashboard shows both counts. For Kottayam specifically, the dataset has 345 qualifying rows across 213 observed dates.

**Other market findings from the supplied files:**

- Highest average Onion modal price by state in 2024: **Andaman and Nicobar**, ₹5,875.00, based on 4 observations.
- Highest average Tomato price by Maharashtra district (2023–2024): **Dharashiv (Usmanabad)**, ₹4,933.33, 54 observations.
- Highest average Potato price by Uttar Pradesh market in 2024: **Sehjanwa**, ₹2,273.20, 231 observations.

### Volatility and grade premium

The raw highest district spread is based on a small sample; a 1,000-observation floor gives a more stable comparison.

| Rank (≥1,000 obs.) | State | District | Average spread / modal price | Observations |
|---:|---|---|---:|---:|
| 1 | Maharashtra | Sholapur | 69.11% | 394,665 |
| 2 | Maharashtra | Kolhapur | 65.44% | 200,757 |
| 3 | Telangana | Hyderabad | 62.21% | 380,048 |
| 4 | Chandigarh | Chandigarh | 58.91% | 38,299 |
| 5 | Tripura | Dhalai | 58.41% | 67,177 |

Raw highest: **South Tripura, Tripura**, 106.99% from 104 observations.

| Commodity | FAQ minus Medium average (₹/quintal) | Varieties compared |
|---|---:|---:|
| Mace | 72,380.99 | 1 |
| Almond (Badam) | 47,742.94 | 1 |
| Pepper ungarbled | 36,269.61 | 1 |
| Cashewnuts | 13,349.05 | 5 |
| Rubber | 12,162.45 | 1 |

## Difference from the saved notebook snapshots

Several saved outputs match the supplied data (for example, the 2020–2024 Rice/Wheat comparison, FAQ premiums, Maharashtra Tomato districts, and Uttar Pradesh Potato market). Some saved output tables are older or use different counting assumptions. The Tomato ‘days’ table counts qualifying rows, not distinct dates; this report separates the measures. The current raw data also ranks high-price Tomato markets differently from the saved notebook’s narrative. Use the figures in this report and dashboard for the supplied dataset.
