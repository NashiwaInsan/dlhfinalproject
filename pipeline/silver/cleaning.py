import pandas as pd
from pathlib import Path
import glob

# =====================================================
# ONLINE SALES
# =====================================================

def clean_online_sales():

    files = glob.glob(
        "lake/bronze/online_sales/*.parquet"
    )

    if not files:
        print("Tidak ada file online sales")
        return

    latest_file = max(
        files,
        key=lambda x: Path(x).stat().st_mtime
    )

    df = pd.read_parquet(
        latest_file
    )

    # ----------------------------
    # Null Handling
    # ----------------------------

    df["CustomerID"] = (
        df["CustomerID"]
        .fillna(0)
    )

    df["ProductID"] = (
        df["ProductID"]
        .fillna(0)
    )

    # ----------------------------
    # Standardisasi Tipe Data
    # ----------------------------

    df["CustomerID"] = (
        df["CustomerID"]
        .astype(int)
    )

    df["ProductID"] = (
        df["ProductID"]
        .astype(int)
    )

    df["OrderQty"] = (
        df["OrderQty"]
        .astype(int)
    )

    df["UnitPrice"] = (
        df["UnitPrice"]
        .astype(float)
    )

    # ----------------------------
    # Deduplikasi
    # ----------------------------

    df = df.drop_duplicates()

    # ----------------------------
    # Validation
    # ----------------------------

    invalid = df[
        (df["OrderQty"] <= 0)
        |
        (df["UnitPrice"] <= 0)
    ]

    valid = df[
        (df["OrderQty"] > 0)
        &
        (df["UnitPrice"] > 0)
    ]

    Path(
        "lake/quarantine/online_sales"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    Path(
        "lake/silver/online_sales"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    if not invalid.empty:

        invalid.to_parquet(
            "lake/quarantine/online_sales/"
            "online_sales_invalid.parquet",
            index=False
        )

    valid.to_parquet(
        "lake/silver/online_sales/"
        "online_sales_clean.parquet",
        index=False
    )

    print(
        f"Online Sales Bersih: {len(valid)}"
    )


# =====================================================
# STORE SALES
# =====================================================

def clean_store_sales():

    files = glob.glob(
        "lake/bronze/store_sales/*.parquet"
    )

    if not files:
        print("Tidak ada file store sales")
        return

    latest_file = max(
        files,
        key=lambda x: Path(x).stat().st_mtime
    )

    df = pd.read_parquet(
        latest_file
    )

    # ----------------------------
    # Null Handling
    # ----------------------------

    df["Region"] = (
        df["Region"]
        .fillna("UNKNOWN")
    )

    # ----------------------------
    # Standardisasi
    # ----------------------------

    df["QtySold"] = (
        df["QtySold"]
        .astype(int)
    )

    df["UnitPrice"] = (
        df["UnitPrice"]
        .astype(float)
    )

    # ----------------------------
    # Deduplikasi
    # ----------------------------

    df = df.drop_duplicates()

    # ----------------------------
    # Validation
    # ----------------------------

    invalid = df[
        (df["QtySold"] <= 0)
        |
        (df["UnitPrice"] <= 0)
    ]

    valid = df[
        (df["QtySold"] > 0)
        &
        (df["UnitPrice"] > 0)
    ]

    Path(
        "lake/quarantine/store_sales"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    Path(
        "lake/silver/store_sales"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    if not invalid.empty:

        invalid.to_parquet(
            "lake/quarantine/store_sales/"
            "store_sales_invalid.parquet",
            index=False
        )

    valid.to_parquet(
        "lake/silver/store_sales/"
        "store_sales_clean.parquet",
        index=False
    )

    print(
        f"Store Sales Bersih: {len(valid)}"
    )


# =====================================================
# REVIEWS
# =====================================================

def clean_reviews():

    files = glob.glob(
        "lake/bronze/reviews/*.parquet"
    )

    if not files:
        print("Tidak ada file reviews")
        return

    latest_file = max(
        files,
        key=lambda x: Path(x).stat().st_mtime
    )

    df = pd.read_parquet(
        latest_file
    )

    # ----------------------------
    # Null Handling
    # ----------------------------

    df["review_text"] = (
        df["review_text"]
        .fillna("NO REVIEW")
    )

    # ----------------------------
    # Standardisasi
    # ----------------------------

    df["rating"] = (
        df["rating"]
        .astype(int)
    )

    # ----------------------------
    # Deduplikasi
    # ----------------------------

    df = df.drop_duplicates()

    # ----------------------------
    # Validation
    # ----------------------------

    invalid = df[
        (df["rating"] < 1)
        |
        (df["rating"] > 5)
    ]

    valid = df[
        (df["rating"] >= 1)
        &
        (df["rating"] <= 5)
    ]

    Path(
        "lake/quarantine/reviews"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    Path(
        "lake/silver/reviews"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    if not invalid.empty:

        invalid.to_parquet(
            "lake/quarantine/reviews/"
            "reviews_invalid.parquet",
            index=False
        )

    valid.to_parquet(
        "lake/silver/reviews/"
        "reviews_clean.parquet",
        index=False
    )

    print(
        f"Reviews Bersih: {len(valid)}"
    )
```
