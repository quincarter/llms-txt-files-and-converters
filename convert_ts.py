import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse

# --- Configuration ---
# We start at the Handbook introduction to find the sidebar
START_URL = "https://www.typescriptlang.org/docs/handbook/intro.html"
BASE_URL = "https://www.typescriptlang.org"
OUTPUT_FILE = "typescript_full.txt"

# Content selector for the actual documentation text
CONTENT_SELECTOR = "#handbook-content, article, main"

# Sidebar selector (Updated for TS site structure)
# The TS site often uses a <nav> with aria-label="Sidebar" or specific classes
SIDEBAR_SELECTORS = ["nav[aria-label='Sidebar']", "nav.toc", "#sidebar"]

def get_doc_urls(start_url):
    print(f"Fetching sidebar links from: {start_url}...")
    try:
        response = requests.get(start_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        urls = []
        sidebar = None
        
        # Try to find the sidebar
        for selector in SIDEBAR_SELECTORS:
            sidebar = soup.select_one(selector)
            if sidebar:
                break
        
        if not sidebar:
            print("Could not identify specific sidebar. Scanning all internal doc links...")
            links = soup.find_all('a', href=True)
        else:
            links = sidebar.find_all('a', href=True)

        for a in links:
            href = a['href']
            
            # Resolve relative URLs
            if not href.startswith("http"):
                href = urljoin(BASE_URL, href)
            
            # Filter: Must be in /docs/ and English
            # Also exclude some noise like playground or release notes if you want
            if "/docs/" in href and "/ja/" not in href and "/es/" not in href:
                urls.append(href.split('#')[0]) # Remove anchors

        # Deduplicate and Sort
        return sorted(list(set(urls)))

    except Exception as e:
        print(f"Error fetching initial page: {e}")
        return []

def html_to_markdown(html_content, url):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract Content
    content = soup.select_one(CONTENT_SELECTOR)
    if not content:
        # Fallback: try finding the main container by class
        content = soup.select_one(".container") 
        
    if not content:
        return f"\n\n--- FAILED TO PARSE: {url} ---\n\n"

    # Clean up noise
    for tag in content.select("nav, footer, script, style, .on-page-nav"):
        tag.decompose()

    output = []
    
    # Title
    title = soup.find('h1')
    title_text = title.get_text(strip=True) if title else "Unknown Page"
    output.append(f"\n\n# {title_text}\n")
    output.append(f"Source: {url}\n\n")

    # Content
    for element in content.descendants:
        if element.name in ['h2', 'h3']:
            output.append(f"\n## {element.get_text(strip=True)}\n")
        elif element.name == 'p':
            text = element.get_text(strip=True)
            if text: output.append(f"{text}\n\n")
        elif element.name == 'pre':
            # Try to detect language
            lang = "typescript"
            if "js" in element.get('class', []): lang = "javascript"
            output.append(f"```\n{element.get_text()}\n```\n\n")
        elif element.name == 'li':
            output.append(f"- {element.get_text(strip=True)}\n")
            
    return "".join(output)

def main():
    urls = get_doc_urls(START_URL)
    
    if not urls:
        print("No URLs found. Exiting.")
        return

    print(f"Found {len(urls)} pages. Starting crawl...")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# TypeScript Documentation (Scraped)\n\n")
        
        for i, url in enumerate(urls):
            print(f"[{i+1}/{len(urls)}] Crawling: {url}")
            try:
                resp = requests.get(url)
                if resp.status_code == 200:
                    markdown = html_to_markdown(resp.content, url)
                    f.write(markdown)
                    f.write(f"\n{'-'*80}\n")
                else:
                    print(f"  Error {resp.status_code}")
                
                time.sleep(0.1) 
                
            except Exception as e:
                print(f"  Failed: {e}")

    print(f"\nDone. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()