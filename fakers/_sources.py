"""
Helper untuk mengambil ID produk & pelanggan yang VALID dari AdventureWorks.
Tujuannya agar data buatan faker (Excel & review) tetap bisa di-join ke
dim_product / dim_customer di tahap Gold nanti.
"""
import random
from functools import lru_cache

import pymssql

from config import settings


def _conn():
    return pymssql.connect(
        server=settings.MSSQL["server"],
        port=str(settings.MSSQL["port"]),
        user=settings.MSSQL["user"],
        password=settings.MSSQL["password"],
        database=settings.MSSQL["database"],
    )


@lru_cache(maxsize=1)
def get_customer_ids():
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT TOP 500 CustomerID FROM Sales.Customer ORDER BY NEWID()")
    ids = [row[0] for row in cur.fetchall()]
    conn.close()
    return ids


@lru_cache(maxsize=1)
def get_products():
    """Kembalikan list (ProductID, ListPrice) untuk produk yang punya harga."""
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT TOP 500 ProductID, ListPrice FROM Production.Product "
        "WHERE ListPrice > 0 ORDER BY NEWID()"
    )
    rows = [(row[0], float(row[1])) for row in cur.fetchall()]
    conn.close()
    return rows


def random_customer():
    return random.choice(get_customer_ids())


def random_product():
    return random.choice(get_products())
