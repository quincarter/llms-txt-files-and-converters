import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import time

# --- Configuration ---
SITEMAP_URL = "https://supabase.com/docs/sitemap.xml"
OUTPUT_FILE = "supabase_js_context.txt"
# Supabase docs use a specific article structure
CONTENT_SELECTOR = "article" 

# We only want URLs that match these patterns
INCLUDE_PATTERNS = [
    "/docs/reference/javascript",  # JS Client Library
    "/docs/guides/auth",           # Auth Guides (highly relevant to JS)
    "/docs/guides/database",       # DB Guides
    "/docs/guides/functions",      # Edge Functions
    "/docs/guides/realtime",       # Realtime
    "/docs/guides/storage"         # Storage
]

# Optional: Exclude patterns if you want to be more specific
EXCLUDE_PATTERNS = [
    "/docs/reference/javascript/v0", # Exclude old versions
    "/docs/reference/javascript/v1", # Exclude old versions
    "mobile", "flutter", "kotlin"    # Exclude non-JS platforms
]

def get_filtered_urls(sitemap_url):
    """Parses sitemap and returns only relevant JS/Guide URLs."""
    try:
        print(f"Fetching sitemap: {sitemap_url}...")
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        # Parse XML (Supabase sitemap is standard)
        root = ET.fromstring(response.content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        urls = []
        for url_tag in root.findall('ns:url', namespace):
            loc = url_tag.find('ns:loc', namespace).text
            
            # 1. Must match at least one INCLUDE pattern
            if not any(pattern in loc for pattern in INCLUDE_PATTERNS):
                continue
                
            # 2. Must NOT match any EXCLUDE pattern
            if any(pattern in loc for pattern in EXCLUDE_PATTERNS):
                continue
                
            urls.append(loc)
            
        print(f"Found {len(urls)} relevant URLs (filtered from total).")
        return sorted(list(set(urls))) # Remove duplicates and sort
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []

def html_to_markdown(html_content, url):
    """Specific parser for Supabase docs structure."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Supabase docs usually keep main content in <article>
    content = soup.find(CONTENT_SELECTOR)
    if not content:
        content = soup.find('main')
        
    if not content:
        return f"\n\n--- COULD NOT PARSE: {url} ---\n\n"

    # Remove sidebar navigations, ads, or footers inside the article
    for tag in content(['nav', 'footer', 'script', 'style', 'button']):
        tag.decompose()

    output = []
    
    # Extract Title
    title = soup.find('h1')
    title_text = title.get_text(strip=True) if title else url.split('/')[-1]
    output.append(f"\n\n# {title_text}\n")
    output.append(f"Source: {url}\n\n")

    # Extract text and code
    for element in content.descendants:
        if element.name in ['h2', 'h3', 'h4']:
            output.append(f"\n### {element.get_text(strip=True)}\n")
        elif element.name == 'p':
            output.append(f"{element.get_text(strip=True)}\n\n")
        elif element.name == 'pre':
            # Supabase code blocks
            code = element.get_text()
            output.append(f"```javascript\n{code}\n```\n\n")
        elif element.name == 'ul':
            for li in element.find_all('li', recursive=False):
                output.append(f"- {li.get_text(strip=True)}\n")
            output.append("\n")

    return "".join(output)

def main():
    urls = get_filtered_urls(SITEMAP_URL)
    
    if not urls:
        print("No URLs found. Check your patterns.")
        return

    print(f"Starting crawl of {len(urls)} pages...")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# Supabase JavaScript Reference & Guides\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d')}\n\n")
        
        for i, url in enumerate(urls):
            print(f"[{i+1}/{len(urls)}] Fetching: {url}")
            try:
                page_resp = requests.get(url)
                if page_resp.status_code == 200:
                    markdown = html_to_markdown(page_resp.content, url)
                    f.write(markdown)
                    f.write("\n" + "="*80 + "\n") # Explicit separator
                else:
                    print(f"  Failed (Status: {page_resp.status_code})")
                
                # Polite delay
                time.sleep(0.2) 
                
            except Exception as e:
                print(f"  Error: {e}")

    print(f"\nSuccess! Saved context to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()