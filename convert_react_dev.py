import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin

# --- Configuration ---
# We start at the root of the Reference section to find the sidebar
START_URL = "https://react.dev/reference/react"
BASE_URL = "https://react.dev"
OUTPUT_FILE = "react_api_reference_llms.txt"

# Only grab URLs that belong to the reference section
INCLUDE_PREFIX = "/reference/"

# React.dev uses semantic <article> tags for the main content
CONTENT_SELECTOR = "article"

def get_reference_urls(start_url):
    print(f"Fetching sidebar links from: {start_url}...")
    try:
        response = requests.get(start_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        urls = []
        
        # Strategy: Find all links on the page, then filter for Sidebar-like behavior.
        # The sidebar on react.dev usually contains the bulk of /reference/ links.
        links = soup.find_all('a', href=True)
        
        for a in links:
            href = a['href']
            
            # 1. Normalize
            full_url = urljoin(BASE_URL, href)
            path = full_url.replace(BASE_URL, "")

            # 2. Strict Filter: Must be a reference page
            if not path.startswith(INCLUDE_PREFIX):
                continue
            
            # 3. Exclude legacy or non-content links if any (React docs are pretty clean)
            if "#" in path:
                # React docs use anchors heavily for TOC; strip them to get unique pages
                full_url = full_url.split('#')[0]

            urls.append(full_url)

        # Deduplicate and Sort
        # Sorting is important to keep Hooks grouped together (e.g., useId, useState)
        unique_urls = sorted(list(set(urls)))
        
        return unique_urls

    except Exception as e:
        print(f"Error fetching initial page: {e}")
        return []

def html_to_markdown(html_content, url):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract Content
    content = soup.select_one(CONTENT_SELECTOR)
    if not content:
        content = soup.select_one("main")
    
    if not content:
        return f"\n\n--- FAILED TO PARSE: {url} ---\n\n"

    # Remove Noise
    # React docs have a "Deep Dive" section which is good, but we remove navigation elements
    for tag in content.select("nav, footer, script, style, button"):
        tag.decompose()

    output = []
    
    # Title
    title = soup.find('h1')
    title_text = title.get_text(strip=True) if title else url.split('/')[-1]
    output.append(f"\n\n# {title_text}\n")
    output.append(f"Source: {url}\n\n")

    # Content Processing
    for element in content.descendants:
        if element.name in ['h2', 'h3', 'h4']:
            # Clean header text (remove '#' links)
            text = element.get_text(strip=True).replace('#', '')
            output.append(f"\n{ '#' * int(element.name[1]) } {text}\n")
        
        elif element.name == 'p':
            text = element.get_text(strip=True)
            if text: output.append(f"{text}\n\n")
            
        elif element.name == 'pre':
            # React docs use standard code blocks
            code = element.get_text()
            # Default to jsx/javascript for React docs
            output.append(f"```jsx\n{code}\n```\n\n")
            
        elif element.name == 'li':
            # List items
            if element.parent.name == 'ul':
                output.append(f"- {element.get_text(strip=True)}\n")
            elif element.parent.name == 'ol':
                output.append(f"1. {element.get_text(strip=True)}\n")
        
        # React docs often use "Note" or "Pitfall" callouts. 
        # These are usually divs with specific classes like 'bg-yellow-100' or similar.
        # We can try to catch generic divs that contain strong text.
        elif element.name == 'div' and 'note' in str(element.get('class', '')).lower():
             output.append(f"> **NOTE:** {element.get_text(strip=True)}\n\n")

    return "".join(output)

def main():
    urls = get_reference_urls(START_URL)
    
    if not urls:
        print("No URLs found. The site structure might have changed.")
        return

    print(f"Found {len(urls)} reference pages.")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# React API Reference\n")
        f.write(f"Scraped from {START_URL}\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d')}\n\n")
        
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
                
                time.sleep(0.25) # Polite delay
                
            except Exception as e:
                print(f"  Failed: {e}")

    print(f"\nDone! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()