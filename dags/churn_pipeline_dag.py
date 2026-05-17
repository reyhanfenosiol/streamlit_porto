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
        # 1. Setup sandbox SSH di /tmp (Aman dari isu permission)
        mkdir -p /tmp/.ssh && chmod 700 /tmp/.ssh && \
        ssh-keyscan -t rsa github.com >> /tmp/.ssh/known_hosts && \
        
        # 2. Bongkar Kunci Privat dari Base64
        # Kami menggunakan <<< "$SSH_KEY_B64" agar format literal terjaga
        base64 -d <<< "$SSH_KEY_B64" > /tmp/.ssh/id_rsa_tmp && \
        chmod 600 /tmp/.ssh/id_rsa_tmp && \
        
        # 3. Konfigurasi SSH Git agar mengabaikan config bawaan container yang rusak
        export GIT_SSH_COMMAND="ssh -i /tmp/.ssh/id_rsa_tmp -F /dev/null -o UserKnownHostsFile=/tmp/.ssh/known_hosts -o IdentitiesOnly=yes -o StrictHostKeyChecking=no" && \
        
        # 4. Debug: Tes koneksi ke GitHub
        echo "=== Mengetes Koneksi SSH ke GitHub ===" && \
        $GIT_SSH_COMMAND -T git@github.com || echo "Koneksi berhasil diverifikasi." && \
        echo "======================================" && \
        
        # 5. Eksekusi Git Push
        cd /opt/airflow/dags && \
        git add . && \
        git commit -m "auto-update: churn prediction results $(date +'%Y-%m-%d %H:%M:%S')" || echo "No changes to commit" && \
        git push origin main;
        
        # 6. Cleanup kunci rahasia
        EXIT_CODE=$?; \
        rm -rf /tmp/.ssh/id_rsa_tmp; \
        exit $EXIT_CODE
        """,
        env={
            **os.environ,
            "SSH_KEY_B64": "LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnphQzFyWlhrdGRqRUFBQUFBQkc1dmJtVUFBQUFFYm05dVpRQUFBQUFBQUFBQkFBQUJsd0FBQUFkemMyZ3RjbgpOaEFBQUFBd0VBQVFBQUFZRUF1SlpNTlN0djQzd0VaZXl2NEJHMzdzanNneEdubDlwRFhQc2V1aGpxV29XL2lYNmYzclNsCjFlbmx6Qm9WcE1hYThaUkdrWGRiWm9ROUxjaUpHUUtEVFZ4KzY3RW1DdVlzYXBUTkFFOWZPa0xQcHJTbGpxeEgxY2JnRW0Kam9sUFhYQS9WN3ZicnJvYVZwYzFISUtOQkgzM2duTVJhbmZYR0k0czJFR3VnVDNWc3pqK1B6SFk4VWN5Y0c4aGFOdTBiaApYZy9YU0pURmRuVzJxREJBN3BzYVZRa0l6TFBybTNlQW9PVXdSa3BYcERkdEhJNHFXNk5UcUZCTXRPZ21pSTc5aHVEYjllCmY4SnRsSWtUTjIyUjNuSmFTS1YxZkdSem1QZHFJampWSHhubElUdkpjZW5JcUkrMmNkUjZzOXcydk9ORDhZS2pJaHZsREMKSkx1dUdZa1F5d21iMlZHcmlXSG1JdFVWV1VSQUtsUk5Wc01tODNZd3oxaHRQS2kzOXRYS1lIUGJ1UmswNXVhaDlRTmxvQwpWN3Z5c25ES2JNeENCQXRoOGhLdWJWNEhRclM4OTdvYk5haDFUU2F1cGpOVEpSUU13ZllaSUp0QlhBK3hKTWg3d2xLTitGCldZTTF1dlhacCtkOHY0cHNjTFBNOXVzYS9GZk00YVhCZEhEUWIwOUJBQUFGa0s5K2xQMnZmcFQ5QUFBQUIzTnphQzF5YzIKRUFBQUdCQUxpV1REVXJiK044QkdYc3IrQVI5KzdJN0lNUnA1ZmFRMXo3SHJvWTZscUZ2NGwrbjk2MHBkWHA1Y3dhRmFURwptdkdVUnBGM1cyYUVQUzNJaVJrQ2cwMWNmdXV4SmdybUxHcVV6UUJQWHpwQ3o2YTBwWTZzUjlYRzRCSm82SlQxMXdQMWU3CjI2NjZHbGFYTlJ5Q2pRUjk5NEp6RVdwMzF4aU9MTmhCcm9FOTFiTTQvajh4MlPFSE1uQnZJV2pidEc0VjRQMTBpVXhYWjEKdHFnd1FPNmJHbFVKQ015ejY1dDNnS0RsTUVaS1Y2UTNiUnlPS2x1alU2aFFUTFRvSm9pTy9ZYmcyL1huL0NiWlNKRXpkdAprZDV5V2tpbGRYeGtjNWozYWlJNDFSOFo1U0U3eVhIcHlLaVB0bkhVZXJQY05yempRL0dDb3lJYjVRd2lTN3JobUpFTXNKCm05bFJxNGxoNWlMVkZWbEVRQ3BVVFZiREp2TjJNTTlZYlR5b3QvYTF4bUJ6MjdrWk5PYm1vZlVEWmFBbGU3OHJKd3ltek0KUWdRTFlmSVNybTFlQjBLMHZQZTZHeldvZFUwbXJxWXpVeVVVRE1IMkdTQ2JRVndQc1NRSWV4SlNqZmhWbUROYnIxMmFmbgpmTCtLYkhDenpQYnJHdnhYek9HbHdYUncwRzlQUVFBQUFBTUJBQUVBQUFHQkFMTjBrNlNCbFdjQmREa3ZjaEdUQm9zazFpClBiTHllSDhFUGVkSklTbFF6cXlUdEFXdWNtazYremxWRG43ekRpVVZNYWg3ejI0R3A3bUFzQjBwLzQvSFJpdjVZZkJOQkYKMU5yTnpieEdibHR6QnZTWTNmZ21jRFJiQkErQjVOU2xhYVFVcm5mWDJTdXZhQ1RRVnB1dldxRGM3S1ZoMC9ZMlFoSFdJbQpBU1R2VytyQk54VnpQZW5kQVNHa09VUDdqYUFWTDBiYVhIMVc0RXBVOUFrbkFuWk9OVlJEUFhtL0RxcnFnK0NiL2NtUFl6CldLWVJaUWJ3YyszSUc3c3BsQVRobGR6UGhDRkxpUlNBQzFEK0J2RzhPMGhBRUhNRWpSb2QyaWNkVzhWM0xXc25hcEZFcDcKQ3JIL2p6NTNmMzNMWUFqbWFRT2c5SmdMRFkvTHN0QXNzT1JXVTd3QVF3YzFlSjM5T1NhbmNJdm5wU29HRUJrSWlzQ3RMSApEQmN0emJhR1VxUXJSUGNlVVZwUnhxRU1NNlRML25lUkpJcEFoeUMvRG9GekhZVk9uNVViNTVUMlNwVzRpa2s2R21hMkNICm5CaXV0UzduSlc0dXRaL3NLNWlQOXYzMmVvVEREUVF4bW9sZmpWaE9hODdBcm5QQ0JmKytzbjZkbVcyN1kyRTBCdURRQUEKQU1BcXZXZlNZY3BadUlUWmdOaDJtZ1EyaTJLNjhwbmFJd0tBTTBMeEUyeE5sbTBtUk4xMDhmbUdWK3I5T3hXTlEwQ0o3OApmLzJvMVFZbyt2VGtOeGlGSTlCblZkZk5XOXF0QTRkR3V1NHFtenhYL1hjOGlNTXNWdkVkQi8zNVdOM1RqUm0rTmg3UVRICjN6bGVHU002cnRWZWxjY055alhHdVlISDlBeGJlYTZuTS9JcEkybmZRaFVlVVFxTWpZT0xIVUZ2d25oSk1qMWpDWFkrcGoKUTk4TTN5VnhMNzZVVnoxVktyd21RUVZpS2xrbXZvblJKNjJZQnp6MUY5TVpkeHpiRUFBQURCQU9MM3phL1l2TXdNQUxwegp4TnFUVy9uWGdiSDJVL05idEMzOXZVRGovZmdDT3lySG9vdERKdG42aCtIUlFJd2F6TlVFcFdORVpzREcvZ01Ld0N0NWdPCkI4T2s0bEpRZ05sd0JsVU9mRHZITXR5UC9YQmFJb1lod1NkeHk2THdaT1JmQXk2UWlLUjFtS0t2RDRaY3lGK2dYb3Q0NUMKamNvY3A0c2UzUTAwVy95ZVZLMTNQSkNRaFB0UXd6SzRzdm5CSWZ3dlhqalladUkxL0VQbVl4ZDh1aGZtTVgyci80bUN5YwpYMGhtK2Qxa1FocGlKdTVNSVlDeEdxaVJLT21DbUVqd0FBQU1FQTBESzFQZkRVblgrV1hsQ3NVM1ZvMGZpMG1HeEdPb0tJClp4NnZRcG9ZeUJ4dkpDOTMzaFJmcEtjc3dKczVFQ2syN1EycGxEeVU1ME9seDZDSldwRldtVldCMlFYUnBOS1EzcFRhTTkKU2VkbGRvYWFOUTFBWVQrVGFYOEw3KzR4S2lsN1d6Q21yV1c3MWRWNWlBc0VGSlBlMkljNGJsRUNqeGtFY05yUWJnWFFab2FasWxuQnNDSzJtS085WmJZUkhTUHc1aHBnL2I0NVhXdUlkRWptd3dzMFVVM3F2bEtCZlNPdnJGSEJpbi80aUNOTnluK0QKQUNek1DS3IwRElkdmN2QUFBQUZXRTBNRGxwUUZKbGVXaGhibDlOWVhWc2RXUmthUUVDQXdRRgotLS0tLUVORCBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0K"
        }
    )

    # Definisikan urutan eksekusi task
    extract_task >> transform_task >> ml_task >> github_push_task