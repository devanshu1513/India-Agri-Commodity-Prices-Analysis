
from pathlib import Path
import argparse
import pandas as pd

# Project directories
PROJECT_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = PROJECT_DIR / "dataset" / "csv"
OUTPUT_DIR = PROJECT_DIR / "data" / "processed"

CHUNK_SIZE = 100_000

# Columns in the original dataset
REQUIRED_COLUMNS = [
    "State", "District", "Market", "Commodity",
    "Variety", "Grade", "Arrival_Date",
    "Min_Price", "Max_Price", "Modal_Price",
    "Commodity_Code"
]


def clean_chunk(df):
    # Remove accidental spaces from column names and text values
    df.columns = df.columns.str.strip()

    text_columns = [
        "State", "District", "Market",
        "Commodity", "Variety", "Grade"
    ]

    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()
        df[column] = df[column].replace("", pd.NA)

    # Convert dates and prices to appropriate data types
    df["Arrival_Date"] = pd.to_datetime(
        df["Arrival_Date"], errors="coerce"
    )

    price_columns = ["Min_Price", "Max_Price", "Modal_Price"]

    for column in price_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["Commodity_Code"] = pd.to_numeric(
        df["Commodity_Code"], errors="coerce"
    )

    # Remove rows with missing essential information
    df = df.dropna(
        subset=[
            "State", "Commodity", "Arrival_Date",
            "Min_Price", "Max_Price", "Modal_Price"
        ]
    )

    # Remove impossible price records
    df = df[
        (df["Min_Price"] >= 0)
        & (df["Max_Price"] >= df["Min_Price"])
        & (df["Modal_Price"] >= 0)
    ]

    # Remove exact duplicate rows within this chunk
    df = df.drop_duplicates()

    return df


def main():
    parser = argparse.ArgumentParser(description="Clean yearly agricultural price CSV files in chunks.")
    parser.add_argument("--input-dir", type=Path, default=INPUT_DIR, help="Folder containing the source yearly CSV files.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, help="Folder for cleaned yearly CSV files.")
    args = parser.parse_args()
    input_dir, output_dir = args.input_dir, args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(input_dir.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {input_dir}"
        )

    for file_path in csv_files:
        output_path = output_dir / file_path.name

        if output_path.exists():
            output_path.unlink()

        total_rows = 0
        cleaned_rows = 0

        print(f"\nProcessing {file_path.name}...")

        for chunk in pd.read_csv(
            file_path,
            chunksize=CHUNK_SIZE,
            low_memory=True
        ):
            total_rows += len(chunk)

            chunk.columns = chunk.columns.str.strip()

            missing_columns = set(REQUIRED_COLUMNS) - set(chunk.columns)
            if missing_columns:
                raise ValueError(
                    f"{file_path.name} is missing columns: "
                    f"{missing_columns}"
                )

            cleaned = clean_chunk(chunk)

            if not cleaned.empty:
                cleaned.to_csv(
                    output_path,
                    mode="a",
                    index=False,
                    header=not output_path.exists()
                )
                cleaned_rows += len(cleaned)

        print(f"Original rows processed: {total_rows:,}")
        print(f"Rows retained: {cleaned_rows:,}")
        print(f"Rows removed: {total_rows - cleaned_rows:,}")
        print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
