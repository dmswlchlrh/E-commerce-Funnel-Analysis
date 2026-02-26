import pandas as pd

RAW_PATH = "data/2019-Nov.csv"
OUTPUT_PATH = "data/sample_ecommerce.csv"

USE_COLS = [
    "user_id",
    "event_type",
    "event_time",
    "product_id",
    "category_code",
    "price"
]

# Number of rows for this project
N_ROWS = 100_000 

def main():
    print("Loading raw data...")
    df = pd.read_csv(
        RAW_PATH,
        usecols=USE_COLS,
        nrows=N_ROWS
    )

    print(f"Sample size: {len(df):,} rows")
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved sample to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
