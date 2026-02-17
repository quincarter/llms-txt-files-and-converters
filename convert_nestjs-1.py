import time
from playwright.sync_api import sync_playwright

START_URL = "https://docs.nestjs.com/"
OUTPUT_FILE = "nestjs_full.txt"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Loading homepage to find links...")
        page.goto(START_URL)
        page.wait_for_selector("app-menu") # Wait for sidebar
        
        # Extract all sidebar links
        links = page.eval_on_selector_all("app-menu a", "elements => elements.map(e => e.href)")
        
        # Filter links
        urls = sorted(list(set([l for l in links if "docs.nestjs.com" in l and not "support" in l])))
        print(f"Found {len(urls)} pages.")
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("# NestJS Docs\n\n")
            
            for i, url in enumerate(urls):
                print(f"[{i+1}/{len(urls)}] Processing {url}")
                try:
                    page.goto(url)
                    # specific wait for content to ensure it's loaded
                    page.wait_for_selector(".content", timeout=5000)
                    
                    # Extract text content from the main article div
                    # We use innerText to get readable text (strips tags automatically)
                    # Or we can get HTML and parse with BS4 if we want formatting.
                    # Here we grab text for speed and cleanliness:
                    content = page.inner_text(".content")
                    
                    title = page.title()
                    f.write(f"# {title}\nSource: {url}\n\n{content}\n\n{'='*80}\n\n")
                    
                except Exception as e:
                    print(f"Error on {url}: {e}")

        browser.close()
        print("Done.")

if __name__ == "__main__":
    run()