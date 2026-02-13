import pandas as pd

# -------------------------------
# 1. Load Dataset
# -------------------------------
df = pd.read_csv("price_dataset.csv")

print("Initial Shape:", df.shape)

# -------------------------------
# 2. Remove Duplicates
# -------------------------------
df = df.drop_duplicates()

# -------------------------------
# 3. Drop Rows Missing Critical Fields
# -------------------------------
df = df.dropna(subset=["Product_ID", "Date", "Amount", "Total_Purchases"])

# -------------------------------
# 4. Convert Date (Mixed Formats Safe)
# -------------------------------
df["Date"] = pd.to_datetime(
    df["Date"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

df = df.dropna(subset=["Date"])

# -------------------------------
# 5. Recreate Year & Month from Date
# -------------------------------
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

# -------------------------------
# 6. Convert Product_ID to Integer
# -------------------------------
df["Product_ID"] = df["Product_ID"].astype(int)

# -------------------------------
# 7. Fix Total_Amount (Business Logic Fix)
# -------------------------------
df["Total_Amount"] = df["Total_Amount"].fillna(
    df["Amount"] * df["Total_Purchases"]
)

# -------------------------------
# 8. Fill Remaining Numeric Columns
# -------------------------------
numeric_cols = df.select_dtypes(include=["number"]).columns
df[numeric_cols] = df[numeric_cols].fillna(0)

# -------------------------------
# 9. Fill Categorical Columns
# -------------------------------
categorical_cols = df.select_dtypes(include=["object", "string"]).columns
df[categorical_cols] = df[categorical_cols].fillna("Unknown")

# -------------------------------
# 10. Final Validation
# -------------------------------
print("\nFinal Shape:", df.shape)
print("\nRemaining Missing Values:\n", df.isnull().sum())

# -------------------------------
# 11. Save Clean Dataset
# -------------------------------
df.to_csv("cleaned_price_dataset.csv", index=False)

print("\n✅ FULLY CLEAN DATASET READY!")
