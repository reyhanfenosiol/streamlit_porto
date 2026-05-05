import os
import duckdb
from google.cloud import bigquery

# key dari google
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:/REYHAN/BOOST ACADEMY/projek_akhir/gcp-key.json"
client = bigquery.Client()

# definisikan nama table
tables = [
    'orders', 'order_items', 'products', 'users', 'inventory_items', 'events'
]

# definisikan data lake
db_path = "D:/REYHAN/BOOST ACADEMY/projek_akhir/duckdb/dev.duckdb"
con = duckdb.connect(db_path)
print("🚀 Memulai proses Ingestion dari BigQuery ke DuckDB...\n")

# mulai jalankan extraction dari google big query
for table in tables:
    print(f"📥 Mengambil tabel: {table}...")

    query = f"SELECT * FROM `bigquery-public-data.thelook_ecommerce.{table}`"

    df = client.query(query).to_dataframe()

    table_name = f"raw_{table}"
    con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
    
    print(f"✅ {table_name} berhasil dibuat ({len(df)} instance).")

print("\n✨ Semua tabel berhasil dipindahkan ke DuckDB!")
con.close()