import os
import sys
import duckdb
from google.cloud import bigquery

# key dari google
if os.path.exists("/opt/airflow"):
    BASE_DIR = "/opt/airflow"  # untuk airflow
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f"{BASE_DIR}/gcp-key.json"
else:
    BASE_DIR = "D:/REYHAN/BOOST ACADEMY/projek_akhir"  # untuk lokal
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f"{BASE_DIR}/gcp-key.json"

db_path = f"{BASE_DIR}/duckdb/dev.duckdb"

# Verifikasi key GCP ditemukan sebelum lanjut ke BigQuery
if not os.path.exists(os.environ["GOOGLE_APPLICATION_CREDENTIALS"]):    
    print(f"❌ Gagal menemukan file key GCP di {os.environ['GOOGLE_APPLICATION_CREDENTIALS']}. Pastikan path sudah benar.")
    sys.exit(1)



# pipeline ingestion data dari big query ke duckdb
client = bigquery.Client()
# definisikan nama table
tables = [
    'orders', 'order_items', 'products', 'users', 'inventory_items'
]

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