```python
from pipeline.ingestion.sql_ingestion import (
    ingest_online_sales
)

from pipeline.ingestion.api_ingestion import (
    ingest_reviews
)

from pipeline.ingestion.excel_ingestion import (
    ingest_store_sales
)

from pipeline.silver.cleaning import (
    clean_online_sales,
    clean_store_sales,
    clean_reviews
)

from pipeline.silver.sentiment import (
    sentiment_reviews
)


def run():

    print("=" * 50)
    print("INGESTION LAYER")
    print("=" * 50)

    ingest_online_sales()

    ingest_store_sales()
    ingest_reviews()

    print("\n")

    print("=" * 50)
    print("SILVER LAYER")
    print("=" * 50)

    clean_online_sales()
    clean_store_sales()
    clean_reviews()

    print("\n")

    print("=" * 50)
    print("SENTIMENT ANALYSIS")
    print("=" * 50)

    sentiment_reviews()

    print("\n")

    print("=" * 50)
    print("PIPELINE SELESAI")
    print("=" * 50)


if __name__ == "__main__":
    run()
```
