"""
Faker PENJUALAN ONLINE.
Menyuntikkan transaksi online "baru" ke tabel dbo.OnlineOrderStream di
SQL Server, sehingga seolah-olah penjualan online terus berjalan.
Data historis 2011-2014 tetap dibaca dari Sales.SalesOrderHeader asli (tidak disentuh faker).
"""
import random
import time
from datetime import datetime

import pymssql

from config import settings
from fakers._sources import get_products, get_customer_ids


def _conn():
    return pymssql.connect(
        server=settings.MSSQL["server"],
        port=str(settings.MSSQL["port"]),
        user=settings.MSSQL["user"],
        password=settings.MSSQL["password"],
        database=settings.MSSQL["database"],
    )


def _insert_order():
    product_id, list_price = random.choice(get_products())
    customer_id = random.choice(get_customer_ids())
    qty = random.randint(1, 5)
    unit_price = round(list_price * random.uniform(0.95, 1.05), 2)

    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO dbo.OnlineOrderStream
               (OrderDate, CustomerID, ProductID, OrderQty, UnitPrice, Channel)
           VALUES (%s, %s, %s, %s, %s, 'Online')""",
        (datetime.now(), customer_id, product_id, qty, unit_price),
    )
    conn.commit()
    conn.close()
    print(f"[sales_online] order cust={customer_id} prod={product_id} qty={qty}")


def run(stop_event=None, duration_hours=None):
    deadline = float("inf") if duration_hours is None else time.time() + duration_hours * 3600
    while time.time() < deadline and (stop_event is None or not stop_event.is_set()):
        try:
            _insert_order()
        except Exception as exc:
            print(f"[sales_online] gagal: {exc}")
        time.sleep(settings.FAKER_ONLINE_INTERVAL)


if __name__ == "__main__":
    _insert_order()  # uji cepat: masukkan satu order lalu keluar
