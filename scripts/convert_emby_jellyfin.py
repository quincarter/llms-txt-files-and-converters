import json
import sys
import os

def clean_text(text):
    if not text: return ""
    return " ".join(str(text).split())

def main():
    # 1. Determine input file from command line or default
    if len(sys.argv) > 1:
        input_filename = sys.argv[1]
    else:
        # Fallback if you just double-click the script
        input_filename = "jellyfin-openapi-stable.json"

    if not os.path.exists(input_filename):
        print(f"Error: File '{input_filename}' not found.")
        print("Usage: python convert_api.py <filename.json>")
        return

    # Auto-generate output filename (e.g., jellyfin.json -> jellyfin-llms.txt)
    base_name = os.path.splitext(input_filename)[0]
    output_filename = f"{base_name}-llms.txt"

    print(f"Reading {input_filename}...")
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            spec = json.load(f)
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        return

    output = []
    
    # Header
    info = spec.get('info', {})
    output.append(f"# {info.get('title', 'API Documentation')}")
    output.append(f"Description: {clean_text(info.get('description', ''))}\n")

    paths = spec.get('paths', {})
    print(f"Processing {len(paths)} endpoints...")

    for path, path_item in paths.items():
        for method_name, details in path_item.items():
            # Skip non-dict items (safety check for Emby/Jellyfin quirks)
            if not isinstance(details, dict):
                continue
            
            method_str = method_name.upper()
            summary = clean_text(details.get('summary', ''))
            description = clean_text(details.get('description', ''))
            
            output.append(f"## {method_str} {path}")
            if summary: output.append(f"**Summary**: {summary}")
            if description and description != summary:
                output.append(f"**Details**: {description}")

            # Parameters
            params = details.get('parameters', [])
            if params:
                output.append("**Parameters**:")
                for p in params:
                    if not isinstance(p, dict): continue
                    name = p.get('name', '?')
                    loc = p.get('in', '?') 
                    type_hint = p.get('schema', {}).get('type', '')
                    desc = clean_text(p.get('description', ''))
                    required = "*" if p.get('required') else ""
                    
                    output.append(f"- `{name}`{required} ({loc} {type_hint}): {desc}")

            output.append("") 

    print(f"Writing to {output_filename}...")
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write("\n".join(output))
    
    print("Success!")

if __name__ == "__main__":
    main()