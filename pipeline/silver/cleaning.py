import pandas as pd

from pathlib import Path


def clean_sales(input_file):

    df = pd.read_parquet(input_file)

    invalid = df[
        (df["OrderQty"] <= 0)
        |
        (df["UnitPrice"] <= 0)
    ]

    clean = df[
        (df["OrderQty"] > 0)
        &
        (df["UnitPrice"] > 0)
    ]

    Path(
        "lake/quarantine/sales"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    Path(
        "lake/silver/sales"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    if not invalid.empty:
        invalid.to_parquet(
            "lake/quarantine/sales/bad_sales.parquet",
            index=False
        )

    clean = clean.drop_duplicates()

    clean.to_parquet(
        "lake/silver/sales/sales_clean.parquet",
        index=False
    )


def clean_reviews(input_file):

    df = pd.read_parquet(input_file)

    invalid = df[
        df["review_text"].isna()
    ]

    clean = df[
        df["review_text"].notna()
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
            "lake/quarantine/reviews/bad_reviews.parquet",
            index=False
        )

    clean = clean.drop_duplicates()

    clean.to_parquet(
        "lake/silver/reviews/reviews_clean.parquet",
        index=False
    )