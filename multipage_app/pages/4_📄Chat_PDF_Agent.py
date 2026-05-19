import os
from dotenv import load_dotenv

import streamlit as st
from langchain_openai import ChatOpenAI
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage


# 1. konfigurasi halaman streamlit
st.set_page_config(
    page_title="PDF Analysis Agent",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI - PDF Analysis Agent")
st.markdown("AI Assistant for analyzing PDF content briefly.")
st.markdown("---")

def set_office_bg():
    img_url = "https://images.unsplash.com/photo-1664882365485-1c5f3983fbf2?q=80&w=1176&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    
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


# 2. load environment variables & data
load_dotenv()

# Gunakan secrets Streamlit jika dideploy, atau fallback ke .env lokal
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY") or st.secrets.get("PINECONE_API_KEY")

if not OPENAI_API_KEY:
    st.error("🔑 OpenAI API Key not found! Please set it in your .env file or Streamlit Secrets.")
    st.stop()

# Fungsi Caching agar koneksi Vector Store tidak dibuat ulang di setiap rerun
@st.cache_resource
def init_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index("growth-europe-2025")
    
    vector_store = PineconeVectorStore(
        index=index,
        embedding=embeddings
    )
    return vector_store.as_retriever(search_kwargs={"k": 3})

retriever = init_vector_store()

# 3. LLM
llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model="gpt-4.1-mini",
    temperature=0.2,
    max_tokens=700
)

@tool("search_pdf_trends")
def search_pdf_trends(query: str) -> str:
    """
    Find market insight and macroeconomic trends from the PDF Growth in European E-Commerce 2025.
    Only use information contained in the document.
    """
    docs = retriever.invoke(query)
    results = []
    for i, doc in enumerate(docs):
        results.append(f"SOURCE {i+1}:\n{doc.page_content[:700]}")
    return "\n".join(results)

tools = [search_pdf_trends]

# 4. Agent
system_prompt = """""
You are an Professor background AI market strategist.

Use only retrieved PDF content.

Rules:
- No fake statistics
- No unsupported assumptions
- State uncertainty clearly
- Give concise macro and market insights
- Respond in user's language

Structure:
1. Market Trend
2. Macro Insight
3. Business Risk
4. Recommendation
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Inisialisasi Agent
agent = llm.bind_tools(tools)

# 5. User interaction
st.subheader("Extract Insights")
default_query = """Analisis market e-commerce dan makroekonomi berdasarkan laporan PDF Growth in European E-Commerce 2025."""

# Teks keterangan kabur (default hint)
st.caption("💡 *The text below is a default query (example). You can run it directly or replace it with your own question.*")

user_query = st.text_area("Enter your question:", value=default_query, height=180)

if st.button("Run Analysis", type="primary"):
    with st.spinner("Analyzing PDF content and generating insights..."):
        try:
            # Gunakan textwrap.dedent atau ketik manual tanpa spasi tab berlebih di awal baris
            system_prompt = (
                "You are an Professor background AI market strategist.\n\n"
                "Use only retrieved PDF content.\n\n"
                "Rules:\n"
                "- No fake statistics\n"
                "- No unsupported assumptions\n"
                "- State uncertainty clearly\n"
                "- Give concise macro and market insights\n"
                "- Respond in user's language\n\n"
                "Structure:\n"
                "1. Market Trend\n"
                "2. Macro Insight\n"
                "3. Business Risk\n"
                "4. Recommendation"
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_query)
            ]

            # Siapkan penanda langkah interaksi
            step_counter = 1
            has_intermediate_steps = False

            # Tulis judul thought process di awal
            st.markdown("### 🧠 Agent Thought Process (Intermediate Steps)")
            
            # Buat placeholder kosong untuk area pemanggilan tool secara dinamis
            steps_placeholder = st.container()

            # Panggilan loop pertama ke Agen
            ai_message = agent.invoke(messages)
            messages.append(ai_message)

            # WHILE LOOP: Terus jalankan tool selama LLM meminta 'tool_calls'
            while ai_message.tool_calls:
                has_intermediate_steps = True
                
                for tool_call in ai_message.tool_calls:
                    with steps_placeholder:
                        with st.expander(f"🔹 STEP {step_counter}: Using Tool `{tool_call['name']}`", expanded=True):
                            st.markdown("**💻 Tool Arguments / Input:**")
                            st.code(tool_call['args'])
                            
                            # Jalankan fungsi RAG secara aman
                            query_arg = tool_call['args'].get('query', user_query)
                            observation = search_pdf_trends.invoke(query_arg)
                            
                            st.markdown("**📄 Observation / Output:**")
                            st.info(observation)
                    
                    # Masukkan output tool ke riwayat pesan
                    messages.append(ToolMessage(content=observation, tool_call_id=tool_call['id']))
                    step_counter += 1
                
                # Minta agen mengevaluasi ulang dokumen yang baru masuk
                ai_message = agent.invoke(messages)
                messages.append(ai_message)

            if not has_intermediate_steps:
                st.write("No intermediate steps taken (answered directly by the LLM).")

            # Ambil teks jawaban akhir dari iterasi paling ujung
            final_output = ai_message.content

            # Berikan jeda pemisah visual, lalu cetak hasil akhir dengan aman
            st.markdown("---")
            st.success("✅ Analysis Completed!")
            st.markdown("### 📝 Answer:")
            st.info(final_output)

        except Exception as e:
            st.error(f"Error during analysis: {e}")