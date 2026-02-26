import os
import pandas as pd
from datetime import datetime

# -------------------------------
# Paths & Settings
# -------------------------------
RAW_PATH = "data/raw/cleaned_price_dataset.csv"
PROCESSED_FOLDER = "data/processed"
DAILY_FOLDER = "data/daily_ingest"
OUTPUT_FILE = "priceoptima_processed.csv"

# Columns required for safe processing
REQUIRED_COLUMNS = [
    "Date",
    "Product_ID",
    "Total_Purchases",
    "Amount"
]

# Optional categorical columns to fill missing values
CATEGORICAL_COLS = [
    "City", "State", "Country", "Customer_Segment",
    "Product_Brand", "Payment_Method"
]

# -------------------------------
# Helper Functions
# -------------------------------
def create_folders():
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    os.makedirs(DAILY_FOLDER, exist_ok=True)

def validate_columns(df):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    print("✅ Column validation successful")

def clean_data(df):
    print(f"Rows before cleaning: {len(df)}")
    df = df.drop_duplicates()
    
    # Fill categorical missing values
    for col in CATEGORICAL_COLS:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].mode()[0])

    # Drop only critical missing values
    df = df.dropna(subset=REQUIRED_COLUMNS)

    # Convert date safely
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")  # <- warning removed
    df = df.dropna(subset=["Date"])

    # Convert numeric fields
    df["Product_ID"] = pd.to_numeric(df["Product_ID"], errors="coerce")
    df["Total_Purchases"] = pd.to_numeric(df["Total_Purchases"], errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

    df = df.dropna(subset=["Product_ID", "Total_Purchases", "Amount"])
    df["Product_ID"] = df["Product_ID"].astype(int)

    # Calculate Total_Amount if column exists
    if "Total_Amount" in df.columns:
        df["Total_Amount"] = df["Total_Amount"].fillna(df["Total_Purchases"] * df["Amount"])

    print(f"Rows after cleaning: {len(df)}")
    return df

def save_processed(df):
    processed_path = os.path.join(PROCESSED_FOLDER, OUTPUT_FILE)
    df.to_csv(processed_path, index=False)
    print(f"✅ Processed file saved: {processed_path}")

def save_daily_copy(df):
    # Timestamp ensures multiple runs per day do not overwrite
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    daily_path = os.path.join(DAILY_FOLDER, timestamp)
    os.makedirs(daily_path, exist_ok=True)
    df.to_csv(os.path.join(daily_path, OUTPUT_FILE), index=False)
    print(f"✅ Daily ingestion completed: {daily_path}")

# -------------------------------
# Main Pipeline
# -------------------------------
def main():
    print("\n===== AI PriceOptima Ingestion Started =====\n")

    create_folders()

    if not os.path.exists(RAW_PATH):
        print("❌ Dataset not found in raw folder.")
        return

    df = pd.read_csv(RAW_PATH)
    print(f"📥 Dataset loaded successfully. Rows: {len(df)}")

    validate_columns(df)
    df_cleaned = clean_data(df)
    save_processed(df_cleaned)
    save_daily_copy(df_cleaned)

    print("\n===== Ingestion Completed Successfully =====\n")

# -------------------------------
# Run Script
# -------------------------------
if __name__ == "__main__":
    main()