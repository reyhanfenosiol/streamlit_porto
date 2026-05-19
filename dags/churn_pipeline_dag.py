from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.bash import BashOperator

# Folder mount utama untuk menyimpan semua file yang dibutuhkan
PROJEK_DIR = "/opt/airflow"

# Menggunakan Python bawaan dari image Airflow di dalam kontainer Docker
PYTHON_EXEC = "python3"

default_args = {
    'owner': 'reyhan_mauluddi',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1, 
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'thelook_ecommerce_churn_pipeline',
    default_args=default_args,
    description='Pipeline End-to-End Otomatis (ETL & ML) Churn Prediction untuk Streamlit',
    schedule_interval=None,  # Tidak dijalankan secara otomatis, hanya manual trigger
    catchup=False,
    tags=['churn_prediction', 'thelook_ecommerce', 'end_to_end_pipeline']
) as dag:
    # Task 1: Extract data dari BigQuery ke DuckDB
    extract_task = BashOperator(
        task_id='1_extract_bigquery_to_duckdb',
        bash_command=f"{PYTHON_EXEC} {PROJEK_DIR}/scripts/extract.py"
    )

    # Task 2: Transform data di DuckDB dan simpan hasilnya
    transform_task = BashOperator(
        task_id='2_transform_and_feature_engineering',
        bash_command=f"{PYTHON_EXEC} {PROJEK_DIR}/scripts/transform.py"
    )

    # Task 3: Train model ML dan simpan hasil prediksi
    ml_task = BashOperator(
        task_id='3_ml_retrain_and_predict',
        bash_command=f"{PYTHON_EXEC} {PROJEK_DIR}/scripts/ml.py"
    )

    # Task 4: Push ke github
    github_push_task = BashOperator(
        task_id='4_push_results_to_github',
        bash_command="""
        # 1. Bypass keamanan owner Git untuk folder mount Docker
        git config --global --add safe.directory /opt/airflow
        
        cd /opt/airflow
        
        # 2. Pastikan berada di branch main yang benar
        git checkout main
        
        # 3. Ambil perubahan terbaru dari remote untuk menghindari konflik/rejected refs
        git fetch origin main
        git pull origin main --rebase
        
        # 4. Stage semua file baru atau modifikasi (seperti model_results.csv)
        git add -A
        
        # 5. Commit hanya jika ada perubahan data baru (diperbaiki menggunakan git diff-index)
        git diff-index --quiet HEAD -- || git commit -m "auto-update: churn prediction results $(date +'%Y-%m-%d %H:%M:%S')"
        
        # 6. Push ke origin secara bersih menggunakan SSH
        git push origin main
        """
    )

    # Definisikan urutan eksekusi task
    extract_task >> transform_task >> ml_task >> github_push_task