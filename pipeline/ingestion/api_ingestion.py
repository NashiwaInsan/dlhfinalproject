import requests
import pandas as pd

from pathlib import Path
from datetime import datetime

from pipeline.state_manager import (
    load_watermark,
    save_watermark
)

API_URL = "http://localhost:8000/reviews/latest"


def ingest_reviews():

    state = load_watermark()

    since = state["review_created_at"]

    response = requests.get(
        API_URL,
        params={"since": since}
    )

    reviews = response.json()

    if len(reviews) == 0:
        print("Tidak ada review baru")
        return

    df = pd.DataFrame(reviews)

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

    state["review_created_at"] = (
        df["created_at"].max()
    )

    save_watermark(state)

    print(
        f"{len(df)} review berhasil disimpan"
    )