from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Initialize LLM at the start
llm = ChatOpenAI(temperature=0)

# Data Models
class FilmDocument(BaseModel):
    """Represents a processed film-related document"""
    url: str
    content: str
    metadata: Dict
    timestamp: str
    relevance_score: Optional[float] = None
    sentiment: Optional[Dict] = None
    summary: Optional[str] = None

def generate_sitemap(start_url: str, max_articles: int = 10) -> List[str]:
    """Generate a sitemap of film articles"""
    base_domain = "https://www.kino.de"
    visited = set()
    sitemap = []
    
    try:
        response = requests.get(start_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for link in soup.find_all('a', href=True):
            full_url = urljoin(base_domain, link['href'])
            if full_url.startswith(base_domain) and '/news/' in full_url and full_url not in visited:
                visited.add(full_url)
                sitemap.append(full_url)
                if len(sitemap) >= max_articles:
                    break
                    
        print(f"Found {len(sitemap)} URLs")
        return sitemap
        
    except requests.RequestException as e:
        print(f"Error fetching {start_url}: {str(e)}")
        return []

def crawl_websites(urls: List[str]) -> List[FilmDocument]:
    """Crawl websites and return list of FilmDocuments"""
    documents = []
    for url in urls:
        try:
            print(f"Crawling: {url}")
            loader = WebBaseLoader(url)
            doc = loader.load()[0]
            
            film_doc = FilmDocument(
                url=doc.metadata.get('source', url),
                content=doc.page_content,
                metadata=doc.metadata,
                timestamp=datetime.now().isoformat()
            )
            documents.append(film_doc)
            
        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")
            continue
    
    return documents

def analyze_sentiment(text: str) -> Dict:
    """Analyze sentiment of text using LLM"""
    response = llm.invoke(
        f"""Analyze the sentiment of the following text and return only a JSON with scores for positive, negative, and neutral (scores should sum to 1.0):

        Text: {text[:1000]}
        
        Return format: {{"positive": float, "negative": float, "neutral": float}}"""
    )
    return eval(response.content)  # Convert string to dict

def generate_summary(text: str) -> str:
    """Generate a summary of the text using LLM"""
    response = llm.invoke(
        f"""Summarize the following film-related content in 2-3 sentences:

        {text[:2000]}"""
    )
    return response.content

def analyze_documents(documents: List[FilmDocument]) -> List[FilmDocument]:
    """Analyze the documents with sentiment and summary"""
    for doc in documents:
        print(f"Analyzing: {doc.url}")
        doc.sentiment = analyze_sentiment(doc.content)
        doc.summary = generate_summary(doc.content)
    return documents

def save_results(documents: List[FilmDocument], filename: str):
    """Save the results to a file"""
    with open(filename, 'w', encoding='utf-8') as f:
        for doc in documents:
            f.write(f"URL: {doc.url}\n")
            f.write(f"Timestamp: {doc.timestamp}\n")
            f.write(f"Summary: {doc.summary}\n")
            f.write(f"Sentiment: {doc.sentiment}\n")
            f.write("\nContent Preview:\n")
            f.write(f"{doc.content[:500]}...\n")
            f.write("="*50 + "\n\n")

def main():
    # Step 1: Generate sitemap
    start_url = "https://www.kino.de/news/"
    urls = generate_sitemap(start_url, max_articles=3)  # Limited for testing
    
    # Step 2: Crawl websites
    documents = crawl_websites(urls)
    print(f"Crawled {len(documents)} documents")
    
    # Step 3: Analyze documents
    analyzed_docs = analyze_documents(documents)
    
    # Step 4: Save results
    save_results(analyzed_docs, "film_monitoring_results.txt")
    
    # Print summary
    print("\nProcessing complete!")
    print(f"Processed {len(analyzed_docs)} documents")
    for doc in analyzed_docs:
        print(f"\nURL: {doc.url}")
        print(f"Summary: {doc.summary}")
        print(f"Sentiment: {doc.sentiment}")

if __name__ == "__main__":
    main()
