import os
import pandas as pd
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_core.messages import HumanMessage, AIMessage  # Ditambahkan untuk kelola history
from dotenv import load_dotenv

# 1. Konfigurasi Halaman & Initialize Session State untuk Memory
st.set_page_config(page_title="Data Analysis Agent", page_icon="📊", layout="wide")


def set_office_bg():
    img_url = "https://images.unsplash.com/photo-1557844681-b0da6a516dc9?q=80&w=1171&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    
    st.markdown(
        f"""
        <style>
        .stApp {{
            /* Gradient gelap agar teks tetap kontras di atas gambar gedung */
            background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.8)), 
                        url("{img_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* Sidebar Glassmorphism */
        [data-testid="stSidebar"] {{
            background-color: rgba(0, 0, 0, 0.7) !important;
            backdrop-filter: blur(12px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }}

        /* Warna teks judul: Putih bersih dengan sedikit glow */
        h1, h2, h3 {{
            color: #ffffff !important;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5);
        }}

        /* Teks pendukung */
        p, span, label {{
            color: #e0e0e0 !important;
        }}

        /* Merapikan kontainer grafik Plotly */
        .stPlotlyChart {{
            background-color: rgba(0, 0, 0, 0.3);
            border-radius: 12px;
            padding: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_office_bg()


# Jika riwayat obrolan belum ada di session, buat list kosong
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("📊 AI - Data Analysis Agent")
st.markdown("AI Assistant for analyzing data statistically and factually.")
st.markdown("---")

# 2. Load Data & Env (Asumsi data sudah aman seperti kode Anda sebelumnya)
load_dotenv()

# Gunakan secrets Streamlit jika dideploy, atau fallback ke .env lokal
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("🔑 OpenAI API Key not found! Please set it up in the .env file or Streamlit Secrets.")
    st.stop()

# Tentukan lokasi CSV
current_dir = os.path.dirname(__file__)
root_path = os.path.abspath(os.path.join(current_dir, ".."))

if os.path.exists("/opt/airflow"):
    BASE_DIR = "/opt/airflow"
else:    
    BASE_DIR = root_path

csv_path = f"{BASE_DIR}/multipage_app/model_results.csv"

# Load Data dengan Caching agar aplikasi cepat saat di-refresh
@st.cache_data
def load_data(path):
    if os.path.exists(path):
        return pd.read_csv(path, encoding="utf-8")
    else:
        st.error(f"📂 File CSV not found at location: {path}")
        return None

df = load_data(csv_path)

# If data loaded successfully, show preview
if df is not None:
    with st.expander("👀 Preview Data"):
        st.dataframe(df.head(10), use_container_width=True)
        st.caption(f"Total baris: {df.shape[0]} | Total kolom: {df.shape[1]}")



# 3. Inisialisasi Model
llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4.1-mini", temperature=0.2)

# 4. CUSTOM PROMPT DENGAN MEMORY PLACEHOLDER
# PENTING: Menambahkan {chat_history} agar agent tahu konteks percakapan sebelumnya
CUSTOM_PREFIX = """You are a Professor background AI assistant that provides answers to questions by using fact-based and statistical information derived from the dataframe.
The response must be specific, concise, and use statistics or numbers whenever possible.
If you cannot find the answer or if it's not present in the dataframe, just say that you don't know, do not try to make up an answer.
Always answer using the exact same language as the user's question.

Previous conversation history:
{chat_history}"""

agent = create_pandas_dataframe_agent(
    llm=llm,
    df=df,
    verbose=True,
    allow_dangerous_code=True,
    prefix=CUSTOM_PREFIX,
    handle_parsing_errors=True,
    agent_type="tool-calling",
    return_intermediate_steps=True
)

# 5. TAMPILKAN RIWAYAT CHAT YANG SUDAH TERJADI (Gaya Chatbot Modern)
st.subheader("💬 Conversation Logs")
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.info(message.content)

st.markdown("---")

# 6. INPUT UNTUK PERTANYAAN BARU / MENYAMBUNG
st.subheader("🔍 Ask a new question or follow-up")

default_query = """Berapa total customer seluruhnya. Jelaskan customer di Brasil secara general mulai dari total customer, presentase churn dan tidak churn beserta prediksinya? Lalu inspeksi karakter customer yang churn dan tidak. Teliti kembali jawabanmu di akhir."""

# Teks petunjuk dinamis: jika sudah ada history, ingatkan user bisa tanya menyambung
if len(st.session_state.chat_history) > 0:
    st.caption("💡 *You can now type a follow-up question to continue the conversation based on the answer above.*")
else:
    st.caption("💡 *The text below is a default query (example). You can run it directly or replace it.*")

user_query = st.text_area("What would you like to analyze?", value="" if len(st.session_state.chat_history) > 0 else default_query, height=180)

# Kolom aksi: Tombol kirim & Tombol Reset Memory jika ingin ganti topik baru
col1, col2 = st.columns([1, 5])
with col1:
    submit_button = st.button("Run Analysis", type="primary")
with col2:
    if st.button("🗑️ Clear History"):
        st.session_state.chat_history = []
        st.rerun()

# 7. PROSES RUN ANALYSIS (MODIFIKASI SESUAI KEINGINAN ANDA)
if submit_button and user_query:
    with st.spinner("Analyzing data and calculating statistics..."):
        try:
            # Jalankan agent dengan menyertakan chat_history saat ini
            response = agent.invoke({
                "input": user_query,
                "chat_history": st.session_state.chat_history
            })
            
            # 1. TAMPILKAN LANGKAH LOGIKA TERLEBIH DAHULU (Intermediate Steps)
            st.markdown("### 🧠 Agent Thought Process (Intermediate Steps)")
            
            if response.get("intermediate_steps"):
                for i, step in enumerate(response["intermediate_steps"], start=1):
                    action, observation = step
                    with st.expander(f"🔹 STEP {i}: Using Tool `{action.tool}`", expanded=True):
                        st.markdown("**💻 Python Code / Input:**")
                        st.code(action.tool_input, language="python")
                        st.markdown("**📊 Execution / Observation:**")
                        st.code(observation)
            else:
                st.write("No intermediate steps taken (answered directly by the LLM).")
            
            st.markdown("---")
            
            # 2. TAMPILKAN JAWABAN AKHIR (Final Output)
            st.success("✅ Analysis Completed!")
            st.markdown("### 📝 Current Answer:")
            st.info(response["output"])
            
            # 3. SIMPAN KE MEMORY: Masukkan chat baru ini ke dalam riwayat session_state
            st.session_state.chat_history.append(HumanMessage(content=user_query))
            st.session_state.chat_history.append(AIMessage(content=response["output"]))
            
            # Memicu rerun kecil agar log obrolan di bagian atas otomatis terupdate
            st.rerun()
                
        except Exception as e:
            st.error(f"An error occurred while processing the data: {e}")