"""
Export sample data dari SQL Server & Marketplace API menjadi file CSV/JSON kecil
di folder sample_data/, supaya bisa di-commit ke GitHub dan dipakai Anggota 2 & 3
TANPA mereka perlu install Docker / restore .bak sendiri.

Jalankan ini SETELAH faker sudah mengisi beberapa data:
    python export_sample_data.py

Catatan: ini hanya untuk keperluan development & testing kode ETL.
Integrasi & hasil akhir tetap dijalankan di laptop Anggota 1 dengan data lengkap.
"""
import json
import os

import pandas as pd
import pymssql
import requests

from config import settings

OUT_DIR = "sample_data"


def export_master_data():
    """Export sample dim_product & dim_customer dari SQL Server."""
    conn = pymssql.connect(
        server=settings.MSSQL["server"], port=str(settings.MSSQL["port"]),
        user=settings.MSSQL["user"], password=settings.MSSQL["password"],
        database=settings.MSSQL["database"],
    )

    products = pd.read_sql(
        """SELECT TOP 200 ProductID, Name AS ProductName, ProductNumber,
                  Color, Size, StandardCost, ListPrice
           FROM Production.Product WHERE ListPrice > 0""", conn)
    products.to_csv(f"{OUT_DIR}/sample_dim_product.csv", index=False)
    print(f"[ok] sample_dim_product.csv ({len(products)} baris)")

    customers = pd.read_sql(
        """SELECT TOP 200 CustomerID, PersonID, StoreID, TerritoryID
           FROM Sales.Customer""", conn)
    customers.to_csv(f"{OUT_DIR}/sample_dim_customer.csv", index=False)
    print(f"[ok] sample_dim_customer.csv ({len(customers)} baris)")

    # Historis online sales (contoh kecil saja, bukan semua 95rb baris)
    sales_hist = pd.read_sql(
        """SELECT TOP 500 soh.SalesOrderID, soh.OrderDate, soh.CustomerID,
                  sod.ProductID, sod.OrderQty, sod.UnitPrice, soh.ModifiedDate
           FROM Sales.SalesOrderHeader soh
           JOIN Sales.SalesOrderDetail sod ON soh.SalesOrderID = sod.SalesOrderID
           ORDER BY soh.ModifiedDate DESC""", conn)
    sales_hist.to_csv(f"{OUT_DIR}/sample_sales_online_historis.csv", index=False)
    print(f"[ok] sample_sales_online_historis.csv ({len(sales_hist)} baris)")

    # Data baru dari faker (tabel stream)
    stream = pd.read_sql("SELECT * FROM dbo.OnlineOrderStream", conn)
    stream.to_csv(f"{OUT_DIR}/sample_sales_online_stream.csv", index=False)
    print(f"[ok] sample_sales_online_stream.csv ({len(stream)} baris)")

    conn.close()


def export_reviews():
    """Export semua review dari API ke file JSON."""
    url = settings.MARKETPLACE_API_URL.rstrip("/") + "/reviews/latest"
    resp = requests.get(url, timeout=10)
    reviews = resp.json()
    with open(f"{OUT_DIR}/sample_reviews.json", "w", encoding="utf-8") as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False, default=str)
    print(f"[ok] sample_reviews.json ({len(reviews)} baris)")


def copy_excel_samples():
    """Salin file Excel faker ke sample_data/excel/."""
    import shutil
    src_dir = settings.WATCHED_EXCEL_PATH
    dst_dir = f"{OUT_DIR}/excel"
    os.makedirs(dst_dir, exist_ok=True)
    files = [f for f in os.listdir(src_dir) if f.endswith(".xlsx")]
    for f in files:
        shutil.copy(os.path.join(src_dir, f), os.path.join(dst_dir, f))
    print(f"[ok] {len(files)} file Excel disalin ke {dst_dir}/")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    export_master_data()
    export_reviews()
    copy_excel_samples()
    print("\nSelesai. Commit folder sample_data/ ke git agar tim bisa pakai.")
