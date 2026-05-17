# Langkah 1: Tentukan "bahan dasar" (Base Image)
FROM apache/airflow:2.8.1-python3.10

# Langkah 2: Pindah ke user root untuk menginstall library sistem Linux
USER root

# Langkah 3: Install dependensi sistem yang dibutuhkan oleh LightGBM dan Git untuk push pipeline
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Langkah 4: Kembalikan ke user airflow demi keamanan
USER airflow