import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse

# --- Configuration ---
SITEMAP_URL = "https://reactnative.dev/sitemap.xml"
OUTPUT_FILE = "react_native_llms.txt"

# React Native uses Docusaurus. The content is usually in <article> 
# or a div with class 'theme-doc-markdown'
CONTENT_SELECTOR = "article"

# Filter to keep the context clean
INCLUDE_PREFIXES = [
    "https://reactnative.dev/docs/",
    "https://reactnative.dev/architecture/"
]

EXCLUDE_PATTERNS = [
    "/docs/0.",       # Exclude old versions (e.g., /docs/0.70/)
    "/docs/next/",    # Exclude 'next' (unreleased) versions to avoid duplicates
    "/blog/",         # Exclude blog posts (optional, remove if you want them)
    "/showcase",      # Exclude showcase
]

def get_filtered_urls(sitemap_url):
    print(f"Fetching sitemap: {sitemap_url}...")
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        urls = []
        for url_tag in root.findall('ns:url', namespace):
            loc = url_tag.find('ns:loc', namespace).text
            
            # 1. Must start with one of our allowed prefixes
            if not any(loc.startswith(p) for p in INCLUDE_PREFIXES):
                continue
                
            # 2. Must NOT match exclude patterns
            if any(p in loc for p in EXCLUDE_PATTERNS):
                continue
                
            urls.append(loc)
            
        # Deduplicate and sort
        return sorted(list(set(urls)))
        
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []

def html_to_markdown(html_content, url):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract main content
    content = soup.select_one(CONTENT_SELECTOR)
    if not content:
        # Fallback for some pages
        content = soup.select_one("main")

    if not content:
        return f"\n\n--- COULD NOT PARSE: {url} ---\n\n"

    # Clean up noise (headers, footers, edit buttons)
    for tag in content.select("nav, footer, script, style, .hash-link, button"):
        tag.decompose()

    output = []
    
    # Title from H1
    h1 = soup.find('h1')
    title = h1.get_text(strip=True) if h1 else url.split('/')[-1]
    output.append(f"\n\n# {title}\n")
    output.append(f"Source: {url}\n\n")

    # Simple element traversal
    for element in content.descendants:
        if element.name in ['h2', 'h3']:
            output.append(f"\n{ '#' * int(element.name[1]) } {element.get_text(strip=True)}\n")
        
        elif element.name == 'p':
            # Skip empty paragraphs
            text = element.get_text(strip=True)
            if text:
                output.append(f"{text}\n\n")
        
        elif element.name == 'pre':
            # Code blocks
            code_text = element.get_text()
            output.append(f"```\n{code_text}\n```\n\n")
            
        elif element.name == 'li':
            # Simple list handling
            output.append(f"- {element.get_text(strip=True)}\n")

    return "".join(output)

def main():
    urls = get_filtered_urls(SITEMAP_URL)
    
    if not urls:
        print("No URLs found. Exiting.")
        return

    print(f"Found {len(urls)} pages. Starting crawl...")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# React Native Documentation\n")
        f.write(f"Generated from {SITEMAP_URL}\n\n")
        
        for i, url in enumerate(urls):
            print(f"[{i+1}/{len(urls)}] Processing: {url}")
            try:
                resp = requests.get(url)
                if resp.status_code == 200:
                    markdown = html_to_markdown(resp.content, url)
                    f.write(markdown)
                    f.write("\n" + "="*80 + "\n") # Separator
                else:
                    print(f"  Failed (Status: {resp.status_code})")
                
                # Sleep to be polite to their server
                time.sleep(0.2)
                
            except Exception as e:
                print(f"  Error: {e}")

    print(f"\nDone! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()