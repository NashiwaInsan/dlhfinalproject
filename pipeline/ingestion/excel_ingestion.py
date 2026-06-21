import pandas as pd
from pathlib import Path
from datetime import datetime

from pipeline.state_manager import (
    load_watermark,
    save_watermark
)


def ingest_store_sales():
    state = load_watermark()

    watermark = state["store_excel"]

    watermark_dt = pd.to_datetime(
        watermark,
        utc=True
    )

    excel_folder = Path(
        "sample_data/excel"
    )

    files = list(
        excel_folder.glob("*.xlsx")
    )

    if not files:
        print("Tidak ada file excel ditemukan")
        return

    all_data = []

    for file in files:

        df = pd.read_excel(file)

        df["SaleDate"] = pd.to_datetime(
            df["SaleDate"]
        )

        delta = df[
            df["SaleDate"] > watermark_dt.tz_localize(None)
        ]

        if not delta.empty:
            all_data.append(delta)

    if not all_data:
        print("Tidak ada store sales baru")
        return

    final_df = pd.concat(
        all_data,
        ignore_index=True
    )

    Path(
        "lake/bronze/store_sales"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    filename = (
        f"lake/bronze/store_sales/"
        f"store_sales_{datetime.now():%Y%m%d_%H%M%S}.parquet"
    )

    final_df.to_parquet(
        filename,
        index=False
    )

    latest_watermark = (
        final_df["SaleDate"]
        .max()
        .isoformat()
    )

    state["store_excel"] = latest_watermark

    save_watermark(state)

    print(
        f"{len(final_df)} store sales berhasil diproses"
    )
