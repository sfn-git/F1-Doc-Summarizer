# FIA Document Send and Summarize

- A program that will retrieve the latest FIA document file, summarize it using AI, then sends it to a Discord channel using webhook.
- Note: This program will only summarize and send documents that are considered `"Summons", "Decision", "Infringement"`.

## Requirements
- Python
- [Ollama](https://github.com/ollama/ollama) (optional)

## Run the Program
### Docker (Recommended)
- Run using docker once to allow for config file creation
    - `docker run -v /path/on/local:/app/config -p 8080:8080 ghcr.io/sfn-git/fia_doc_webhook:latest` 
- Navigate to the web ui at port 8080 
### Manual
- Install python dependencies requirements.txt
    - `pip install -r requirements.txt`
- Run `main.py` once
    - `python main.py`
- Navigate to the web ui at port 8080

## Configs
### Edit configs on the configs page of the webui
- `DISCORD_WEBHOOK_URL`
    - An array of webhook URLs to allow for the program to send to multiple channels.
- `OLLAMA_URL` (optional)
    - If not skipping summary, the link to your ollama instance
- `OLLAMA_MODEL` (optional)
    - Model you will use to summarize the pdf content

## Custom Scheduler Coming Soon...
- Currently, the scheduler built in will run every minute on Friday-Sunday and every hour on Monday - Thursday.