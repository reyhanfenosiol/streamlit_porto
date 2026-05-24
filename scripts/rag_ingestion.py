import os
from pathlib import Path
from dotenv import load_dotenv

import fitz
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
# from langchain_community.document_loaders import PyPDFLoader

# load environment variables from a .env file
load_dotenv()
api_key = os.environ["PINECONE_API_KEY"]

# load pdf
if os.path.exists("/opt/airflow"):
    BASE_DIR = "/opt/airflow"  # untuk airflow
else:    
    BASE_DIR = "D:/REYHAN/BOOST ACADEMY/projek_akhir"  # untuk lokal

pdf_path = f"{BASE_DIR}/multipage_app/GROWTH_IN_EUROPEAN_E_COMMERCE_ANALYZING_THE_SURGE_IN_ONLINE_SHOPPING_AND_CONSUMER_BEHAVIOUR1.pdf"


docs = []
doc = fitz.open(pdf_path)

for page_num, page in enumerate(doc):
    # Mengekstrak teks dengan mempertahankan struktur kolom/layout
    text = page.get_text("text")

    if not text.strip():
        print(f"⚠️ Halaman {page_num} kosong atau tidak memiliki teks yang dapat diekstrak.")
        continue

    metadata = {"source": pdf_path, "page": page_num + 1}
    docs.append(Document(page_content=text, metadata=metadata))
print(f"Jumlah halaman dalam PDF: {len(doc)}")


# split text
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=100, separators=["\n\n", "\n", " ", ""])
all_split = text_splitter.split_documents(docs)
print(f"✂️ Total chunks yang dihasilkan: {len(all_split)}")

# buat embedding
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
pc = Pinecone(api_key=api_key)

# buat index
index_name = "growth-europe-2025"
existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
if index_name not in existing_indexes:
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1",
        )
    )
index = pc.Index(index_name)

# buat vector store
vector_store = PineconeVectorStore(index=index, embedding=embedding)

chunk_ids = [
    f"growth-europe-2025-p{chunk.metadata['page']}-c{i}" 
    for i, chunk in enumerate(all_split)
]
print(f"🚀 Memulai proses pengiriman {len(all_split)} records ke Pinecone...")
result = vector_store.add_documents(documents=all_split, ids=chunk_ids)

print("✅ Proses Upsert Selesai!")
print(f"Hasil Response (ID Terdaftar): {len(result)} records.")