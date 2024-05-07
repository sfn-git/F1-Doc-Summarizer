import utils.config as config
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
            }
        ]
        result = requests.post(url, json = data)

        try:
            result.raise_for_status()
        except Exception as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))