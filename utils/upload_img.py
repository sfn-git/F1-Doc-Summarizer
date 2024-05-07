import requests

def uploadImg(img_path):

    url = "https://discord.com/api/webhooks/987750700253581412/0tWPywW1SJFpyT7Fujnk2CAOkx1HrfxhOCdSYIU9eewYuD6210yK54XLNssprqJZ2tqt"

    files = {"image": open(img_path, "rb")}

    result = requests.post(url, files = files)

    try:
        result.raise_for_status()
    except Exception as err:
        print(err)
    else:
        print("Image Uploaded".format(result.status_code))
        return result.json()["attachments"][0]["url"]