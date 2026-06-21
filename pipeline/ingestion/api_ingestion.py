import pandas as pd
from pathlib import Path
from datetime import datetime

from pipeline.state_manager import (
    load_watermark,
    save_watermark
)


def ingest_reviews():
    state = load_watermark()

    watermark = state["reviews"]

    df = pd.read_json(
        "sample_data/sample_reviews.json"
    )

    df["created_at"] = pd.to_datetime(
        df["created_at"]
    )

    watermark_dt = pd.to_datetime(
        watermark
    )

    df = df[
        df["created_at"] > watermark_dt
    ]

    if df.empty:
        print("Tidak ada review baru")
        return

    Path(
        "lake/bronze/reviews"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    filename = (
        f"lake/bronze/reviews/"
        f"reviews_{datetime.now():%Y%m%d_%H%M%S}.parquet"
    )

    df.to_parquet(
        filename,
        index=False
    )

    latest_watermark = (
        df["created_at"]
        .max()
        .isoformat()
    )

    state["reviews"] = latest_watermark

    save_watermark(state)
    print(
        f"{len(df)} review berhasil diproses"
    )