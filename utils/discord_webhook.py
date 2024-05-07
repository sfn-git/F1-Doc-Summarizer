import utils.config as config
from utils.logging import logging
import requests #dependency

def sendMessage(title, description, doc_url, img_url):
    urls = config.data["DISCORD_WEBHOOK_URL"]

    for url in urls:
        #for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
        data = {
            "username" : "FIA Document"
        }

        data["embeds"] = [
            {
                "title": "{}".format(title),
                "description" : "{}".format(description),
                "url": "{}".format(doc_url),
                "timestamp": ''
            }
        ]
        result = requests.post(url, json = data)

        try:
            result.raise_for_status()
        except Exception as err:
            logging.error("Embed failed to send to {}. {}".format(url, err))
        else:
            logging.info("Embed sent to {}, with status code {}.".format(url, result.status_code))