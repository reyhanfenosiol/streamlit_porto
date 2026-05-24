import os
import pandas as pd
# from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv


# 1. Load environment variables
load_dotenv()
# groq_api_key = os.environ["GROQ_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# 2. Tentukan lokasi CSV (menyesuaikan lokal vs airflow seperti kode Anda sebelumnya)
if os.path.exists("/opt/airflow"):
    BASE_DIR = "/opt/airflow"
else:    
    BASE_DIR = "D:/REYHAN/BOOST ACADEMY/projek_akhir"

csv_path = f"{BASE_DIR}/multipage_app/model_results.csv"

# 3. Load data menggunakan pandas (Gunakan encoding utf-8 agar aman)
df = pd.read_csv(csv_path, encoding="utf-8")

# 4. Inisialisasi model
# llm = ChatGroq(
#     groq_api_key=groq_api_key, 
#     model_name='llama-3.3-70b-versatile', 
#     temperature=0,
#     max_tokens=2048
#     )
llm = ChatOpenAI(
    api_key=OPENAI_API_KEY, 
    model="gpt-4.1-mini", 
    temperature=0.2,
    max_tokens=2048
    )

# 5. Buat Pandas DataFrame Agent
# Catatan: Gunakan prefix_prompt untuk memaksa LLM menjawab dalam Bahasa Indonesia
CUSTOM_PREFIX = """You are a Professor background AI assistant that provides answers to questions by using fact-based and statistical information derived from the dataframe.
The response must be specific, concise, and use statistics or numbers whenever possible.
If you cannot find the answer or if it's not present in the dataframe, just say that you don't know, do not try to make up an answer.
Always answer using the exact same language as the user's question (e.g., if the user asks in Indonesian, answer in Indonesian)."""

agent = create_pandas_dataframe_agent(
    llm=llm,
    df=df,
    verbose=True,
    allow_dangerous_code=True,
    prefix=CUSTOM_PREFIX,  # Masukkan ke parameter prefix
    handle_parsing_errors=True,
    agent_type="tool-calling",
    return_intermediate_steps=True
)

# 6. Jalankan pertanyaan hitungan atau statistik
query = f"""
Berapa total customer seluruhnya. Jelaskan customer di Brasil secara general mulai dari total customer, 
presentase churn dan tidak churn beserta prediksinya? 
Lalu inspeksi karakter customer yang churn dan tidak.
Teliti kembali jawabanmu di akhir. 
"""


response = agent.invoke({"input": query})
print("\n=== FINAL OUTPUT ===\n")
print(response["output"])

print("\n=== INTERMEDIATE STEPS ===\n")

for i, step in enumerate(response["intermediate_steps"], start=1):

    action, observation = step

    print(f"\n🔹 STEP {i}")

    print(f"• Tool      : {action.tool}")
    print(f"• Input     : {action.tool_input}")

    print("• Observation:")
    print(f"  {observation}")