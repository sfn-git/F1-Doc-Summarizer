# FIA Document Send and Summarize

- A program that will retrieve the latest FIA document file, summarize it using AI, then sends it to a Discord channel using webhook.
- Note: This program will only summarize and send documents that are considered `"Summons", "Decision", "Infringement"`. More document types will come in the future.

## Requirements
- Python
- [Ollama](https://github.com/ollama/ollama) (optional)
- Cron/Scheduler (See Cron Section)

## Run the Program
### Docker
- Run using docker once to allow for config file creation
    - `docker run -v /path/on/local:/app/config ghcr.io/sfn-git/fia_doc_webhook:latest`
- Edit config/config.json file (see config file section IMPORTANT!) 
- Run again to retrieve and send the summaries. 
### Manual
- Install python dependencies requirements.txt
    - `pip install -r requirements.txt`
- Run `main.py` once
    - `python main.py`
- Edit config/config.json file (see config file section IMPORTANT!)
- Run `main.py` whenever you want to check and send FIA Doc files that have not been sent.

## Config File
### Upon running the first time, the config file will generate and the program will exit

- `DISCORD_WEBHOOK_URL`
    - An array of webhook URLs to allow for the program to send to multiple channels.
- `ENV` (optional)
    - No significance as of now. Can be used for reference
- `SKIP_SUMMARY` [Default: False] (True/False)
    - Skip Ollama summarizing the document and only send the link to the document
- ‼️ `HASH_ONLY` [Default: True] (True/False) 
    - Only generate the hashes into config/sent-hashes.json. It is recommended to run the program again after updating the config file with this option as `true` to allow for the hashes of past documents to be generated to avoid spamming. Once generated, this can be set to false.
- `OLLAMA_URL` (optional)
    - If not skipping summary, the link to your ollama instance
- `OLLAMA_MODEL` (optional)
    - Model you will use to summarize the pdf content

## Cron
- After initial setup, it is recommended to run this program in conjunction with a scheduler (cron) to allow for constant checking of FIA documents. See below for the recommended timings for this program.

- [Every minute on Thursday, Friday, Saturday, & Sunday](https://crontab.guru/#*_*_*_*_0,4,5,6)
- [Every hour on Monday, Tuesday, & Wednesday](https://crontab.guru/#0_*/1_*_*_1,2,3)