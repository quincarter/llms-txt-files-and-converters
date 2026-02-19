import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin

# --- Configuration ---
START_URL = "https://www.chartjs.org/docs/latest/"
BASE_URL = "https://www.chartjs.org"
OUTPUT_FILE = "chartjs_full_llms.txt"

INCLUDE_PREFIX = "/docs/latest/"
CONTENT_SELECTOR = ".theme-default-content, main.page, main"

def html_to_markdown(html_content, url):
    """Converts the raw HTML to clean markdown."""
    soup = BeautifulSoup(html_content, 'html.parser')
    content = soup.select_one(CONTENT_SELECTOR)
        
    if not content:
        return f"\n\n--- FAILED TO PARSE CONTENT FOR: {url} ---\n\n"

    # Remove noise (TOCs, edit links, navigation buttons, header anchors)
    for tag in content.select(".table-of-contents, .page-edit, .page-nav, a.header-anchor"):
        tag.decompose()

    output = []
    
    # Title
    title = soup.find('h1')
    title_text = title.get_text(strip=True) if title else url.split('/')[-1]
    output.append(f"\n\n# {title_text}\n")
    output.append(f"Source: {url}\n\n")

    for element in content.descendants:
        if element.name in ['h2', 'h3', 'h4']:
            output.append(f"\n{ '#' * int(element.name[1]) } {element.get_text(strip=True)}\n")
        
        elif element.name == 'p':
            text = element.get_text(strip=True)
            if text: output.append(f"{text}\n\n")
            
        elif element.name == 'pre':
            code = element.get_text()
            # VuePress wraps pre in a div containing the language class
            lang = "javascript" 
            parent_div = element.find_parent('div', class_=lambda c: c and c.startswith('language-'))
            if parent_div:
                for c in parent_div['class']:
                    if c.startswith('language-'):
                        lang = c.replace('language-', '')
                        break
            output.append(f"``` {lang}\n{code}\n```\n\n")
            
        elif element.name == 'li':
            if element.parent.name in ['ul', 'ol']:
                output.append(f"- {element.get_text(strip=True)}\n")
                
        # VuePress Tip/Warning/Danger Custom Blocks
        elif element.name == 'div' and element.get('class'):
            classes = element['class']
            if 'custom-block' in classes:
                block_type = "NOTE"
                if 'tip' in classes: block_type = "TIP"
                elif 'warning' in classes: block_type = "WARNING"
                elif 'danger' in classes: block_type = "DANGER"
                
                text = element.get_text(" ", strip=True)
                output.append(f"> **{block_type}:** {text}\n\n")

    return "".join(output)

def main():
    # Phase 1: Deep Discovery & Caching
    # We cache the HTML so we don't have to make 2 requests per page
    queue = [START_URL]
    url_to_html = {}
    
    print("Phase 1: Deep Crawling to discover hidden sidebar links...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    while queue:
        current_url = queue.pop(0)
        
        if current_url in url_to_html:
            continue
            
        print(f"  Fetching: {current_url}")
        try:
            resp = requests.get(current_url, headers=headers)
            if resp.status_code != 200:
                print(f"    Failed with status {resp.status_code}")
                continue
                
            # Cache the HTML
            url_to_html[current_url] = resp.content
            
            # Look for NEW links that just rendered in the DOM
            soup = BeautifulSoup(resp.content, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = urljoin(BASE_URL, href)
                path = full_url.replace(BASE_URL, "")

                if path.startswith(INCLUDE_PREFIX):
                    # Strip anchor hashes to avoid duplicate page visits
                    clean_url = full_url.split('#')[0] 
                    
                    if clean_url not in url_to_html and clean_url not in queue:
                        queue.append(clean_url)
            
            # Be polite to Chart.js servers
            time.sleep(0.15)
            
        except Exception as e:
            print(f"    Error: {e}")

    # Phase 2: Processing & Saving
    # We sort alphabetically so /api/ comes before /api/interfaces/, keeping the file highly organized
    sorted_urls = sorted(list(url_to_html.keys()))
    
    print(f"\nPhase 2: Converting {len(sorted_urls)} discovered pages to Markdown...")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# Chart.js Documentation (Full Deep Crawl)\n")
        f.write(f"Scraped starting from {START_URL}\n\n")
        
        for url in sorted_urls:
            html_content = url_to_html[url]
            markdown = html_to_markdown(html_content, url)
            f.write(markdown)
            f.write(f"\n{'-'*80}\n")
            
    print(f"\nDone! Successfully defeated the SPA routing. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()