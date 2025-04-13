# FIA Document Send and Summarize

- A program that will retrieve the latest FIA document file, summarize it using AI, then sends it to a Discord channel using webhook

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
    - Ability to filter the type of document that should be sent based off the title of the document
- Scheduler
    - Built in scheduler allows you to customize how often you would like to check the FIA documents website for a new document to process. 
        - Use cron syntax to set the timing for a specific job. 
        - To disable a job, simply make the cron string invalid (Example: `-* * * * *`)

### Prompts/Ollama
- For the AI Summary, you can use a custom prompt to adjust what information you would like to see. The default prompt does a good job at summarizing the information but the format can be inconsistent and the summaries can get wordy at times. See below for some custom prompts that I have been using. I will add more as I experiment with the prompts.
- As for the model to use, I have found that llama3.1 is the best at giving a straight forward summary based on the default prompt. I have experimented with 3.2 but found the summaries to be inconsistent when compared to 3.1. As I test other models I will update the readme. 

1. Model llama3.1 (Default)
```
Summarize the event that occurred in the document. Where applicable, include the driver(s), team(s), or organization(s) involved. Where applicable, include any penalties and what regulation was breached as part of the penalty.
Raw Data: [doc_data]
```
2. Model llama3.1
```
Summarize the event that occurred in the document. Where applicable, include the driver(s), team(s), or organization(s) involved only as stated within the document. Include any penalties and what regulation was breached as part of the penalty. Use the exact format below to structure the response. 

Document Text: [doc_data]

Format
Drivers Involved: [List drivers only]
Summary of Events: [Summarize the event that occurred in the document]
Penalties: [List any penalties. If none, write Not Applicable. If there is a number, write out the number]
```