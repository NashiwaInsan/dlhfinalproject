# Panduan Anggota 1 — Infra Engineer & Data Generator

Tanggung jawabmu: menyalakan infrastruktur (Docker), me-restore database,
dan membuat data mengalir lewat faker. Setelah ini hidup, Anggota 2 & 3 baru
bisa mengetes ETL mereka.

## Yang harus dipasang lebih dulu
- Docker Desktop
- Python 3.11+
- File **AdventureWorks2025.bak** (versi penuh/OLTP, **bukan** AdventureWorksLT)

## Struktur proyek
```
aw-lakehouse/
├── docker/
│   ├── docker-compose.yml      # semua service
│   ├── sqlserver/
│   │   ├── restore.sh          # restore .bak otomatis
│   │   ├── online_stream.sql   # tabel untuk faker online
│   │   └── backup/             # TARUH AdventureWorks2025.bak DI SINI
│   └── postgres/init.sql       # tabel reviews
├── marketplace_api/            # FastAPI penerima ulasan
├── fakers/                     # 3 faker daemon
├── config/settings.py          # baca .env
├── watched/excel/              # output faker Excel
├── run_fakers.py               # menjalankan faker
├── requirements.txt
└── .env.example
```

## Langkah demi langkah

### 1. Siapkan environment
```bash
cp .env.example .env
# buka .env, pastikan MSSQL_PASSWORD memenuhi syarat kompleksitas
```

### 2. Letakkan file backup
Salin `AdventureWorks2025.bak` ke `docker/sqlserver/backup/`.
(Namanya harus persis `AdventureWorks2025.bak`, atau ubah di restore.sh.)

### 3. Nyalakan Docker
```bash
cd docker
docker compose up -d
docker compose logs -f sqlserver_init     # tunggu sampai "INIT SELESAI"
```
Container `sqlserver_init` akan otomatis: menunggu SQL Server siap → restore
`.bak` → membuat tabel `dbo.OnlineOrderStream`. Restore butuh beberapa menit.

> Jika muncul error MOVE: lihat output "RESTORE FILELISTONLY" di log, lalu
> samakan nama logical file di `restore.sh` (baris MOVE).

### 4. Cek semuanya hidup
- SQL Server: `localhost:1433` (sa / password .env)
- PostgreSQL: `localhost:5432`
- pgAdmin: http://localhost:5050 (admin@datalake.local / admin123)
- Marketplace API: http://localhost:8000/health  →  {"status":"ok"}

### 5. Pasang dependensi faker & jalankan
```bash
cd ..                    # kembali ke root proyek
pip install -r requirements.txt
python run_fakers.py --sources all --duration 1
```
Yang terjadi:
- `sales_online` → menambah baris ke `dbo.OnlineOrderStream`
- `store_excel`  → membuat file `.xlsx` di `watched/excel/`
- `marketplace`  → POST ulasan ke API → tersimpan di PostgreSQL

Biarkan jalan beberapa menit, lalu Ctrl+C. Verifikasi:
- ada file di `watched/excel/`
- `GET http://localhost:8000/reviews/latest` mengembalikan daftar ulasan
- query `SELECT COUNT(*) FROM dbo.OnlineOrderStream` > 0

### 6. Serah-terima ke tim
Kalau ketiga sumber sudah berisi data, kabari Anggota 2 (ingestion → Silver)
dan Anggota 3 (Gold → DuckDB → Power BI). Mereka membaca dari:
- SQL Server: `Sales.SalesOrderHeader` (historis) + `dbo.OnlineOrderStream` (baru)
- Folder `watched/excel/`
- `GET /reviews/latest?since=<watermark>`

## Catatan keaslian
Kode ini kerangka awal untuk kamu pahami dan ubah, bukan untuk disalin mentah.
Baca tiap file, sesuaikan gaya/penamaan, dan pastikan kamu bisa menjelaskannya.
