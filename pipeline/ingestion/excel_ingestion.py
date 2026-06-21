import os
import shutil

from pathlib import Path

from pipeline.state_manager import (
    load_watermark,
    save_watermark
)

WATCH_FOLDER = "watched"


def ingest_excel():

    state = load_watermark()

    processed = state["processed_excel_files"]

    Path(
        "lake/bronze/excel"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    files = [
        f for f in os.listdir(WATCH_FOLDER)
        if f.endswith(".xlsx")
    ]

    for file in files:

        if file in processed:
            continue

        src = os.path.join(
            WATCH_FOLDER,
            file
        )

        dst = os.path.join(
            "lake/bronze/excel",
            file
        )

        shutil.copy(
            src,
            dst
        )

        processed.append(file)

        print(f"{file} berhasil diproses")

    state["processed_excel_files"] = processed

    save_watermark(state)   