from pipeline.ingestion.sql_ingestion import (
    ingest_sales
)

from pipeline.ingestion.api_ingestion import (
    ingest_reviews
)

from pipeline.ingestion.excel_ingestion import (
    ingest_excel
)

from pipeline.silver.cleaning import (
    clean_sales,
    clean_reviews
)

from pipeline.silver.sentiment import (
    sentiment_reviews
)

import glob


def run():

    ingest_sales()

    ingest_reviews()

    ingest_excel()

    sales_files = glob.glob(
        "lake/bronze/sales/*.parquet"
    )

    review_files = glob.glob(
        "lake/bronze/reviews/*.parquet"
    )

    if sales_files:
        clean_sales(
            sales_files[-1]
        )

    if review_files:
        clean_reviews(
            review_files[-1]
        )

        sentiment_reviews()


if __name__ == "__main__":
    run()