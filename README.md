
# llms-txt-files-and-converters

This repository provides:

- Python scripts to convert API documentation, codebases, and guides into text files suitable for Large Language Model (LLM) ingestion.
- A collection of pre-converted LLM context files for various technologies and APIs.

## Repository Structure

### Python Converter Scripts (`scripts/`)
Scripts for extracting and converting documentation or codebases:

- `convert.py` — General conversion utility
- `convert_docs.py` — For documentation files
- `convert_emby_jellyfin.py` — For Emby/Jellyfin OpenAPI specs
- `convert_lit.py` — For Lit framework
- `convert_nestjs-1.py` — For NestJS
- `convert_rn.py` — For React Native
- `convert_seer.py` — For Seer
- `convert_supabase.py` — For Supabase
- `convert_ts.py` — For TypeScript
- `convert_react_learn.py` — For React Learn
- `convert_react_dev.py` — For React Dev

### Source Files (`json-and-html/`)
API specs, documentation, and guides to be converted:

- `emby-api.json`
- `jellyfin-openapi-stable.json`
- `swagger_full.json`
- `Proxmox VE Administration Guide.html`

### LLM Context Files (`llms/`)
Text files containing processed documentation or code context for LLMs:

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
- `react_learn_llms.txt`
- `react_reference_llms.txt`


### LLMs.txt files created already
- [NextJS](https://nextjs.org/llms.txt) - this one had one created


## Usage

1. **Convert Documentation**: Run the relevant Python script from the `scripts/` directory to convert a source file into an LLM context file. For example:

   ```bash
   python scripts/convert_emby_jellyfin.py
   ```

   The output will be saved in the `llms/` directory.

2. **Use LLM Context Files**: The `.txt` files in `llms/` can be used for LLM prompt engineering, fine-tuning, or as reference material.

## Contributing

Feel free to submit issues or pull requests for new converters or improvements.

## License

MIT License

## Author

[quincarter](https://github.com/quincarter)

## Usage

1. **Convert Documentation**: Run the relevant Python script to convert a source file into an LLM context file. For example:

   ```bash
   python convert_emby_jellyfin.py
   ```

   The output will be saved in the `llms/` directory.

2. **Use LLM Context Files**: The `.txt` files in `llms/` can be used for LLM prompt engineering, fine-tuning, or as reference material.

## Contributing

Feel free to submit issues or pull requests for new converters or improvements.

## License

MIT License

## Author

[quincarter](https://github.com/quincarter)
