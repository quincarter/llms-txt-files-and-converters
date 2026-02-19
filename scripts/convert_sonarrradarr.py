import json
import sys
import os

def clean_text(text):
    if not text: return ""
    # Remove newlines and excess whitespace
    return " ".join(str(text).split())

def process_file(input_filename):
    if not os.path.exists(input_filename):
        print(f"Skipping {input_filename}: File not found.")
        return

    # Determine output filename
    base_name = os.path.splitext(os.path.basename(input_filename))[0]
    # Rename 'v3' to 'sonarr' for clarity if needed
    if base_name == "v3": base_name = "sonarr"
    
    output_filename = f"{base_name}-llms.txt"

    print(f"Reading {input_filename}...")
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            spec = json.load(f)
    except Exception as e:
        print(f"Error parsing JSON in {input_filename}: {e}")
        return

    output = []
    
    # 1. Header Info
    info = spec.get('info', {})
    title = info.get('title', base_name.capitalize())
    output.append(f"# {title} API Documentation")
    output.append(f"Version: {info.get('version', '?')}")
    output.append(f"Description: {clean_text(info.get('description', ''))}\n")

    # 2. Endpoints
    paths = spec.get('paths', {})
    print(f"  - Found {len(paths)} endpoints.")

    for path, path_item in paths.items():
        for method_name, details in path_item.items():
            if not isinstance(details, dict): continue
            
            # Common methods only
            if method_name.lower() not in ['get', 'post', 'put', 'delete', 'patch']:
                continue

            method_str = method_name.upper()
            summary = clean_text(details.get('summary', ''))
            description = clean_text(details.get('description', ''))
            operation_id = details.get('operationId', '')

            # Header: Method + Path
            output.append(f"## {method_str} {path}")
            
            # Metadata
            if summary: output.append(f"**Summary**: {summary}")
            if operation_id: output.append(f"**ID**: {operation_id}")
            if description and description != summary:
                output.append(f"**Details**: {description}")

            # Parameters (Query/Path)
            params = details.get('parameters', [])
            if params:
                output.append("**Parameters**:")
                for p in params:
                    if not isinstance(p, dict): continue
                    
                    name = p.get('name', '?')
                    loc = p.get('in', '?') # query, path
                    req = "*" if p.get('required') else ""
                    schema_type = p.get('schema', {}).get('type', 'string')
                    desc = clean_text(p.get('description', ''))
                    
                    output.append(f"- `{name}`{req} ({loc} {schema_type}): {desc}")

            # Request Body (JSON)
            if 'requestBody' in details:
                content = details['requestBody'].get('content', {})
                # Usually application/json
                json_body = content.get('application/json', {})
                schema_ref = json_body.get('schema', {}).get('$ref', '')
                
                if schema_ref:
                    # Extract "SeriesResource" from "#/components/schemas/SeriesResource"
                    model_name = schema_ref.split('/')[-1]
                    output.append(f"**Body**: Requires object `{model_name}`")

            output.append("") # Spacer

    # 3. Write Output
    print(f"  - Writing to {output_filename}...")
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write("\n".join(output))
    print("  - Done.")

def main():
    # List of files to convert
    files_to_convert = ["v3.json", "radarr-openapi.json"]
    
    # If user provided arguments, use those instead
    if len(sys.argv) > 1:
        files_to_convert = sys.argv[1:]

    for f in files_to_convert:
        process_file(f)

if __name__ == "__main__":
    main()