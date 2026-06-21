# AdventureWorks Data Lakehouse

Proyek Final Data Lakehouse untuk **AdventureWorks** (perusahaan manufaktur &
distributor sepeda). Tujuannya menyatukan data yang tadinya terpisah-pisah
(silo) dari tiga kanal berbeda ke dalam satu gudang data analitik, lalu
menyajikannya sebagai dashboard Business Intelligence.

---

## Apa ini?

Sistem mengintegrasikan **tiga sumber data** yang formatnya berbeda-beda:

1. **Penjualan online** — database transaksional SQL Server (`AdventureWorks2025`)
2. **Penjualan toko fisik** — file Excel harian (disimulasikan)
3. **Ulasan pelanggan** — REST API marketplace, disimpan di PostgreSQL (disimulasikan)

Data ditarik lewat pipeline ETL Python, diproses bertahap dengan **Medallion
Architecture** (Bronze → Silver → Gold) berformat Parquet, dimuat ke gudang data
**DuckDB** (Star Schema), lalu divisualisasikan di **Power BI**. Ulasan dianalisis
sentimennya menggunakan **NLTK VADER**.

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

### Tech stack
Python (pandas, pyarrow) · NLTK VADER · Parquet · FastAPI · Docker Compose ·
DuckDB · Power BI Desktop

---

## Pembagian tugas & status

| Anggota | Fokus | Status |
|--------|-------|--------|
| **Anggota 1** | Infrastruktur Docker, restore database, faker (generator data) | ✅ Selesai |
| **Anggota 2** | Ingestion (incremental/watermark) + Silver Layer (cleaning) | ⬜ Belum |
| **Anggota 3** | Gold Layer (Star Schema) + load DuckDB + Power BI | ⬜ Belum |

---

## PENTING: Cara Kerja Tim (baca dulu sebelum mulai!)

**Anggota 2 & 3 TIDAK PERLU install Docker atau menjalankan faker.** Infrastruktur
dan data sudah hidup di laptop Anggota 1. Supaya kalian tetap bisa menulis dan
menguji kode tanpa setup berat, Anggota 1 sudah meng-*export* contoh data ke
folder `sample_data/` (sudah ikut di-commit ke repo ini, tinggal pakai langsung).

Alur kerjanya:
1. Anggota 2 & 3 `git clone` repo ini, lalu **kembangkan & uji kode** memakai
   file-file di `sample_data/` (CSV/JSON kecil, struktur kolomnya identik
   dengan data asli).
2. Setelah kode jalan dengan baik di sample data, `git push` ke repo ini.
3. Anggota 1 `git pull`, lalu menjalankan kode tersebut **di laptopnya**
   (Laptop Utama) di atas data lengkap & live (Docker, SQL Server, dst).
4. Hasil akhir (DuckDB + dashboard Power BI) dihasilkan dari proses nomor 3 ini.

> Kalau ada bug yang hanya muncul di data lengkap (bukan di sample), kalian
> berkumpul sebentar di Laptop Utama untuk debug bersama — ini bagian
> "Fase Integrasi" yang sudah direncanakan dari awal.

### Isi folder `sample_data/`
```
sample_data/
├── sample_dim_product.csv          # ~200 baris produk
├── sample_dim_customer.csv         # ~200 baris pelanggan
├── sample_sales_online_historis.csv  # contoh transaksi online 2011-2014
├── sample_sales_online_stream.csv  # transaksi baru dari faker
├── sample_reviews.json             # ulasan dari marketplace API
└── excel/
    └── sales_*.xlsx                # contoh file toko fisik
```
Struktur kolom di sample ini **sama persis** dengan data asli — hanya jumlah
barisnya lebih sedikit. Kode yang kalian tulis untuk sample ini akan jalan
tanpa ubah apa pun saat dipindah ke data lengkap.

---

## Cara menjalankan infrastruktur (hanya untuk Anggota 1 / Laptop Utama)

> Detail lengkap + troubleshooting ada di **PANDUAN_ANGGOTA1.md**.

**Prasyarat:** Docker Desktop, Python 3.11+, file `AdventureWorks2025.bak`
(unduh dari [SQL Server samples Microsoft](https://github.com/Microsoft/sql-server-samples/releases/tag/adventureworks),
versi OLTP penuh — **bukan** LT/DW).

```bash
# 1. Siapkan environment
cd docker
cp ../.env.example .env

# 2. Taruh AdventureWorks2025.bak ke docker/sqlserver/backup/

# 3. Nyalakan semua service
docker compose up -d
docker compose logs -f sqlserver_init    # tunggu "INIT SELESAI"

# 4. Jalankan faker (mengisi data toko fisik & ulasan)
cd ..
cp .env.example .env
pip install -r requirements.txt
python run_fakers.py --sources all --duration 1

# 5. (Opsional) Perbarui sample_data/ untuk dibagikan ke tim
python export_sample_data.py
git add sample_data/
git commit -m "Update sample data"
git push
```

---

## Kontrak Data (struktur tiap sumber)

### Sumber 1 — Penjualan Online
- **Sample (untuk dev):** `sample_data/sample_sales_online_historis.csv` +
  `sample_data/sample_sales_online_stream.csv`
- **Data asli (di Laptop Utama):** SQL Server `localhost:1433`, DB `AdventureWorks2025`
  - Historis: `Sales.SalesOrderHeader` + `Sales.SalesOrderDetail` (filter `ModifiedDate`)
  - Baru dari faker: tabel `dbo.OnlineOrderStream`
    (kolom: `OrderStreamID, OrderDate, CustomerID, ProductID, OrderQty, UnitPrice, Channel, ModifiedDate`)
  - Master: `Production.Product` (`StandardCost`, `ListPrice`), `Sales.Customer`

### Sumber 2 — Toko Fisik (Excel)
- **Sample:** `sample_data/excel/*.xlsx`
- **Data asli:** folder `watched/excel/*.xlsx` di Laptop Utama
- Kolom: `SalespersonID, StoreID, ProductID, QtySold, UnitPrice, SaleDate, Region`

### Sumber 3 — Ulasan Pelanggan
- **Sample:** `sample_data/sample_reviews.json`
- **Data asli:** `GET http://localhost:8000/reviews/latest?since=<ISO timestamp>`
- Field: `review_id, product_id, customer_id, rating, review_text, language, is_verified, review_date, created_at`

### Watermark
Simpan timestamp terakhir tiap sumber di `state/watermark.json`:
```json
{
  "sales_online": "2026-06-21T05:00:00+00:00",
  "store_excel":  "2026-06-21T05:00:00+00:00",
  "reviews":      "2026-06-21T05:00:00+00:00"
}
```

---

## Tugas yang Tersisa

### Anggota 2 — Ingestion + Silver Layer
Buat folder `pipeline/ingestion/` dan `pipeline/silver/`. Tugas:

1. **Ingestion (→ Bronze):**
   - Baca delta dari 3 sumber pakai watermark (`state/watermark.json`).
   - Untuk dev: baca dari `sample_data/`. Untuk run asli: baca dari SQL Server/
     folder Excel/API langsung (ganti sumber baca saja, logikanya sama).
   - Simpan mentah (tanpa diubah) ke `lake/bronze/<sumber>/` sebagai Parquet.
   - Update `state/watermark.json` setelah sukses.

2. **Silver (bersih & validasi):**
   - Baca Bronze, lakukan: deduplikasi, null-handling, standarisasi tipe data.
   - Aturan bisnis: transaksi valid jika `Quantity > 0` dan `UnitPrice > 0`;
     rating ulasan harus 1–5.
   - Baris yang gagal validasi → pindahkan ke `lake/quarantine/` (jangan dihapus).
   - Hasil bersih → simpan ke `lake/silver/`.

3. **Sentimen:** jalankan NLTK VADER (`SentimentIntensityAnalyzer`) pada kolom
   `review_text` di tahap Silver ulasan → hasilkan kolom `SentimentLabel`
   (POSITIVE/NEUTRAL/NEGATIVE) dan `SentimentConfidence`.

### Anggota 3 — Gold Layer + DuckDB + Power BI
Buat folder `pipeline/gold/`. Tugas:

1. **Gold (Star Schema):** dari Silver, bentuk tabel:
   - `dim_date` (DateKey YYYYMMDD, Date, Week, Month, Quarter, Year)
   - `dim_product` (ProductID, ProductName, ProductNumber, Color, Size, StandardCost, ListPrice, kategori)
   - `dim_customer` (CustomerID, FullName, CustomerType)
   - `fact_sales` (SaleID, FK ke semua dimensi, Quantity, Revenue, Cost, Profit, Channel)
   - `fact_reviews` (ReviewID, FK dimensi, RatingScore, SentimentLabel, SentimentConfidence)
   - `mart_sentiment` (agregat per produk: AvgRating, PosCount, NeutCount, NegCount, TotalReviews)
   - Hitung `Profit = Revenue - Cost`. Cost dari `StandardCost`; jika tidak ada
     (transaksi Excel), pakai default `UnitPrice * 0.6`.
   - Simpan semua tabel ke `lake/gold/` sebagai Parquet.

2. **Load DuckDB:** buat `warehouse/datalake.duckdb`, muat semua tabel Gold:
   ```sql
   CREATE TABLE fact_sales AS SELECT * FROM read_parquet('lake/gold/fact_sales*.parquet');
   ```

3. **Power BI:**
   - Pasang DuckDB ODBC Driver, buat DSN ke `warehouse/datalake.duckdb`
     dengan `access_mode=read_only`.
   - Bentuk relasi Star Schema (filter satu arah, dimensi → fakta).
   - Buat measure DAX: `Total Revenue`, `Total Cost`, `Total Profit`,
     `Profit Margin %`, `Total Sales Count`.
   - Susun visual: bar chart revenue/profit per kategori, trend per tahun,
     donut chart sentimen, scatter plot rating vs profit.

---

## Kredensial default (development lokal, di Laptop Utama)
- SQL Server: user `sa`, password di `.env` (`MSSQL_PASSWORD`), DB `AdventureWorks2025`
- PostgreSQL: `mkuser` / `mkpass123`, DB `marketplace_db`
- Marketplace API: `http://localhost:8000`

## Catatan
File `.bak`, `.env`, dan data lake/warehouse penuh **tidak** disimpan di Git
(lihat `.gitignore`) — hanya `sample_data/` yang sengaja dikecualikan supaya
tim bisa develop tanpa setup berat.
