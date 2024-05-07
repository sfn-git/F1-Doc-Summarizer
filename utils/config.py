import json
from utils.logging import logging
import os
from sys import exit

config_file_path = "./config.json"

if not os.path.exists(config_file_path):
        blank_file = {
                "DISCORD_WEBHOOK_URL" : [],
                "ENV" : "dev",
                "SKIP_SUMMARY": False,
                "HASH_ONLY": True,
                "OLLAMA_URL": "http://localhost:11434",
                "OLLAMA_MODEL": "llama3"
            }
        with open(config_file_path, "w") as jsonFile:
            json.dump(blank_file, jsonFile)
            logging.warn('Created config.json file. Edit configs before running the program again')
            exit()

# Opening JSON file
f = open('./config.json')
  
# returns JSON object as 
# a dictionary
data = json.load(f)
logging.info("Config file loaded")
logging.info("DISCORD_WEBHOOK_URL(s): {}".format(data["DISCORD_WEBHOOK_URL"]))
logging.info("ENV: {}".format(data["ENV"]))
logging.info("SKIP_SUMMARY: {}".format(data["SKIP_SUMMARY"]))
logging.info("HASH_ONLY: {}".format(data["HASH_ONLY"]))
logging.info("OLLAMA_URL: {}".format(data["OLLAMA_URL"]))
logging.info("OLLAMA_MODEL: {}".format(data["OLLAMA_MODEL"]))

# Closing file
f.close()