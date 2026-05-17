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
        # 1. Buat sandbox SSH yang bersih di /tmp (100% dikontrol user airflow)
        mkdir -p /tmp/.ssh && chmod 700 /tmp/.ssh && \
        ssh-keyscan -t rsa github.com >> /tmp/.ssh/known_hosts && \
        
        # 2. Salin private key ke sandbox dan amankan permission-nya menjadi 600
        cp /home/airflow/.ssh/id_rsa /tmp/.ssh/id_rsa_tmp && \
        chmod 600 /tmp/.ssh/id_rsa_tmp && \
        
        # 3. Set opsi SSH agar mengabaikan config global (-F /dev/null) 
        # dan arahkan ke kunci privat yang bersih di /tmp
        export GIT_SSH_COMMAND="ssh -i /tmp/.ssh/id_rsa_tmp -F /dev/null -o UserKnownHostsFile=/tmp/.ssh/known_hosts -o IdentitiesOnly=yes" && \
        
        # 4. Jalankan Tes Koneksi ke GitHub untuk memastikan jabat tangan berhasil
        echo "=== Mengetes Koneksi SSH ke GitHub ===" && \
        $GIT_SSH_COMMAND -T git@github.com || echo "Status tes SSH selesai." && \
        echo "======================================" && \
        
        # 5. Masuk ke root folder dags tempat repositori git Anda berada
        cd /opt/airflow/dags && \
        
        # 6. Jalankan proses Git Commit dan Push
        git add . && \
        git commit -m "auto-update: churn prediction results $(date +'%Y-%m-%d %H:%M:%S')" || echo "No changes to commit" && \
        git push origin main; \
        
        # 7. Bersihkan kunci temporer dari /tmp demi keamanan
        EXIT_CODE=$?; \
        rm -rf /tmp/.ssh/id_rsa_tmp; \
        exit $EXIT_CODE
        """,
    )

    # Definisikan urutan eksekusi task
    extract_task >> transform_task >> ml_task >> github_push_task