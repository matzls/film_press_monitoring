import os
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_community.document_loaders import WebBaseLoader

# Load environment variables
load_dotenv()

# Data Models
class FilmDocument(BaseModel):
    """Represents a processed film-related document"""
    url: str
    content: str
    metadata: Dict
    timestamp: str

def crawl_website(url: str) -> FilmDocument:
    """Crawl a single page using WebBaseLoader"""
    try:
        print(f"Attempting to crawl {url}")
        
        # Initialize WebBaseLoader
        loader = WebBaseLoader(url)
        
        # Load document
        doc = loader.load()[0]
        
        # Convert to FilmDocument
        film_doc = FilmDocument(
            url=doc.metadata.get('source', url),
            content=doc.page_content,
            metadata=doc.metadata,
            timestamp=datetime.now().isoformat()
        )
        
        return film_doc

    except Exception as e:
        print(f"Error crawling {url}: {str(e)}")
        return None

def save_to_file(documents: List[FilmDocument], filename: str):
    """Save documents to a text file"""
    with open(filename, 'w', encoding='utf-8') as f:
        for doc in documents:
            f.write(f"URL: {doc.url}\n")
            f.write(f"Content length: {len(doc.content)} characters\n")
            f.write(f"Metadata: {doc.metadata}\n")
            f.write("\nContent:\n")
            f.write(doc.content)
            f.write("\n" + "="*50 + "\n")

def main():
    # Read URLs from rough_sitemap.txt
    with open("rough_sitemap.txt", "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f.readlines()]

    documents = []
    for url in urls:
        doc = crawl_website(url)
        if doc:
            documents.append(doc)
    
    # Save output to a file
    save_to_file(documents, "sitemap_crawler_output.txt")

if __name__ == "__main__":
    main()
