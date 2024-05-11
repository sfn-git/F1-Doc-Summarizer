import utils.db as db
from utils.logging import logging
import requests #dependency

def sendMessage(url, title, description, doc_url, img_url):

    try:
        #for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
        data = {
            "username" : "FIA Document"
        }

        data["embeds"] = [
            {
                "title": "{}".format(title),
                "description" : "{}".format(description),
                "url": "{}".format(doc_url)
            }
        ]

        print(data)
        result = requests.post(url, json = data)
        result.raise_for_status()
        return True
    except Exception as err:
        logging.error("Embed failed to send. {}".format(err))
        return False