# FIA Document Send and Summarize

- A program that will retrieve the latest FIA document file, summarize it using AI, then sends it to a Discord channel using webhook.

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

### Getting Started
- Use the nav links to configure the application
- Configure [Discord Webhooks](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) by adding a channel to send documents
- Configure Ollama server to enable AI summarization of documents
    - You can adjust the prompt used to configure to your liking
    - You can use different prompts depending on the document type (see documents)
- Documents
    - Ability to filter the type of document that should be sent based off the title of the document. 
- Scheduler
    - Built in scheduler allows you to customize how often you would like to check the FIA documents website for a new document to process. 
        - Use cron syntax to set the timing for a specific job. 
        - To disable a job, simply make the cron string invalid (Example: `-* * * * *`)