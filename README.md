# llms-txt-files-and-converters

This repository contains a collection of Large Language Model (LLM) context files and Python scripts for converting various API documentation and codebases into text formats suitable for LLM ingestion or analysis.

## Repository Structure

- **Python Converter Scripts**: Scripts for converting API specs, documentation, and codebases into LLM-friendly text files.
  - `convert_docs.py`
  - `convert_emby_jellyfin.py`
  - `convert_lit.py`
  - `convert_nestjs-1.py`
  - `convert_rn.py`
  - `convert_seer.py`
  - `convert_supabase.py`
  - `convert_ts.py`
  - `convert.py`

- **API/OpenAPI/Swagger Files**: Source files for conversion.
  - `emby-api.json`
  - `jellyfin-openapi-stable.json`
  - `swagger_full.json`
  - `Proxmox VE Administration Guide.html`
  - `lit_full.txt`

- **LLM Context Files**: Output files containing processed documentation or code context for LLMs, organized in the `llms/` directory.
  - `effect-llms-full.txt`
  - `emby-api-llms.txt`
  - `jellyfin-openapi-stable-llms.txt`
  - `lit_full.txt`
  - `nestjs_full.txt`
  - `proxmox-llms-full.txt`
  - `react_native_llms.txt`
  - `react-paper-llms-full.txt`
  - `seer-llms.txt`
  - `supabase_js_context.txt`
  - `typescript_full.txt`

## Usage

1. **Convert Documentation**: Use the provided Python scripts to convert API specs or documentation into LLM context files. Each script is tailored for a specific source or format.
2. **LLM Context Files**: The generated `.txt` files in the `llms/` directory can be used as input for LLM training, fine-tuning, or prompt engineering.

## Example

To convert the Emby API OpenAPI spec to a text file for LLMs:

```bash
python convert_emby_jellyfin.py
```

The output will be saved as `llms/emby-api-llms.txt`.

## License

MIT License

## Author

[quincarter](https://github.com/quincarter)
