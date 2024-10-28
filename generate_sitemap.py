"""
Sitemap Generator for Kino.de News Articles

This script crawls the Kino.de news section and generates a sitemap of article URLs.
It saves the URLs to a text file in a specified directory.

Features:
    - Crawls kino.de news section
    - Filters for valid news article URLs
    - Limits the number of articles collected
    - Saves results to a specified directory
    - Handles network errors gracefully

Usage:
    Run the script directly: python generate_sitemap.py
    The sitemap will be saved to: /Users/mg/Desktop/GitHub/ASTRAL/Code/film_monitoring/Data/rough_sitemap.txt

Dependencies:
    - requests: For making HTTP requests
    - beautifulsoup4: For parsing HTML content
    - urllib: For URL parsing and joining
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

def is_valid_url(url, base_domain):
    """
    Validate if a URL belongs to the specified base domain.
    
    Args:
        url (str): The URL to validate
        base_domain (str): The base domain to check against
    
    Returns:
        bool: True if URL is valid and belongs to base_domain, False otherwise
    """
    return url.startswith(base_domain)

def generate_sitemap(start_url, max_articles=10):
    """
    Generate a sitemap by crawling kino.de news articles.
    
    Args:
        start_url (str): The URL to start crawling from
        max_articles (int, optional): Maximum number of articles to collect. Defaults to 10
    
    Returns:
        list: List of collected article URLs
    
    Raises:
        requests.RequestException: If there's an error fetching the webpage
    """
    base_domain = "https://www.kino.de"
    visited = set()  # Track visited URLs to avoid duplicates
    sitemap = []     # Store valid article URLs

    try:
        # Fetch and parse the webpage
        response = requests.get(start_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links and process them
        for link in soup.find_all('a', href=True):
            # Convert relative URLs to absolute URLs
            full_url = urljoin(base_domain, link['href'])
            
            # Check if URL is valid and hasn't been visited
            if is_valid_url(full_url, base_domain) and full_url not in visited:
                if '/news/' in full_url:  # Only collect news articles
                    visited.add(full_url)
                    sitemap.append(full_url)
                    
                    # Stop if we've reached the maximum number of articles
                    if len(sitemap) >= max_articles:
                        break

    except requests.RequestException as e:
        print(f"Error fetching {start_url}: {str(e)}")

    return sitemap

def main():
    """
    Main function to execute the sitemap generation process.
    
    This function:
    1. Initiates the crawling process
    2. Creates the output directory if it doesn't exist
    3. Saves the collected URLs to a text file
    4. Prints status information
    """
    # Define the starting point for crawling
    start_url = "https://www.kino.de/news/"
    sitemap = generate_sitemap(start_url)
    
    # Set up the output directory
    output_dir = "/Users/mg/Desktop/GitHub/ASTRAL/Code/film_monitoring/Data"
    os.makedirs(output_dir, exist_ok=True)
    
    # Define output file path and save results
    output_file = os.path.join(output_dir, "rough_sitemap.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        for url in sitemap:
            f.write(url + "\n")
    
    # Print status information
    print(f"Sitemap generated with {len(sitemap)} URLs.")
    print(f"File saved to: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()
