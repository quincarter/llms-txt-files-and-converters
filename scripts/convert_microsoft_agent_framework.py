import requests
import json
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# --- Configuration ---
# 1. We aim for the JSON TOC file directly. 
# For MS Learn, it is usually at the root of the docset + "/toc.json"
TOC_URL = "https://learn.microsoft.com/en-us/agent-framework/toc.json"
BASE_URL = "https://learn.microsoft.com/en-us/agent-framework/"
OUTPUT_FILE = "ms_agent_framework_llms.txt"

def get_urls_from_json_toc(toc_url):
    print(f"Fetching TOC JSON: {toc_url}...")
    try:
        response = requests.get(toc_url)
        response.raise_for_status()
        data = response.json()
        
        urls = []

        # Recursive function to parse nested TOC items
        def extract_hrefs(items):
            for item in items:
                # Some items are just headers (no href), so we check
                if 'href' in item:
                    # MS Learn TOC hrefs are usually relative (e.g., "overview.md" or "concepts/")
                    # We strictly want HTML links, not .md files if possible, 
                    # but usually requests handles the redirect. 
                    # Let's clean it up:
                    rel_path = item['href'].replace('.md', '')
                    full_url = urljoin(BASE_URL, rel_path)
                    
                    # Remove anchors and query params
                    clean_url = full_url.split('?')[0].split('#')[0]
                    urls.append(clean_url)
                
                if 'children' in item:
                    extract_hrefs(item['children'])

        extract_hrefs(data.get('items', []))
        
        # Deduplicate and keep order
        return list(dict.fromkeys(urls))

    except Exception as e:
        print(f"Error fetching TOC JSON: {e}")
        return []

def html_to_markdown(html_content, url):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # MS Learn Main Content
    content = soup.select_one("main, #main-column")
    if not content:
        return f"\n\n--- FAILED TO PARSE: {url} ---\n\n"

    # Clean Noise
    for tag in content.select(".metadata, .page-metadata, .feedback-section, #action-panel, .page-actions, nav, footer, script, style"):
        tag.decompose()

    output = []
    
    # Title
    title = soup.find('h1')
    title_text = title.get_text(strip=True) if title else "Unknown Page"
    output.append(f"\n\n# {title_text}\n")
    output.append(f"Source: {url}\n\n")

    # Parse Content
    for element in content.descendants:
        if element.name in ['h2', 'h3']:
            output.append(f"\n{ '#' * int(element.name[1]) } {element.get_text(strip=True)}\n")
        
        elif element.name == 'p':
            text = element.get_text(strip=True)
            if text: output.append(f"{text}\n\n")
            
        elif element.name == 'pre':
            # Code Blocks
            code = element.get_text()
            # Detect Language from class (e.g., 'lang-csharp')
            lang = ""
            code_tag = element.find('code')
            if code_tag and code_tag.get('class'):
                for c in code_tag['class']:
                    if c.startswith('lang-'):
                        lang = c.replace('lang-', '')
            
            output.append(f"``` {lang}\n{code}\n```\n\n")

        elif element.name == 'div' and 'alert' in element.get('class', []):
            # MS Learn Alerts (Tip/Note/Important)
            # They usually look like: <div class="alert is-info"><p class="alert-title">Note</p>...</div>
            alert_title_tag = element.find(class_='alert-title')
            alert_type = alert_title_tag.get_text(strip=True) if alert_title_tag else "NOTE"
            
            # Get text but exclude the title we just extracted
            text_content = element.get_text(" ", strip=True).replace(alert_type, "", 1).strip()
            output.append(f"> **{alert_type.upper()}**: {text_content}\n\n")

        elif element.name == 'li':
            if element.parent.name in ['ul', 'ol']:
                output.append(f"- {element.get_text(strip=True)}\n")

    return "".join(output)

def main():
    urls = get_urls_from_json_toc(TOC_URL)
    
    if not urls:
        print("No URLs found. The TOC JSON might be missing or moved.")
        print(f"Tried: {TOC_URL}")
        return

    print(f"Found {len(urls)} pages from TOC. Starting crawl...")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# Microsoft Agent Framework Docs\n")
        f.write(f"Source TOC: {TOC_URL}\n\n")
        
        for i, url in enumerate(urls):
            print(f"[{i+1}/{len(urls)}] Crawling: {url}")
            try:
                # MS Learn sometimes 403s python user-agents, so we fake it
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                resp = requests.get(url, headers=headers)
                
                if resp.status_code == 200:
                    markdown = html_to_markdown(resp.content, url)
                    f.write(markdown)
                    f.write(f"\n{'-'*80}\n")
                else:
                    print(f"  Error {resp.status_code}")
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"  Failed: {e}")

    print(f"\nDone! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()