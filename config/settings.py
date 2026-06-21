"""Konfigurasi terpusat. Membaca file .env di root proyek."""
import os
from dotenv import load_dotenv

load_dotenv()

# SQL Server diakses dari HOST -> pakai localhost + port yang dipublikasikan.
MSSQL = dict(
    server=os.getenv("MSSQL_HOST", "localhost"),
    port=int(os.getenv("MSSQL_PORT", "1433")),
    user=os.getenv("MSSQL_USER", "sa"),
    password=os.getenv("MSSQL_PASSWORD", "YourStrong!Passw0rd"),
    database=os.getenv("MSSQL_DATABASE", "AdventureWorks2022"),
)

MARKETPLACE_API_URL = os.getenv("MARKETPLACE_API_URL", "http://localhost:8000")
WATCHED_EXCEL_PATH = os.getenv("WATCHED_EXCEL_PATH", "./watched/excel")

FAKER_ONLINE_INTERVAL = int(os.getenv("FAKER_ONLINE_INTERVAL", "60"))
FAKER_REVIEW_INTERVAL = int(os.getenv("FAKER_REVIEW_INTERVAL", "45"))
FAKER_EXCEL_INTERVAL = int(os.getenv("FAKER_EXCEL_INTERVAL", "600"))
