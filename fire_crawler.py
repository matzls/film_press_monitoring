import os
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_community.document_loaders import FireCrawlLoader
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Get API keys
FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
if not FIRECRAWL_API_KEY:
    raise ValueError("FIRECRAWL_API_KEY not found in environment variables")

print(FIRECRAWL_API_KEY[:4] + "XXXX")

# Data Models
class FilmDocument(BaseModel):
    """Represents a processed film-related document"""
    url: str
    content: str
    metadata: Dict
    timestamp: str

def extract_content(html: str) -> str:
    """Extract specific content from HTML using BeautifulSoup"""
    soup = BeautifulSoup(html, 'html.parser')
    # Example: Extract main article content
    article = soup.find('article')
    if article:
        return article.get_text(separator='\n').strip()
    return ""

def crawl_website(url: str) -> List[FilmDocument]:
    """Crawl a single page using FireCrawlLoader"""
    try:
        print(f"Attempting to crawl {url}")
        
        # Initialize FireCrawlLoader
        loader = FireCrawlLoader(
            url=url,
            mode="scrape",  # Use scrape mode for a single page
            api_key=FIRECRAWL_API_KEY
        )
        
        # Load documents
        docs = loader.load()
        
        # Convert to FilmDocuments
        film_docs = []
        for doc in docs:
            content = extract_content(doc.page_content)
            film_docs.append(
                FilmDocument(
                    url=doc.metadata.get('sourceURL', url),
                    content=content,
                    metadata=doc.metadata,
                    timestamp=datetime.now().isoformat()
                )
            )
        
        return film_docs

    except Exception as e:
        print(f"Error crawling {url}: {str(e)}")
        return []

def main():
    # Target a specific page
    url = "https://www.kino.de/news/hochzeit-auf-den-ersten-blick-diese-neuerungen-erwarten-euch-2024/"
    documents = crawl_website(url)
    
    print(f"\nTotal documents crawled: {len(documents)}")
    for doc in documents:
        print("\n" + "="*50)
        print(f"URL: {doc.url}")
        print(f"Content length: {len(doc.content)} characters")
        print(f"Metadata: {doc.metadata}")
        print("\nContent preview:")
        print(doc.content + "..." if doc.content else "No content")

if __name__ == "__main__":
    main()
