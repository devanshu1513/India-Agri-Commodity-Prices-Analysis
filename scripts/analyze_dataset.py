from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
SOURCE = PROJECT_DIR / "dataset" / "csv"
DEST = PROJECT_DIR / "analysis_summary.json"
CHUNK_SIZE = 200_000
MIN_YEAR, MAX_YEAR = 2001, 2025


def category_for(value: str) -> str:
    s = str(value).strip().lower()
    rules = {
        "Pulses": ("gram", "dal", "moong", "arhar", "urd", "masur", "lentil", "peas", "lobia", "moath"),
        "Grains": ("wheat", "rice", "maize", "jowar", "bajra", "barley", "ragi", "millet", "paddy", "soji"),
        "Spices": ("ginger", "coriander", "turmeric", "pepper", "jeera", "cummin", "chill", "soanf", "methi", "ajwan", "cinamon", "clove", "cardamom", "bay leaf"),
        "Vegetables": ("onion", "potato", "brinjal", "cauliflower", "tomato", "garlic", "cabbage", "capsicum", "carrot", "gourd", "pumpkin", "beans", "cucumber", "raddish", "spinach", "yam", "beetroot", "ladies finger", "lemon", "lime", "drumstick"),
        "Fruits": ("grape", "orange", "pineapple", "apple", "banana", "mango", "papaya", "pomegranate", "guava", "watermelon"),
        "Oilseeds": ("groundnut", "mustard", "soyabean", "soybean", "sesame", "sunflower", "linseed", "castor"),
    }
    for label, words in rules.items():
        if any(word in s for word in words):
            return label
    return "Other"


def merge(store, frame, keys, value):
    grouped = frame.groupby(keys, dropna=False)[value].agg(["sum", "count"])
    for key, row in grouped.iterrows():
        k = key if isinstance(key, tuple) else (key,)
        acc = store[k]
        acc[0] += float(row["sum"])
        acc[1] += int(row["count"])


def rows_from(store, key_names, output_names):
    out = []
    for key, (total, count) in store.items():
        row = dict(zip(key_names, key))
        row[output_names[0]] = total / count if count else None
        row[output_names[1]] = count
        out.append(row)
    return out


def main():
    global SOURCE, DEST
    parser = argparse.ArgumentParser(description="Stream and summarize yearly agricultural price CSV files.")
    parser.add_argument("--input-dir", type=Path, default=SOURCE, help="Folder containing yearly CSV files.")
    parser.add_argument("--output", type=Path, default=DEST, help="Path for the JSON aggregate output.")
    args = parser.parse_args()
    SOURCE, DEST = args.input_dir, args.output
    files = sorted(
        (p for p in SOURCE.glob("*.csv") if p.stem.isdigit() and MIN_YEAR <= int(p.stem) <= MAX_YEAR),
        key=lambda p: int(p.stem),
    )
    if not files:
        raise FileNotFoundError(f"No yearly CSV files found in {SOURCE}")

    yearly = defaultdict(lambda: [0.0, 0])
    monthly = defaultdict(lambda: [0.0, 0])
    category_monthly = defaultdict(lambda: [0.0, 0])
    district_spread = defaultdict(lambda: [0.0, 0])
    grade_prices = defaultdict(lambda: [0.0, 0])
    tomato_market_days = {}
    total_rows = 0
    rejected_price_rows = 0

    usecols = ["State", "District", "Market", "Commodity", "Variety", "Grade", "Arrival_Date", "Min_Price", "Max_Price", "Modal_Price"]
    for path in files:
        rows_for_file = 0
        for chunk in pd.read_csv(path, usecols=usecols, chunksize=CHUNK_SIZE, low_memory=False):
            rows_for_file += len(chunk)
            chunk["Arrival_Date"] = pd.to_datetime(chunk["Arrival_Date"], errors="coerce")
            for col in ("Min_Price", "Max_Price", "Modal_Price"):
                chunk[col] = pd.to_numeric(chunk[col], errors="coerce")
            before = len(chunk)
            chunk = chunk.dropna(subset=["Arrival_Date", "Commodity", "Modal_Price"])
            rejected_price_rows += before - len(chunk)
            chunk = chunk[(chunk["Arrival_Date"].dt.year >= MIN_YEAR) & (chunk["Arrival_Date"].dt.year <= MAX_YEAR)]
            if chunk.empty:
                continue
            chunk["Year"] = chunk["Arrival_Date"].dt.year.astype("int16")
            chunk["Month"] = chunk["Arrival_Date"].dt.month.astype("int8")

            merge(yearly, chunk, ["Commodity", "Year"], "Modal_Price")
            merge(monthly, chunk, ["Commodity", "Year", "Month"], "Modal_Price")
            chunk["Category"] = chunk["Commodity"].map(category_for)
            merge(category_monthly, chunk, ["Category", "Year", "Month"], "Modal_Price")

            spread = chunk.dropna(subset=["State", "District", "Min_Price", "Max_Price"])
            spread = spread[(spread["Modal_Price"] > 0) & (spread["Max_Price"] >= spread["Min_Price"])]
            if not spread.empty:
                spread = spread.assign(SpreadPct=100 * (spread["Max_Price"] - spread["Min_Price"]) / spread["Modal_Price"])
                merge(district_spread, spread, ["State", "District"], "SpreadPct")

            grade = chunk[chunk["Grade"].isin(["FAQ", "Medium"])].dropna(subset=["Commodity", "Variety"])
            if not grade.empty:
                merge(grade_prices, grade, ["Commodity", "Variety", "Grade"], "Modal_Price")

            tomato = chunk[(chunk["Commodity"].str.casefold() == "tomato") & (chunk["Year"] == 2024) & (chunk["State"].notna()) & (chunk["Market"].notna())]
            if not tomato.empty:
                daily = tomato.groupby(["State", "Market", "Arrival_Date"])["Modal_Price"].max()
                for (state, market, date), price in daily.items():
                    key = (str(state), str(market), str(date.date()))
                    tomato_market_days[key] = max(tomato_market_days.get(key, float("-inf")), float(price))

        total_rows += rows_for_file
        print(f"Processed {path.name}: {rows_for_file:,} rows", flush=True)

    year_rows = rows_from(yearly, ["Commodity", "Year"], ["avg_modal_price", "observations"])
    monthly_rows = rows_from(monthly, ["Commodity", "Year", "Month"], ["avg_modal_price", "observations"])
    cat_rows = rows_from(category_monthly, ["Category", "Year", "Month"], ["avg_modal_price", "observations"])
    district_rows = rows_from(district_spread, ["State", "District"], ["avg_spread_pct", "observations"])
    grade_rows = rows_from(grade_prices, ["Commodity", "Variety", "Grade"], ["avg_modal_price", "observations"])

    yr_df = pd.DataFrame(year_rows)
    year_increases = []
    for commodity, group in yr_df[yr_df["Year"].isin([2015, 2025])].groupby("Commodity"):
        vals = group.set_index("Year")["avg_modal_price"]
        if 2015 in vals.index and 2025 in vals.index:
            start, end = float(vals.loc[2015]), float(vals.loc[2025])
            year_increases.append({"Commodity": commodity, "price_2015": start, "price_2025": end,
                                   "absolute_change": end - start,
                                   "percent_change": (100 * (end - start) / start) if start else None})
    year_increases.sort(key=lambda x: x["absolute_change"], reverse=True)

    category_df = pd.DataFrame(cat_rows)
    category_map = {(r.Category, int(r.Year), int(r.Month)): float(r.avg_modal_price) for r in category_df.itertuples()}
    seasonal = defaultdict(list)
    for (cat, year, month), price in category_map.items():
        prior = category_map.get((cat, year - 1, month))
        if prior not in (None, 0):
            seasonal[month].append(100 * (price - prior) / prior)
    month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    seasonal_rows = [{"Month": m, "Month_Name": month_names[m - 1], "avg_yoy_change_pct": sum(v) / len(v), "category_year_pairs": len(v)} for m, v in seasonal.items() if v]
    seasonal_rows.sort(key=lambda x: x["avg_yoy_change_pct"], reverse=True)

    grade_df = pd.DataFrame(grade_rows)
    if not grade_df.empty:
        grade_wide = grade_df.pivot_table(index=["Commodity", "Variety"], columns="Grade", values="avg_modal_price", aggfunc="first").dropna(subset=["FAQ", "Medium"])
        grade_wide["premium"] = grade_wide["FAQ"] - grade_wide["Medium"]
        premiums = grade_wide.groupby("Commodity")["premium"].mean().sort_values(ascending=False)
        premium_rows = [{"Commodity": str(k), "avg_faq_premium": float(v), "varieties_compared": int((grade_wide.reset_index()["Commodity"] == k).sum())} for k, v in premiums.items()]
    else:
        premium_rows = []

    tomato_counts = defaultdict(int)
    for (state, market, date), price in tomato_market_days.items():
        if price >= 3000:
            tomato_counts[(state, market)] += 1
    tomato_rows = [{"State": k[0], "Market": k[1], "days_ge_3000": v} for k, v in sorted(tomato_counts.items(), key=lambda kv: kv[1], reverse=True)]

    rice_wheat = [r for r in year_rows if r["Commodity"] in ("Rice", "Wheat") and r["Year"] in (2020, 2024)]
    results = {
        "source": str(SOURCE), "years_included": [MIN_YEAR, MAX_YEAR], "source_files": [p.name for p in files],
        "source_csv_count": len(files), "raw_rows_scanned": total_rows, "rows_skipped_for_core_nulls": rejected_price_rows,
        "yearly_commodity_prices": year_rows,
        "largest_2015_2025_increases": year_increases[:15],
        "monthly_commodity_prices": monthly_rows,
        "seasonal_yoy_ranking": seasonal_rows,
        "district_volatility_top_20": sorted(district_rows, key=lambda x: x["avg_spread_pct"], reverse=True)[:20],
        "faq_grade_premiums_top_15": premium_rows[:15],
        "tomato_high_price_days_2024_top_20": tomato_rows[:20],
        "rice_wheat_2020_2024": rice_wheat,
    }
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nScanned {total_rows:,} rows across {len(files)} files ({MIN_YEAR}-{MAX_YEAR}).", flush=True)
    print(f"Saved aggregates: {DEST}", flush=True)
    print("Top tomato markets:", json.dumps(tomato_rows[:5], ensure_ascii=False), flush=True)
    print("Top volatility:", json.dumps(results["district_volatility_top_20"][:5], ensure_ascii=False), flush=True)
    print("Top premiums:", json.dumps(premium_rows[:5], ensure_ascii=False), flush=True)
    print("Seasonality:", json.dumps(seasonal_rows[:5], ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
