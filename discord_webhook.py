import config
import requests #dependency

def sendMessage(title, description, doc_url):
    url = config.data["DISCORD_WEBHOOK_URL"]

    #for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
    data = {
        "username" : "FIA Document"
    }

    data["embeds"] = [
        {
            "title": "{}".format(title),
            "description" : "{}".format(description),
            "url": "{}".format(doc_url),
            "image": {
                    "url": "https://www.fia.com/sites/default/files/styles/panopoly_image_original/public/fia_logo_final_.png",
                    "height": 160,
                    "width": 240
                }
        }
    ]

    result = requests.post(url, json = data)

    try:
        result.raise_for_status()
    except Exception as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))