import json
import time
from playwright.sync_api import sync_playwright

# --- Configuration ---
TARGET_URL = "http://192.168.86.116:5055/api-docs/"
OUTPUT_JSON = "swagger_full.json"
OUTPUT_TXT = "llms-api.txt"

def json_to_markdown(spec):
    """Converts the JSON spec to a simplified text format for LLMs."""
    output = []
    
    info = spec.get('info', {})
    output.append(f"# {info.get('title', 'API Documentation')}")
    output.append(f"Description: {info.get('description', '')}\n")
    
    paths = spec.get('paths', {})
    for path, methods in paths.items():
        for method, details in methods.items():
            summary = details.get('summary', 'No summary')
            desc = details.get('description', '')
            output.append(f"## {method.upper()} {path}")
            output.append(f"**Summary**: {summary}")
            if desc:
                # Truncate long descriptions to save tokens
                clean_desc = desc.split('\n')[0][:200]
                output.append(f"**Details**: {clean_desc}")
            
            # Parameters
            params = details.get('parameters', [])
            if params:
                param_list = []
                for p in params:
                    req = "*" if p.get('required') else ""
                    param_list.append(f"{p['name']}{req} ({p.get('in','')})")
                output.append(f"**Params**: {', '.join(param_list)}")
            
            output.append("") # Spacer

    return "\n".join(output)

def run():
    print(f"Launching headless browser to inspect {TARGET_URL}...")
    
    with sync_playwright() as p:
        # Launch Chromium (headless means no visible UI)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(TARGET_URL)
            
            # Wait for the Swagger UI element to actually appear on screen
            print("Waiting for Swagger UI to load...")
            page.wait_for_selector(".swagger-ui", timeout=10000)
            
            # Give it a moment to finish processing (Swagger UI can be slow to hydrate)
            time.sleep(2)
            
            print("Extracting spec from browser memory...")
            # We execute JavaScript inside the browser to get the data from the Global 'ui' object
            # standard Swagger UI exposes 'window.ui'
            spec = page.evaluate("""() => {
                if (window.ui && window.ui.specSelectors && window.ui.specSelectors.specJson) {
                    // specJson() returns an Immutable.js object, we convert it to standard JS
                    return window.ui.specSelectors.specJson().toJS();
                }
                return null;
            }""")
            
            if not spec:
                print("Failed to find 'window.ui' object. Trying fallback (network interception)...")
                # Fallback: Sometimes it's not in window.ui, but we can grab the 'openapi' object if it exists
                spec = page.evaluate("() => window.openapi || window.swaggerDoc || null")

            if spec:
                print("Success! Extracted API Specification.")
                
                # 1. Save JSON
                with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
                    json.dump(spec, f, indent=2)
                print(f"-> Saved raw JSON to {OUTPUT_JSON}")
                
                # 2. Convert to Markdown
                print("Converting to AI-friendly format...")
                md_text = json_to_markdown(spec)
                with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
                    f.write(md_text)
                print(f"-> Saved context to {OUTPUT_TXT}")
                
            else:
                print("CRITICAL: Could not find API spec object in browser memory.")
                print("Debug: Taking screenshot...")
                page.screenshot(path="debug_error.png")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()