# Sample Data untuk Development

Folder ini berisi CONTOH data kecil (struktur sama dengan data asli) agar
Anggota 2 & 3 bisa menulis & menguji kode ETL tanpa perlu install Docker.

File-file di sini di-generate dengan menjalankan (di laptop Anggota 1):
```bash
python export_sample_data.py
```

Kalau folder ini masih kosong / placeholder, berarti Anggota 1 belum
menjalankan skrip itu — minta dia export & push dulu.

Saat menulis kode, baca dari folder ini dulu untuk development. Path asli
(SQL Server / folder watched/excel / API) baru dipakai saat run di Laptop
Utama untuk hasil final.
