# 📊 E-Commerce End-to-End Data Pipeline, Churn Analytics and AI Analyst Agent

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge.svg)](https://my-porto-reyhanmauluddi.streamlit.app/)

Welcome to my portfolio repository. This project integrates a large-scale automated data pipeline with an interactive analytics dashboard designed to predict customer churn and uncover loyal customer behavior for a fast-growing e-commerce startup integrated with an AI Analyst Agent for reasoning across both structured transaction data and unstructured PDF reports to deliver prescriptive business insights.

🔗 **Live Dashboard:** [Mochammad Reyhan Mauluddi Portfolio](https://my-porto-reyhanmauluddi.streamlit.app/)

---

## 📌 Project Overview

### 🔹 Background
* **Company Profile:** A fast-growing e-commerce startup scaling operations globally since 2019.
* **Product Scale:** Manages an extensive portfolio covering 26 product categories and over 2,700 brand variations.
* **Market Reach:** Successfully recorded more than 100,000 transactions across 15 countries, serving a broad customer demographic (aged 12–70).

### 🔹 Challenges
* ⚠️ **Data Scalability:** Rapidly growing data volumes demand an optimized reporting architecture.
* ⚠️ **Pipeline Requirements:** Need to build an automated architecture from raw sources in Google BigQuery to final visualization.
* ⚠️ **Retention Analysis:** Deriving actionable insights from loyal customer behavior to minimize churn.
* ⚠️ **Real-Time Prediction:** Empowering the Head of Operational to monitor churn probabilities seamlessly.

### 🔹 Solutions
* ✔ **Automated Data Pipeline:** Integrated Google BigQuery, Apache Airflow, and Streamlit Cloud for a scheduled data pipeline.
* ✔ **Comprehensive Framework Dashboard:** An interactive dashboard with analytical capabilities:
  * *Descriptive Analytics:* Visualizing historical transactions and demographics.
  * *Diagnostic Analytics:* Identifying root causes behind customer churn behavior.
  * *Prescriptive Analytics & AI Agent:* Utilizing a **RAG-based AI Chatbot Agent** for narrative data context.

---

## 🚀 Key Results & Impact

* ✅ **200% Workflow Efficiency:** Shifted from manual coding to a fully automated pipeline (Extract, Transform, Visualize).
* ✅ **Non-Technical Accessibility:** Analytics utilized by non-technical users through real-time interactive visualizations.
* ✅ **Security & Deployment:** Deployed via **Docker** and **Airflow** on a private server for security and scheduling.
* ✅ **AI-Powered Assistant:** Integrated **RAG (Retrieval-Augmented Generation)** agents to translate complex datasets into narrative business insights.

---

## 🛠️ Technical Stack & Architecture

| Component | Technology |
| :--- | :--- |
| **Core Language** | Python |
| **Data Source** | Google Big Query, GCP Key Integration |
| **Data Processing** | Pandas, NumPy, DuckDB |
| **Machine Learning & Modelling** | Scikit-Learn, Joblib |
| **AI & RAG Framework** | LangChain, OpenAI (GPT models), Pandas AI Agent, Pinecone |
| **Automation & DevOps** | Apache Airflow, Docker, Docker Compose, Git & Github |
| **Visualization** | Streamlit Cloud, Plotly Express |
| **Development Environment** | Visual Studio Code (VS Code) |

---

## 📂 Repository Structure

```text
├── dags/                       # Airflow DAGs (churn_pipeline_dag.py)
├── multipage_app/              # Streamlit Application
│   ├── pages/                  # App Pages (Analysis, Churn Prediction, Chat Analyst, etc.)
│   ├── assets/                 # mp3 for music background in profile/about me
├── scripts/                    # Core logic (Extract, Transform, ML, RAG)
│   ├── rag_ingestion.py        # Vector ingestion (Upserting data to Pinecone)
│   ├── extract.py              # Extraction data from Google Big Query
|   ├── transform.py            # Data cleaning, transformation and enrichment
│   └── ml.py                   # Machine learning implementation
├── docker-compose.yaml         # Docker orchestration
├── Dockerfile                  # Container configuration
├── airflow.cfg                 # Airflow environment settings
├── gcp-key.json                # GCP Authentication (Restricted)
├── requirements.txt            # Python dependencies
└── requirements-airflow.txt    # Python dependencies for Airflow DAGs