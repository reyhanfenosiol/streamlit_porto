from datetime import datetime, timedelta
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
        # 1. Mengamankan jabat tangan host GitHub
        mkdir -p /tmp/.ssh && chmod 700 /tmp/.ssh && \
        ssh-keyscan -t rsa github.com >> /tmp/.ssh/known_hosts && \
        
        # 2. Set environment variable SSH agar menggunakan id_rsa yang valid
        export GIT_SSH_COMMAND="ssh -i /home/airflow/.ssh/id_rsa -F /dev/null -o UserKnownHostsFile=/tmp/.ssh/known_hosts" && \
        
        # 3. Masuk ke root folder dags tempat repositori git Anda berada
        cd /opt/airflow/dags && \
        
        # 4. Jalankan proses Git Push ke branch main
        git add . && \
        git commit -m "auto-update: churn prediction results $(date +'%Y-%m-%d %H:%M:%S')" || echo "No changes to commit" && \
        git push origin main
        """,
    )

    # Definisikan urutan eksekusi task
    extract_task >> transform_task >> ml_task >> github_push_task