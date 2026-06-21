import pandas as pd
import pyodbc

from pathlib import Path
from datetime import datetime

from pipeline.state_manager import (
    load_watermark,
    save_watermark
)


def ingest_sales():

    state = load_watermark()

    watermark = state["sales_modified_date"]

    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost,1433;"
        "DATABASE=AdventureWorks2025;"
        "UID=sa;"
        "PWD=YOUR_PASSWORD"
    )

    query = f"""
    SELECT *
    FROM dbo.OnlineOrderStream
    WHERE ModifiedDate > '{watermark}'
    ORDER BY ModifiedDate
    """

    df = pd.read_sql(
        query,
        conn
    )

    if df.empty:
        print("Tidak ada sales baru")
        conn.close()
        return

    Path(
        "lake/bronze/sales"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    filename = (
        f"lake/bronze/sales/"
        f"sales_{datetime.now():%Y%m%d_%H%M%S}.parquet"
    )

    df.to_parquet(
        filename,
        index=False
    )

    state["sales_modified_date"] = str(
        df["ModifiedDate"].max()
    )

    save_watermark(state)

    conn.close()

    print(
        f"{len(df)} sales berhasil disimpan"
    )