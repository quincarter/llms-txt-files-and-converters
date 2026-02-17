import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin

# --- Configuration ---
START_URL = "https://react.dev/learn"
BASE_URL = "https://react.dev"
OUTPUT_FILE = "react_learn_llms.txt"

# Only grab URLs from the Learn section
INCLUDE_PREFIX = "/learn"

# Selectors
CONTENT_SELECTOR = "article"

def get_learning_path(start_url):
    print(f"Fetching curriculum from: {start_url}...")
    try:
        response = requests.get(start_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        urls = []
        seen = set()

        # Strategy: The React docs sidebar is usually a <nav> containing the links.
        # We try to find the specific sidebar first to preserve the "Curriculum Order".
        sidebar = soup.find('nav', {'aria-label': 'Sidebar'}) 
        if not sidebar:
            # Fallback: Look for the generic sidebar container class often used in Next.js docs
            sidebar = soup.select_one('aside nav')

        source = sidebar if sidebar else soup

        links = source.find_all('a', href=True)
        
        for a in links:
            href = a['href']
            full_url = urljoin(BASE_URL, href)
            path = full_url.replace(BASE_URL, "")

            # 1. Filter: Must be in /learn
            if not path.startswith(INCLUDE_PREFIX):
                continue
            
            # 2. Clean anchors
            clean_url = full_url.split('#')[0]

            # 3. Deduplicate while PRESERVING ORDER
            if clean_url not in seen:
                seen.add(clean_url)
                urls.append(clean_url)

        return urls

    except Exception as e:
        print(f"Error fetching path: {e}")
        return []

def html_to_markdown(html_content, url):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    content = soup.select_one(CONTENT_SELECTOR)
    if not content:
        content = soup.select_one("main")
    
    if not content:
        return f"\n\n--- FAILED TO PARSE: {url} ---\n\n"

    # Cleanup: Remove "Deep Dive" toggles buttons, footers, etc.
    for tag in content.select("nav, footer, script, style, button"):
        tag.decompose()

    output = []
    
    # Title
    title = soup.find('h1')
    title_text = title.get_text(strip=True) if title else url.split('/')[-1]
    output.append(f"\n\n# {title_text}\n")
    output.append(f"Source: {url}\n\n")

    for element in content.descendants:
        if element.name in ['h2', 'h3', 'h4']:
            text = element.get_text(strip=True).replace('#', '')
            output.append(f"\n{ '#' * int(element.name[1]) } {text}\n")
        
        elif element.name == 'p':
            text = element.get_text(strip=True)
            if text: output.append(f"{text}\n\n")
            
        elif element.name == 'pre':
            code = element.get_text()
            output.append(f"```jsx\n{code}\n```\n\n")
            
        elif element.name == 'li':
            if element.parent.name in ['ul', 'ol']:
                 output.append(f"- {element.get_text(strip=True)}\n")
        
        # Capture "Recap" or "Deep Dive" boxes which are often in <aside> or specific divs
        elif element.name == 'aside':
             output.append(f"> {element.get_text(strip=True)}\n\n")

    return "".join(output)

def main():
    urls = get_learning_path(START_URL)
    
    if not urls:
        print("No URLs found.")
        return

    print(f"Found {len(urls)} learning modules.")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# React Learning Curriculum\n")
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