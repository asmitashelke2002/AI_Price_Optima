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
# 3. Clean Text Columns (Trim Spaces)
# -------------------------------
text_cols = df.select_dtypes(include=["object", "string"]).columns
df[text_cols] = df[text_cols].apply(lambda x: x.str.strip())

# -------------------------------
# 4. Remove Invalid Product Categories
# -------------------------------
if "Product_Category" in df.columns:
    df["Product_Category"] = df["Product_Category"].str.title()

    df = df[
        (df["Product_Category"].notna()) &
        (df["Product_Category"] != "") &
        (df["Product_Category"].str.lower() != "unknown")
    ]

# -------------------------------
# 5. Clean Feedback & Shipping_Method
# -------------------------------
if "Feedback" in df.columns:
    df["Feedback"] = df["Feedback"].replace("", pd.NA)
    df = df.dropna(subset=["Feedback"])
    df["Feedback"] = df["Feedback"].str.title()

    valid_feedback = ["Excellent", "Good", "Average", "Bad"]
    df = df[df["Feedback"].isin(valid_feedback)]

if "Shipping_Method" in df.columns:
    df["Shipping_Method"] = df["Shipping_Method"].replace("", pd.NA)
    df = df.dropna(subset=["Shipping_Method"])
    df["Shipping_Method"] = df["Shipping_Method"].str.title()

    valid_shipping = ["Same-Day", "Standard", "Express"]
    df = df[df["Shipping_Method"].isin(valid_shipping)]

# -------------------------------
# 6. Drop Rows Missing Critical Numeric Fields
# -------------------------------
df = df.dropna(subset=["Product_ID", "Date", "Amount", "Total_Purchases"])

# -------------------------------
# 7. Convert Date (Mixed Format Safe)
# -------------------------------
df["Date"] = pd.to_datetime(
    df["Date"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

df = df.dropna(subset=["Date"])

# -------------------------------
# 8. Create Year & Month Columns
# -------------------------------
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

# -------------------------------
# 9. Convert Numeric Columns Safely
# -------------------------------
numeric_columns = ["Product_ID", "Amount", "Total_Purchases", "Total_Amount"]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["Product_ID"])
df["Product_ID"] = df["Product_ID"].astype(int)

# -------------------------------
# 10. Fix Total_Amount (Business Logic)
# -------------------------------
if "Total_Amount" in df.columns:
    df["Total_Amount"] = df["Total_Amount"].fillna(
        df["Amount"] * df["Total_Purchases"]
    )

# -------------------------------
# 11. Fill Remaining Numeric Missing Values with 0
# -------------------------------
numeric_cols = df.select_dtypes(include=["number"]).columns
df[numeric_cols] = df[numeric_cols].fillna(0)

# -------------------------------
# 12. Fill Remaining Categorical Missing Values with Mode
# -------------------------------
categorical_cols = ["City", "State", "Country", "Customer_Segment",
                    "Product_Brand", "Payment_Method", "Time"]

for col in categorical_cols:
    if col in df.columns:
        df[col] = df[col].fillna(df[col].mode()[0])

# -------------------------------
# 13. Final Validation
# -------------------------------
print("\nFinal Shape:", df.shape)
print("\nRemaining Missing Values:\n", df.isnull().sum())

if "Product_Category" in df.columns:
    print("\nUnique Product Categories:")
    print(df["Product_Category"].unique())

if "Feedback" in df.columns:
    print("\nUnique Feedback Values:")
    print(df["Feedback"].unique())

if "Shipping_Method" in df.columns:
    print("\nUnique Shipping Methods:")
    print(df["Shipping_Method"].unique())
# -------------------------------
# 14. Dataset Summary (EDA Check)
# -------------------------------
print("\nNumeric Summary:")
print(df.describe())

print("\nCategorical Summary:")
print(df.describe(include=['object', 'string']))


# -------------------------------
# 15. Save Clean Dataset
# -------------------------------
df.to_csv("cleaned_price_dataset.csv", index=False)

print("\n✅ FULLY CLEANED DATASET READY FOR ANALYSIS!")