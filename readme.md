# FIA Document Discord Webhook and Summarizer

- Program will retrieve the latest FIA document file and sends it to a discord webhook link.

## External Requirements
- Ollama server

## How to run
### Manually
- Install from requirements.txt
    - `pip install -r requirements.txt`
- Run `main.py` once
    - `python main.py`
- Edit config.json file (see config file section)
- Rename `example_sent-hashes.json` to `sent-hashes.json` to only send documents after the 2024 Miami Grand Prix.
    - Note: When running without this file, a new `send-hashes.json` will be created and will send all of the documents that are on the FIA page to your discord webhook if HASH_ONLY is set to false. It is recommended to run this the first time with HASH_ONLY set to true (default when config file is created). 
- Run `main.py` whenever you want to check and send FIA Doc files that have not been sent.

### Docker
- Coming soon...

## Config File
- Upon running the first time, the config file will generate and exit

- `DISCORD_WEBHOOK_URL` 
- `ENV`
    - No significance as of now. Can be used for reference
- `SKIP_SUMMARY` [Default: False] (True/False)
    - Will skip summarizing the document and only send the link to the document
- `HASH_ONLY` [Default: True] (True/False) 
    - Will skip all steps and only generate the hashes into sent-hashes.json
- `OLLAMA_URL`
    - If not skipping summary, the link to your ollama instance
- `OLLAMA_MODEL`
    - Model you will use to summarize the pdf content