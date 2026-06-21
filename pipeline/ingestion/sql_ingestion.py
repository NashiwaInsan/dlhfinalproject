```python
import pandas as pd
from pathlib import Path
from datetime import datetime

from pipeline.state_manager import (
    load_watermark,
    save_watermark
)


def ingest_online_sales():

    state = load_watermark()

    watermark = state["sales_online"]

    # =====================================================
    # LOAD SAMPLE DATA
    # =====================================================

    historis = pd.read_csv(
        "sample_data/sample_sales_online_historis.csv"
    )

    stream = pd.read_csv(
        "sample_data/sample_sales_online_stream.csv"
    )

    # =====================================================
    # STANDARDIZE DATE
    # =====================================================

    historis["ModifiedDate"] = pd.to_datetime(
        historis["ModifiedDate"]
    )

    stream["ModifiedDate"] = pd.to_datetime(
        stream["ModifiedDate"]
    )

    watermark_dt = pd.to_datetime(
        watermark,
        utc=True
    )

    # Hilangkan timezone agar konsisten
    watermark_dt = watermark_dt.tz_localize(None)

    # =====================================================
    # INCREMENTAL FILTER
    # =====================================================

    historis_delta = historis[
        historis["ModifiedDate"] > watermark_dt
    ]

    stream_delta = stream[
        stream["ModifiedDate"] > watermark_dt
    ]

    # =====================================================
    # COMBINE
    # =====================================================

    df = pd.concat(
        [historis_delta, stream_delta],
        ignore_index=True
    )

    if df.empty:

        print(
            "Tidak ada online sales baru"
        )

        return

    # =====================================================
    # CREATE OUTPUT FOLDER
    # =====================================================

    Path(
        "lake/bronze/online_sales"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    # =====================================================
    # SAVE PARQUET
    # =====================================================

    filename = (
        "lake/bronze/online_sales/"
        f"online_sales_{datetime.now():%Y%m%d_%H%M%S}.parquet"
    )

    df.to_parquet(
        filename,
        index=False
    )

    # =====================================================
    # UPDATE WATERMARK
    # =====================================================

    latest_watermark = (
        df["ModifiedDate"]
        .max()
        .isoformat()
    )

    state["sales_online"] = latest_watermark
    save_watermark(state)

    # =====================================================
    # LOG
    # =====================================================

    print(
        f"{len(df)} online sales berhasil diproses"
    )

    print(
        f"Output : {filename}"
    )

    print(
        f"Watermark baru : {latest_watermark}"
    )


if __name__ == "__main__":

    ingest_online_sales()
```
