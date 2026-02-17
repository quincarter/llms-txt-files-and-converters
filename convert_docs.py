import requests
from markdownify import markdownify as md
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import time
import sys

# --- Configuration ---
SITEMAP_URL = "https://supabase.com/docs/sitemap.xml"
OUTPUT_FILE = "llms-full.txt"
# CSS selector for the main content area (Inspect the site to find this)
# For React Native Paper/Docusaurus sites, it's often 'main', 'article', or a specific div class.
# If unsure, leave as None to grab the <body>, though this may include navbars.
CONTENT_SELECTOR = "main" 
DELAY_BETWEEN_REQUESTS = 0.5 # Seconds to wait between requests to be polite

def get_urls_from_sitemap(sitemap_url):
    """Parses the XML sitemap and returns a list of URLs."""
    try:
        print(f"Fetching sitemap: {sitemap_url}...")
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        # Sitemaps use a namespace, we need to handle that
        # Usually http://www.sitemaps.org/schemas/sitemap/0.9
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        urls = []
        for url in root.findall('ns:url', namespace):
            loc = url.find('ns:loc', namespace).text
            urls.append(loc)
            
        print(f"Found {len(urls)} URLs in sitemap.")
        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []

def html_to_markdown(html_content, url):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract content
    if CONTENT_SELECTOR:
        content = soup.select_one(CONTENT_SELECTOR)
    else:
        content = soup.body

    if not content: return ""
    
    # Remove noise
    for tag in content(['script', 'style', 'nav', 'footer']):
        tag.decompose()

    # Convert to Markdown
    text = md(str(content), heading_style="ATX")
    
    return f"\n\n# Page: {url}\n\n{text}"

def main():
    urls = get_urls_from_sitemap(SITEMAP_URL)
    
    if not urls:
        print("No URLs found. Exiting.")
        return

    print(f"Starting crawl of {len(urls)} pages...")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        # Write header
        f.write(f"# Documentation Dump\n")
        f.write(f"Source: {SITEMAP_URL}\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d')}\n\n")
        
        for i, url in enumerate(urls):
            print(f"[{i+1}/{len(urls)}] Processing {url}...")
            try:
                page_resp = requests.get(url)
                if page_resp.status_code == 200:
                    markdown = html_to_markdown(page_resp.content, url)
                    f.write(markdown)
                    f.write("\n\n" + "-"*80 + "\n\n") # Separator between pages
                else:
                    print(f"Failed to fetch {url} (Status: {page_resp.status_code})")
                
                time.sleep(DELAY_BETWEEN_REQUESTS)
                
            except Exception as e:
                print(f"Error processing {url}: {e}")

    print(f"\nDone! Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()