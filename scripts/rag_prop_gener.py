import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_core.tools import tool
from langchain.agents import create_agent

# ==================== LOAD ENV ====================
load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# ==================== LLM ====================
llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model="gpt-4.1-mini",
    temperature=0.2,
    max_tokens=700
)

# ==================== PDF RAG ====================
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

pc = Pinecone(
    api_key=os.environ["PINECONE_API_KEY"]
)

index = pc.Index("property-opportunity-2026")

vector_store = PineconeVectorStore(
    index=index,
    embedding=embeddings
)

retriever = vector_store.as_retriever(
    search_kwargs={"k": 3}
)

# ==================== TOOL ====================
@tool("search_pdf_trends")
def search_pdf_trends(query: str) -> str:
    """
    Cari insight market dan makroekonomi dari PDF Property Opportunity 2026.
    Hanya gunakan informasi yang ada di dokumen, jangan menambahkan informasi eksternal.
    """

    docs = retriever.invoke(query)

    results = []

    for i, doc in enumerate(docs):

        results.append(
            f"""
SOURCE {i+1}:
{doc.page_content[:700]}
"""
        )

    return "\n".join(results)

# ==================== TOOLS ====================
tools = [search_pdf_trends]

# ==================== SYSTEM PROMPT ====================
system_prompt = """
You are an AI market strategist.

Use only retrieved PDF content.

Rules:
- No fake statistics
- No unsupported assumptions
- State uncertainty clearly
- Give concise macroeconomy and market opportunity
- Respond in user's language
"""

# Structure:
# 1. Market Trend
# 2. Macro Insight
# 3. Business Risk
# 4. Recommendation

# ==================== AGENT ====================
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt
)

# ==================== QUERY ====================
query = """
Di 2 tahun ke depan pada pasar properti di Indonesia, 
apa yang harus diperhatikan oleh pengusaha properti di Jakarta?.
"""

# ==================== RUN ====================
print("Memulai analisis PDF...")

response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": query
            }
        ]
    }
)

print("\n--- PDF MARKET ANALYSIS ---\n")

if "messages" in response:
    print(response["messages"][-1].content)
else:
    print(response)