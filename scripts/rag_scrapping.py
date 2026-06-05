import requests
from newspaper import Article

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Scraping the article content from the given URL
headers = {
'User-Agent': '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'''
} 

article_pages = [
    "https://tekno.kompas.com/read/2026/02/25/10010007/skenario-krisis-2028-saat-ai-gantikan-manusia-terlalu-cepat",
    "https://tekno.kompas.com/read/2026/02/25/10010007/skenario-krisis-2028-saat-ai-gantikan-manusia-terlalu-cepat?page=2",
    "https://tekno.kompas.com/read/2026/02/25/10010007/skenario-krisis-2028-saat-ai-gantikan-manusia-terlalu-cepat?page=3"
]

session = requests.Session()

article_title = ""
full_text_content = []

print("Scrapping is starting .....")

for index, url in enumerate(article_pages, start=1):
    try:
        response = session.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            article = Article(url)
            article.download(input_html=response.text)
            article.parse()

            if index == 1:
                article_title = article.title

            full_text_content.append(article.text)
            print(f"Succeed to scrape page {index}")

        else:
            print(f"Error to scrape page {index}. Status: {response.status_code}")
    
    except Exception as e:
        print(f"Error occured in page {index}: {e}")

if full_text_content:
    final_story = "\n\n[Lanjut ke halaman berikutnya...]\n\n".join(full_text_content)
    print("\n" + "="*50)
    print(f"TITLE: {article_title}")
    print("="*50)
    print(f"TEXT:\n\n{final_story}")
    print("="*50)
else:
    print("Error occurred while scraping all of articles.")

# Create a prompt for the language model to summarize the article content
template = """You are a very good assistant that summarizes online articles.
Here's the article you want to summarize.
==================
Title: {article_title}
{full_text_content}
==================
Write a summary of the previous article. 
"""

prompt = template.format(article_title=article_title, full_text_content=final_story)

# Load model
load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

chat = ChatOpenAI(
    api_key=OPENAI_API_KEY, 
    model="gpt-4.1-mini", 
    temperature=0,
    max_tokens=2048
    )

# Generate summary
summary = chat.invoke([HumanMessage(content=prompt)])
print(summary.content)