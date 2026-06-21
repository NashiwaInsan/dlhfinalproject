# AdventureWorks Data Lakehouse

Proyek Data Lakehouse untuk **AdventureWorks**, perusahaan manufaktur dan
distributor sepeda. Proyek ini menyatukan data yang awalnya terpisah-pisah
(silo) dari tiga kanal berbeda ke dalam satu gudang data analitik, lalu
menyajikannya sebagai dashboard Business Intelligence.

---

## Apa ini?

Sistem ini mengintegrasikan **tiga sumber data** yang formatnya berbeda-beda:

1. **Penjualan online** — database transaksional SQL Server (`AdventureWorks2025`)
2. **Penjualan toko fisik** — file Excel harian (disimulasikan)
3. **Ulasan pelanggan** — REST API marketplace, disimpan di PostgreSQL (disimulasikan)

Ketiga sumber data tersebut tadinya tidak saling terhubung, baik dari sisi
teknologi penyimpanan maupun format datanya. Proyek ini membangun pipeline
yang menarik, membersihkan, dan menggabungkan ketiganya, sehingga performa
penjualan dan persepsi pelanggan terhadap produk bisa dianalisis dalam satu
tempat yang sama.

---

## Anggota & Jobdesk

| Anggota | Jobdesk |
|---------|---------|
| Anggota 1 | Infrastruktur Docker, restore database, faker (generator data) |
| Anggota 2 | Ingestion (incremental/watermark) + Silver Layer (cleaning & sentimen) |
| Anggota 3 | Gold Layer (Star Schema) + load DuckDB + dashboard Power BI |

---

## Cara Kerjanya

Data ditarik lewat pipeline ETL berbasis Python, diproses bertahap dengan
**Medallion Architecture** (Bronze → Silver → Gold) berformat Parquet, dimuat
ke gudang data **DuckDB** (Star Schema), lalu divisualisasikan di **Power BI**.
Ulasan pelanggan dianalisis sentimennya menggunakan **NLTK VADER**.

### Alur singkat
```
[SQL Server]  [Excel]  [REST API/Postgres]
        \        |        /
         v       v       v
        ETL (Python, watermark/incremental)
                 |
     Bronze -> Silver -> Gold   (Parquet, /lake/)
                 |
              DuckDB  (Star Schema)
                 |
             Power BI
```

Secara bertahap, alur kerjanya seperti ini:

1. **Ingestion (→ Bronze).** Setiap sumber data ditarik secara inkremental
   menggunakan mekanisme watermark, yaitu penanda waktu terakhir kali data
   diambil. Hanya data baru atau yang berubah sejak watermark terakhir yang
   diambil, lalu disimpan mentah (tanpa diubah) ke `lake/bronze/` sebagai
   Parquet. Watermark tiap sumber dicatat di `pipeline/state/watermark.json`.

2. **Silver (bersih & validasi).** Data Bronze dibersihkan: deduplikasi,
   penanganan nilai kosong, dan standarisasi tipe data. Aturan bisnis yang
   diterapkan adalah transaksi valid jika `Quantity > 0` dan `UnitPrice > 0`,
   serta rating ulasan harus berada pada rentang 1 sampai 5. Baris yang gagal
   validasi dipindahkan ke `lake/quarantine/` (tidak dihapus), sedangkan
   yang valid disimpan ke `lake/silver/`. Di tahap ini juga dijalankan
   analisis sentimen NLTK VADER pada teks ulasan, menghasilkan kolom
   `SentimentLabel` (POSITIVE/NEUTRAL/NEGATIVE) dan `SentimentConfidence`.

3. **Gold (Star Schema).** Data Silver dimodelkan menjadi skema bintang yang
   terdiri dari tabel dimensi (`dim_date`, `dim_product`, `dim_customer`) dan
   tabel fakta (`fact_sales`, `fact_reviews`), ditambah satu data mart agregat
   (`mart_sentiment`). Pada tahap ini juga dihitung metrik `Revenue`, `Cost`,
   dan `Profit`. Hasilnya disimpan ke `lake/gold/` sebagai Parquet.

4. **Data Warehouse & Visualisasi.** Seluruh tabel Gold dimuat ke dalam
   database **DuckDB** (`warehouse/datalake.duckdb`), lalu diakses oleh
   **Power BI Desktop** melalui koneksi ODBC dengan mode `read_only`, untuk
   ditampilkan sebagai dashboard interaktif (revenue/profit per kategori,
   tren per tahun, distribusi sentimen, dan korelasi rating dengan profit).

### Tech stack
Python (pandas, pyarrow) · NLTK VADER · Parquet · FastAPI · Docker Compose ·
DuckDB · Power BI Desktop

---

## Struktur Direktori

```
.
├── config/                     # Konfigurasi koneksi (SQL Server, Postgres, path, dst.)
│   └── settings.py
│
├── docker/                     # Definisi infrastruktur sumber data
│   ├── docker-compose.yml      # SQL Server, Postgres, pgAdmin, Marketplace API
│   ├── postgres/init.sql       # Skema awal tabel reviews
│   └── sqlserver/               # Skrip restore database & tabel stream
│       ├── restore.sh
│       └── online_stream.sql
│
├── marketplace_api/            # REST API (FastAPI) penerima ulasan pelanggan
│   ├── main.py
│   └── Dockerfile
│
├── fakers/                     # Generator data simulasi (faker)
│   ├── faker_sales_online.py       # simulasi transaksi online baru
│   ├── faker_store_excel.py        # simulasi file Excel toko fisik
│   ├── faker_marketplace_reviews.py # simulasi ulasan pelanggan
│   └── _sources.py                 # helper ambil ProductID/CustomerID valid
│
├── pipeline/                   # Inti pipeline ETL
│   ├── runner.py                # orkestrator: jalankan semua tahap berurutan
│   ├── state_manager.py         # baca/tulis watermark
│   ├── state/
│   │   └── watermark.json       # timestamp terakhir tiap sumber data
│   ├── ingestion/                # tahap Bronze (extract per sumber)
│   │   ├── sql_ingestion.py
│   │   ├── excel_ingestion.py
│   │   └── api_ingestion.py
│   ├── silver/                   # tahap pembersihan & sentimen
│   │   ├── cleaning.py
│   │   └── sentiment.py
│   └── gold/                     # tahap pemodelan Star Schema
│       └── star_schema_builder.py
│
├── lake/                       # Data lake fisik (hasil pipeline)
│   ├── bronze/                  # data mentah per sumber (online_sales, store_sales, reviews)
│   ├── silver/                  # data bersih & terstandarisasi
│   ├── gold/                    # tabel dimensi & fakta siap pakai (Parquet)
│   └── quarantine/              # baris yang gagal validasi, untuk audit
│
├── watched/excel/              # folder yang dipantau untuk file Excel toko fisik baru
│
├── sample_data/                 # contoh data berskala kecil untuk pengembangan
│   ├── sample_dim_product.csv
│   ├── sample_dim_customer.csv
│   ├── sample_sales_online_historis.csv
│   ├── sample_sales_online_stream.csv
│   ├── sample_reviews.json
│   └── excel/sales_*.xlsx
│
├── run_fakers.py                # entry point menjalankan satu/semua faker
├── export_sample_data.py        # menarik sample dari data live ke sample_data/
├── requirements.txt
└── .env.example                 # contoh konfigurasi environment
```

---

## Kontrak Data (struktur tiap sumber)

### Sumber 1 — Penjualan Online
- SQL Server `localhost:1433`, database `AdventureWorks2025`
  - Historis: `Sales.SalesOrderHeader` + `Sales.SalesOrderDetail` (filter `ModifiedDate`)
  - Data baru dari faker: tabel `dbo.OnlineOrderStream`
    (kolom: `OrderStreamID, OrderDate, CustomerID, ProductID, OrderQty, UnitPrice, Channel, ModifiedDate`)
  - Master: `Production.Product` (`StandardCost`, `ListPrice`), `Sales.Customer`

### Sumber 2 — Toko Fisik (Excel)
- Folder `watched/excel/*.xlsx`
- Kolom: `SalespersonID, StoreID, ProductID, QtySold, UnitPrice, SaleDate, Region`

### Sumber 3 — Ulasan Pelanggan
- `GET http://localhost:8000/reviews/latest?since=<ISO timestamp>`
- Field: `review_id, product_id, customer_id, rating, review_text, language, is_verified, review_date, created_at`

### Watermark
Timestamp terakhir tiap sumber disimpan di `pipeline/state/watermark.json`:
```json
{
  "sales_online": "2026-06-21T05:00:00+00:00",
  "store_excel":  "2026-06-21T05:00:00+00:00",
  "reviews":      "2026-06-21T05:00:00+00:00"
}
```

---

## Beberapa Keputusan Desain

### `Channel` di `fact_sales`
- Data dari SQL Server (`Sales.SalesOrderHeader`/`OnlineOrderStream`) → `'Online'`
- Data dari Excel toko fisik → `'Store'` (bukan `'Offline'`), agar konsisten
  dengan empat nilai kanal standar (`Online, Partner, Reseller, Store`) yang
  dipakai pada laporan referensi proyek ini.

### Format `SaleID`
Karena Excel tidak punya ID transaksi bawaan, `fact_sales.SaleID` dibentuk
sebagai surrogate key string per sumber, dijamin unik dan idempoten (tidak
berubah meski pipeline dijalankan ulang):

| Sumber | Format | Contoh |
|--------|--------|--------|
| Online historis | `ON-{SalesOrderID}-{ProductID}` | `ON-71774-708` |
| Online stream (faker) | `ON-STREAM-{OrderStreamID}` | `ON-STREAM-42` |
| Toko fisik (Excel) | `OFF-{NamaFileExcelTanpaExtensi}-{NomorBarisDalamFile}` | `OFF-sales_20260621_121139-7` |

### Cost & Profit
`Profit = Revenue - Cost`. Nilai `Cost` diambil dari `StandardCost` produk.
Jika tidak tersedia (umumnya pada transaksi Excel yang produknya tidak
tercatat di master), digunakan biaya standar default `UnitPrice * 0.6`.

---

## Cara Menjalankan

**Prasyarat:** Docker Desktop, Python 3.11+, file `AdventureWorks2025.bak`
(unduh dari [SQL Server samples Microsoft](https://github.com/Microsoft/sql-server-samples/releases/tag/adventureworks),
versi OLTP penuh, bukan LT/DW).

```bash
# 1. Siapkan environment
cd docker
cp ../.env.example .env

# 2. Taruh AdventureWorks2025.bak ke docker/sqlserver/backup/

# 3. Nyalakan semua service
docker compose up -d
docker compose logs -f sqlserver_init    # tunggu "INIT SELESAI"

# 4. Jalankan faker (mengisi data toko fisik & ulasan secara berkala)
cd ..
cp .env.example .env
pip install -r requirements.txt
python run_fakers.py --sources all --duration 1

# 5. Jalankan pipeline ETL (Bronze -> Silver -> Gold)
python -m pipeline.runner
```

## Final Deliverables

- `warehouse/datalake.duckdb`
- `AdventureWorks_Dashboard.pbix`

## Kredensial Default (development lokal)
- SQL Server: user `sa`, password di `.env` (`MSSQL_PASSWORD`), DB `AdventureWorks2025`
- PostgreSQL: `mkuser` / `mkpass123`, DB `marketplace_db`
- Marketplace API: `http://localhost:8000`

## Catatan
File `.bak`, `.env`, dan data lake/warehouse penuh **tidak** disimpan di Git
(lihat `.gitignore`), hanya `sample_data/` yang sengaja dikecualikan supaya
proyek ini bisa dijalankan ulang dan dikembangkan tanpa setup berat.
