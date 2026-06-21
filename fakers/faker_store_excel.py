"""
Faker TOKO FISIK (offline).
Membuat file Excel berisi transaksi salesperson dan menaruhnya di
folder watched/excel/. Inilah "data toko fisik" yang seluruhnya disimulasikan
(tidak ada di AdventureWorks asli).
"""
import os
import random
import time
from datetime import datetime, timedelta

import pandas as pd

from config import settings
from fakers._sources import get_products

REGIONS = ["Jakarta", "Surabaya", "Bandung", "Medan", "Makassar", "Semarang"]


def _generate_one_file():
    products = get_products()
    n_rows = random.randint(20, 60)
    rows = []
    for _ in range(n_rows):
        product_id, list_price = random.choice(products)
        rows.append(
            {
                "SalespersonID": random.randint(1, 17),
                "StoreID": random.randint(100, 130),
                "ProductID": product_id,
                "QtySold": random.randint(1, 10),
                # harga toko sedikit bervariasi dari ListPrice
                "UnitPrice": round(list_price * random.uniform(0.9, 1.1), 2),
                "SaleDate": (datetime.now() - timedelta(days=random.randint(0, 3))).strftime("%Y-%m-%d"),
                "Region": random.choice(REGIONS),
            }
        )

    os.makedirs(settings.WATCHED_EXCEL_PATH, exist_ok=True)
    filename = f"sales_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
    path = os.path.join(settings.WATCHED_EXCEL_PATH, filename)
    pd.DataFrame(rows).to_excel(path, index=False)
    print(f"[store_excel] menulis {path} ({n_rows} baris)")


def run(stop_event=None, duration_hours=72):
    deadline = time.time() + duration_hours * 3600
    while time.time() < deadline and (stop_event is None or not stop_event.is_set()):
        try:
            _generate_one_file()
        except Exception as exc:
            print(f"[store_excel] gagal: {exc}")
        time.sleep(settings.FAKER_EXCEL_INTERVAL)


if __name__ == "__main__":
    _generate_one_file()  # uji cepat: buat satu file lalu keluar
