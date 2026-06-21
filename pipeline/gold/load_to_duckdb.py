import duckdb
from pathlib import Path

def load_to_warehouse():
    print("Mulai memuat data Parquet ke DuckDB...")
    
    # Buat folder warehouse jika belum ada sesuai instruksi
    Path("warehouse").mkdir(exist_ok=True)
    
    # Buka/buat koneksi ke database lokal
    con = duckdb.connect("warehouse/datalake.duckdb")
    
    # Daftar tabel target
    tables = [
        "dim_product", 
        "dim_customer", 
        "dim_date", 
        "fact_sales", 
        "fact_reviews", 
        "mart_sentiment"
    ]
    
    for table in tables:
        # CREATE OR REPLACE digunakan agar aman jika Anda tidak sengaja menjalankan skrip ini dua kali
        query = f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_parquet('lake/gold/{table}.parquet');"
        con.execute(query)
        print(f"  -> Tabel {table} berhasil dimuat.")
        
    con.close()
    print("SELESAI! File warehouse/datalake.duckdb sudah jadi dan siap ditarik ke Power BI.")

if __name__ == "__main__":
    load_to_warehouse()