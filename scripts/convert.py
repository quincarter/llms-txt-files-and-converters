import bs4
from bs4 import BeautifulSoup
import re

def clean_text(text):
    """Cleans up whitespace while preserving essential formatting."""
    if not text:
        return ""
    # Replace multiple spaces with single space
    text = re.sub(r'[ \t]+', ' ', text)
    # Fix multiple newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

def html_to_markdown(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # The main documentation usually lives in a specific content div
    # Based on your file structure, id="content" appears to hold the meat
    content_div = soup.find('div', id='content')
    if not content_div:
        content_div = soup.body

    output = []

    # Iterate over elements to preserve order
    for element in content_div.descendants:
        if isinstance(element, bs4.element.NavigableString):
            continue
            
        # Handle Headers
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(element.name[1])
            # Remove link anchors inside headers if present
            text = element.get_text(strip=True).replace("Permalink to this heading", "")
            output.append(f"\n\n{'#' * level} {text}\n")
            
        # Handle Paragraphs
        elif element.name == 'p':
            # Skip paragraphs inside tables or lists to avoid duplication if handled elsewhere
            if element.find_parent(['td', 'li']):
                continue
            text = clean_text(element.get_text())
            if text:
                output.append(f"\n{text}\n")

        # Handle Code Blocks (Proxmox docs use .monospaced or pre)
        elif element.name == 'pre' or (element.name == 'div' and 'listingblock' in element.get('class', [])):
            code_text = element.get_text()
            if code_text.strip():
                output.append(f"\n```\n{code_text}\n```\n")

        # Handle Lists
        elif element.name == 'li':
            # Determine indentation based on nesting
            parents = len(element.find_parents(['ul', 'ol'])) - 1
            indent = "  " * parents
            
            # Simple check for ordered vs unordered (approximation)
            prefix = "*"
            if element.parent.name == 'ol':
                prefix = "1." 
            
            text = clean_text(element.get_text(strip=True))
            if text:
                output.append(f"{indent}{prefix} {text}\n")

        # Handle Admonitions (Notes, Warnings)
        elif element.name == 'div' and 'admonitionblock' in element.get('class', []):
            # Extract the type (Note/Warning) and content
            role_div = element.find('td', class_='icon')
            content_cell = element.find('td', class_='content')
            
            if role_div and content_cell:
                role = role_div.get_text(strip=True) or "Note"
                text = clean_text(content_cell.get_text())
                output.append(f"\n> **{role.upper()}:** {text}\n")

    # Join and clean up final output
    full_text = "".join(output)
    return clean_text(full_text)

# --- Execution ---
input_filename = "Proxmox VE Administration Guide.html"
output_filename = "llms-full.txt"

try:
    print(f"Reading {input_filename}...")
    with open(input_filename, 'r', encoding='utf-8') as f:
        html_data = f.read()

    print("Converting to Markdown/Text...")
    markdown_text = html_to_markdown(html_data)

    # Add a header for the LLM context
    final_content = f"# Proxmox VE Administration Guide\n\n{markdown_text}"

    print(f"Saving to {output_filename}...")
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print("Success! File created.")

except FileNotFoundError:
    print(f"Error: Could not find '{input_filename}'. Make sure the script is in the same folder.")
except Exception as e:
    print(f"An error occurred: {e}")