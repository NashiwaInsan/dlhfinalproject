import pandas as pd
import numpy as np
from pathlib import Path
import os

def build_gold_layer():
    print("=" * 50)
    print("MEMBANGUN GOLD LAYER (STAR SCHEMA)")
    print("=" * 50)

    # Buat folder output jika belum ada
    gold_dir = Path("lake/gold")
    gold_dir.mkdir(parents=True, exist_ok=True)

    # =====================================================
    # 1. BACA DATA SUMBER (SILVER & SAMPLE DIMENSI)
    # =====================================================
    print("1. Membaca data Silver dan Dimensi...")
    
    # Dimensi dari sample_data
    dim_product = pd.read_csv("sample_data/sample_dim_product.csv")
    dim_customer = pd.read_csv("sample_data/sample_dim_customer.csv")
    
    # Tambahkan kolom kategori statis jika tidak ada di CSV untuk memenuhi kontrak
    if 'Category' not in dim_product.columns:
        dim_product['Category'] = 'Uncategorized'

    # Silver Data
    online_sales = pd.read_parquet("lake/silver/online_sales/online_sales_clean.parquet")
    store_sales = pd.read_parquet("lake/silver/store_sales/store_sales_clean.parquet")
    reviews = pd.read_parquet("lake/silver/reviews/reviews_sentiment.parquet")

    # =====================================================
    # 2. TRANSFORMASI FACT_SALES
    # =====================================================
    print("2. Memproses fact_sales...")
    
    # --- Proses Online Sales ---
    # Samakan nama kolom
    online_sales = online_sales.rename(columns={
        'OrderQty': 'Quantity',
        'ModifiedDate': 'TransactionDate'
    })
    
    # Fungsi Surrogate Key untuk Online
    def generate_online_saleid(row):
        if 'OrderStreamID' in row and pd.notna(row['OrderStreamID']):
            return f"ON-STREAM-{int(row['OrderStreamID'])}"
        elif 'SalesOrderID' in row and pd.notna(row['SalesOrderID']):
            return f"ON-{int(row['SalesOrderID'])}-{int(row['ProductID'])}"
        else:
            return f"ON-UNKNOWN-{row.name}"
            
    online_sales['SaleID'] = online_sales.apply(generate_online_saleid, axis=1)
    # Channel sudah "Online" dari faker
    
    # --- Proses Store Sales (Excel) ---
    store_sales = store_sales.rename(columns={
        'QtySold': 'Quantity',
        'SaleDate': 'TransactionDate'
    })
    store_sales['Channel'] = 'Store'
    # Fallback SaleID untuk Excel karena nama file tidak diekstrak di Silver
    store_sales['SaleID'] = "OFF-STORE-" + store_sales.index.astype(str)
    store_sales['CustomerID'] = 0 # Excel tidak punya data pelanggan, set ke 0 (Unknown)

    # --- Gabungkan (Union) Fakta Penjualan ---
    cols_to_keep = ['SaleID', 'TransactionDate', 'ProductID', 'CustomerID', 'Quantity', 'UnitPrice', 'Channel']
    
    # Handle kolom yang mungkin hilang (mengamankan concat)
    for col in cols_to_keep:
        if col not in online_sales.columns: online_sales[col] = np.nan
        if col not in store_sales.columns: store_sales[col] = np.nan

    fact_sales = pd.concat([online_sales[cols_to_keep], store_sales[cols_to_keep]], ignore_index=True)
    fact_sales['TransactionDate'] = pd.to_datetime(fact_sales['TransactionDate'])
    
    # --- Kalkulasi Metrik (Revenue, Cost, Profit) ---
    fact_sales['Revenue'] = fact_sales['Quantity'] * fact_sales['UnitPrice']
    
    # Ambil StandardCost dari dim_product
    fact_sales = fact_sales.merge(dim_product[['ProductID', 'StandardCost']], on='ProductID', how='left')
    
    # Logika Cost: Pakai StandardCost, jika null (seperti transaksi excel yang produknya tidak ada di master) pakai UnitPrice * 0.6
    cost_per_unit = np.where(fact_sales['StandardCost'].isna(), fact_sales['UnitPrice'] * 0.6, fact_sales['StandardCost'])
    fact_sales['Cost'] = fact_sales['Quantity'] * cost_per_unit
    fact_sales['Profit'] = fact_sales['Revenue'] - fact_sales['Cost']
    
    # Buat DateKey
    fact_sales['DateKey'] = fact_sales['TransactionDate'].dt.strftime('%Y%m%d').astype(int)
    
    # Bersihkan kolom yang tidak diperlukan di fact table akhir
    fact_sales = fact_sales[['SaleID', 'DateKey', 'ProductID', 'CustomerID', 'Quantity', 'Revenue', 'Cost', 'Profit', 'Channel']]

    # =====================================================
    # 3. TRANSFORMASI FACT_REVIEWS
    # =====================================================
    print("3. Memproses fact_reviews...")
    reviews = reviews.rename(columns={
        'review_id': 'ReviewID',
        'product_id': 'ProductID',
        'customer_id': 'CustomerID',
        'rating': 'RatingScore',
        'created_at': 'ReviewDate'
    })
    reviews['ReviewDate'] = pd.to_datetime(reviews['ReviewDate'])
    reviews['DateKey'] = reviews['ReviewDate'].dt.strftime('%Y%m%d').astype(int)
    
    fact_reviews = reviews[['ReviewID', 'ProductID', 'CustomerID', 'DateKey', 'RatingScore', 'SentimentLabel', 'SentimentConfidence']]

# =====================================================
    # 4. MEMBANGUN DIM_DATE
    # =====================================================
    print("4. Membangun dim_date...")
    
    # Standardisasi format waktu (buang timezone) sebelum digabung
    date_online = pd.to_datetime(online_sales['TransactionDate'], utc=True).dt.tz_localize(None).dt.normalize()
    date_store = pd.to_datetime(store_sales['TransactionDate'], utc=True).dt.tz_localize(None).dt.normalize()
    date_reviews = pd.to_datetime(reviews['ReviewDate'], utc=True).dt.tz_localize(None).dt.normalize()

    all_dates = pd.concat([date_online, date_store, date_reviews]).drop_duplicates().dropna()

    dim_date = pd.DataFrame({'Date': all_dates})
    dim_date['DateKey'] = dim_date['Date'].dt.strftime('%Y%m%d').astype(int)
    dim_date['Week'] = dim_date['Date'].dt.isocalendar().week.astype(int)
    dim_date['Month'] = dim_date['Date'].dt.month
    dim_date['Quarter'] = dim_date['Date'].dt.quarter
    dim_date['Year'] = dim_date['Date'].dt.year

    # =====================================================
    # 5. MEMBANGUN MART_SENTIMENT
    # =====================================================
    print("5. Membangun mart_sentiment (Agregasi)...")
    mart_sentiment = fact_reviews.groupby('ProductID').agg(
        TotalReviews=('ReviewID', 'count'),
        AvgRating=('RatingScore', 'mean'),
        PosCount=('SentimentLabel', lambda x: (x == 'POSITIVE').sum()),
        NeutCount=('SentimentLabel', lambda x: (x == 'NEUTRAL').sum()),
        NegCount=('SentimentLabel', lambda x: (x == 'NEGATIVE').sum())
    ).reset_index()
    mart_sentiment['AvgRating'] = mart_sentiment['AvgRating'].round(2)

    # =====================================================
    # 6. SIMPAN SEMUA KE PARQUET (LAKE/GOLD/)
    # =====================================================
    print("6. Menyimpan tabel Gold sebagai Parquet...")
    
    datasets = {
        "dim_product": dim_product,
        "dim_customer": dim_customer,
        "dim_date": dim_date,
        "fact_sales": fact_sales,
        "fact_reviews": fact_reviews,
        "mart_sentiment": mart_sentiment
    }
    
    for name, df in datasets.items():
        output_path = gold_dir / f"{name}.parquet"
        df.to_parquet(output_path, index=False)
        print(f"   [OK] {name}.parquet ({len(df)} baris)")

    print("=" * 50)
    print("GOLD LAYER SELESAI!")
    print("=" * 50)

if __name__ == "__main__":
    build_gold_layer()