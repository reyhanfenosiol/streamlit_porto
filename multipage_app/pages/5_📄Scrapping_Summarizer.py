import streamlit as st
import requests
from newspaper import Article
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Streamlit Page Configuration
st.set_page_config(page_title="Multi-page Article Summarizer", page_icon="📰", layout="wide")
st.title("📰 Multi-page Article Summarizer")
st.markdown("Scrape multi-page web articles and automatically generate an AI summary.")


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
        
        .scrollable-summary-box {{
            height: 450px;
            overflow-y: auto;
            padding: 20px;
            background-color: #1e1e1e !important; 
            
            /* PERBAIKAN: Border kuning terang + Efek Glow halus agar mata langsung tertuju ke sini */
            border: 2px solid #FFFF00 !important;  
            box-shadow: 0 0 15px rgba(255, 255, 0, 0.2); 
            
            border-radius: 10px;
            color: #ffffff !important;
            white-space: pre-wrap;
            font-size: 15px;
            line-height: 1.6;
        }}

        /* Tambahan pengaman: Memastikan semua elemen teks di dalam box kustom ini dipaksa menjadi putih murni */
        .scrollable-summary-box *, .scrollable-summary-box p, .scrollable-summary-box span {{
            color: #ffffff !important;
        }}

        .scrollable-content-box {{
            height: 450px;            /* Tinggi disamakan agar seimbang */
            overflow-y: auto;         /* Otomatis memunculkan scroll vertikal */
            padding: 20px;
            
            /* Warna Biru Donker (Dark Navy Blue) */
            background-color: #121212 !important; 
            
            /* Garis tepi biru yang sedikit lebih terang agar elegan */
            border: 1px solid #262626 !important;  
            border-radius: 10px;       /* Sudut melengkung */
            
            color: #ffffff !important; /* Teks tetap putih murni */
            white-space: pre-wrap;    /* Menjaga format spasi/paragraf asli */
            font-size: 15px;
            line-height: 1.6;
        }}

        /* Pengaman agar teks di dalam box biru donker tetap putih murni */
        .scrollable-content-box *, .scrollable-content-box p, .scrollable-content-box span {{
            color: #ffffff !important;
        }}



        </style>
        """,
        unsafe_allow_html=True
    )

set_office_bg()



# Load Environment Variables for the OpenAI API Key
load_dotenv()

# --- SIDEBAR: API CONFIGURATION ---

# Fetch API Key from .env file, user can also manually input/overwrite it
openai_api_key = os.getenv("OPENAI_API_KEY", "")

st.caption("This application utilizes the `gpt-4o-mini` model for cost-efficiency and speed.")

st.divider()

# --- DYNAMIC URL INPUT ---
st.subheader("🔗 Enter Article URLs")
st.write("If the article spans multiple pages, insert all page URLs below (one URL per line).")

# Default values formatted as a newline-separated string
default_urls = "\n".join([
    "https://tekno.kompas.com/read/2026/02/25/10010007/skenario-krisis-2028-saat-ai-gantikan-manusia-terlalu-cepat",
    "https://tekno.kompas.com/read/2026/02/25/10010007/skenario-krisis-2028-saat-ai-gantikan-manusia-terlalu-cepat?page=2",
    "https://tekno.kompas.com/read/2026/02/25/10010007/skenario-krisis-2028-saat-ai-gantikan-manusia-terlalu-cepat?page=3"
])

url_input = st.text_area("Article Pages URL List:", value=default_urls, height=150)

# Process the text input into a Python List (removing empty lines if any)
article_pages = [url.strip() for url in url_input.split("\n") if url.strip()]


# --- MAIN CORE FUNCTION (SCRAPING) ---
def scrape_articles(pages):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }
    session = requests.Session()
    
    title = ""
    text_content = []
    
    for index, url in enumerate(pages, start=1):
        try:
            response = session.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                article = Article(url)
                article.download(input_html=response.text)
                article.parse()
                
                # Fetch the main title from the very first page only
                if index == 1:
                    title = article.title
                    
                text_content.append(article.text)
            else:
                st.error(f"❌ Failed to fetch Page {index}. Status Code: {response.status_code}")
        except Exception as e:
            st.error(f"⚠️ Error occurred on Page {index}: {e}")
            
    return title, text_content


# --- TRIGGER BUTTON & EXECUTION FLOW ---
if st.button("Start Scraping and Summarize", type="primary"):
    if not openai_api_key:
        st.warning("⚠️ Please provide an OpenAI API Key in the sidebar first!")
    elif not article_pages:
        st.warning("⚠️ Please enter at least one article URL!")
    else:
        with st.spinner("Extracting content from the article pages..."):
            article_title, text_list = scrape_articles(article_pages)
            
        if text_list:
            # Merging text from all pages into one comprehensive string
            final_story = "\n\n[Continued onto the next page...]\n\n".join(text_list)
            
            # Display results side-by-side using Streamlit Columns
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Full Content**")
                st.success("✅ Scraping completed successfully!")
                full_content_html = f"""<div class="scrollable-content-box"><strong style="font-size: 16px;">Title: {article_title}</strong><div style="margin-top: 5px;"></div> {final_story.strip()}</div>"""
                st.markdown(full_content_html, unsafe_allow_html=True)


                # st.markdown(f"**Title:** {article_title}")
                # # Wrapped inside a text area for clear vertical scrolling
                # st.text_area("**Content:**", value=final_story, height=450)
                
            with col2:
                with st.spinner("AI is generating your summary..."):
                    try:
                        template = """You are a very good assistant that summarizes online articles.
Here's the article you want to summarize.
==================
Title: {article_title}
{full_text_content}
==================
Write a summary of the previous article respond in the same language used in the article. 
"""
                        prompt = template.format(article_title=article_title, full_text_content=final_story)
                        
                        # Initializing the modern OpenAI model client via LangChain
                        chat = ChatOpenAI(
                            api_key=openai_api_key, 
                            model="gpt-4o-mini", 
                            temperature=0,
                            max_tokens=2048
                        )
                        
                        summary = chat.invoke([HumanMessage(content=prompt)])
                        
                        st.markdown("**AI Summary**")
                        st.success("✅ Summary generated successfully!")
                        
                        with st.container():
                        
                            full_summary_html = f"""<div class="scrollable-summary-box"><div style="margin-top: 5px;"></div>{summary.content}</div>"""

                            st.markdown(full_summary_html, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Failed to generate summary via OpenAI: {e}")
        else:
            st.error("Failed to extract any text content from the provided URLs.")