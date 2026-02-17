import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin

# --- Configuration ---
# Start at the root docs page to find the sidebar links
START_URL = "https://lit.dev/docs/"
BASE_URL = "https://lit.dev"
OUTPUT_FILE = "lit_full.txt"

# Lit.dev uses specific semantic tags
CONTENT_SELECTOR = "article" 
# The sidebar is usually in a nav inside the drawer or main layout
# We will fallback to scanning all /docs/ links if a specific selector fails
SIDEBAR_SELECTOR = "nav" 

# Filter to keep context focused
INCLUDE_PREFIX = "/docs/"
EXCLUDE_PATTERNS = [
    "/v1/",           # Legacy docs
    "/playground/",   # Interactive tools
    "/api/",          # API reference (optional: keep if you want raw class references)
    "#",              # Anchor tags
]

def get_doc_queue(start_url):
    print(f"Fetching sidebar links from: {start_url}...")
    try:
        response = requests.get(start_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        urls = []
        
        # Lit.dev usually puts sidebar links in the left drawer. 
        # Strategy: Grab ALL links on the page, then strictly filter for doc pages.
        # This is more robust than guessing the sidebar class name which changes.
        links = soup.find_all('a', href=True)
        
        for a in links:
            href = a['href']
            
            # Normalize to absolute URL
            full_url = urljoin(BASE_URL, href)
            path = full_url.replace(BASE_URL, "")

            # 1. Must be in /docs/
            if not path.startswith(INCLUDE_PREFIX):
                continue
            
            # 2. Must not be excluded
            if any(exc in path for exc in EXCLUDE_PATTERNS):
                continue

            # 3. Clean anchors (e.g., /docs/templates#expressions -> /docs/templates)
            clean_url = full_url.split('#')[0]
            
            urls.append(clean_url)

        # Remove duplicates and sort
        # Note: Sorting alphabetically might break the "Getting Started -> Advanced" flow
        # but it ensures we get everything.
        unique_urls = sorted(list(set(urls)))
        
        return unique_urls

    except Exception as e:
        print(f"Error fetching queue: {e}")
        return []

def html_to_markdown(html_content, url):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract content
    content = soup.select_one(CONTENT_SELECTOR)
    if not content:
        content = soup.select_one("main")
        
    if not content:
        return f"\n\n--- FAILED TO PARSE: {url} ---\n\n"

    # Remove noise
    for tag in content.select("nav, footer, script, style, .toc, .edit-page-link"):
        tag.decompose()

    output = []
    
    # Title
    title = soup.find('h1')
    title_text = title.get_text(strip=True) if title else url.split('/')[-1]
    output.append(f"\n\n# {title_text}\n")
    output.append(f"Source: {url}\n\n")

    # Parse elements
    for element in content.descendants:
        if element.name in ['h2', 'h3']:
            # Remove the '#' permalink often found in headers
            text = element.get_text(strip=True).replace('#', '')
            output.append(f"\n## {text}\n")
            
        elif element.name == 'p':
            text = element.get_text(strip=True)
            # Filter out "Permalink" or empty text
            if text and "Permalink" not in text:
                output.append(f"{text}\n\n")
                
        elif element.name == 'pre':
            # Code blocks
            code = element.get_text()
            # Try to grab language class from code tag
            code_tag = element.find('code')
            lang = ""
            if code_tag and code_tag.get('class'):
                # classes look like ['language-ts', 'hljs']
                for c in code_tag['class']:
                    if c.startswith('language-'):
                        lang = c.replace('language-', '')
            
            output.append(f"``` {lang}\n{code}\n```\n\n")
            
        elif element.name == 'li':
             if element.parent.name in ['ul', 'ol']:
                output.append(f"- {element.get_text(strip=True)}\n")

    return "".join(output)

def main():
    urls = get_doc_queue(START_URL)
    
    if not urls:
        print("No URLs found. The site structure might have changed.")
        return

    print(f"Found {len(urls)} documentation pages.")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# Lit Documentation\n")
        f.write(f"Scraped from {START_URL}\n\n")
        
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
                
                time.sleep(0.2)
                
            except Exception as e:
                print(f"  Failed: {e}")

    print(f"\nDone! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()