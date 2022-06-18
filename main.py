from discord_webhook import sendMessage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from sys import exit
from shutil import rmtree
from os import mkdir
import requests
from pdf2image import convert_from_path
from upload_img import uploadImg

options = Options()
options.headless = True
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--no-sandbox")

try:
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season-2022-2005")
    latest_document = driver.find_element(By.XPATH, "/html/body/div[3]/div/div[3]/div[2]/div/div[3]/div/div[2]/div/ul[1]/li/ul/li/ul/li[1]")
    title = latest_document.find_element(By.CLASS_NAME,'title').text
    date = latest_document.find_element(By.CLASS_NAME, "date-display-single").text
    document_url = latest_document.find_element(By.TAG_NAME, "a")
    url = document_url.get_attribute("href")
    description = "{}".format(date)
    driver.quit()
except Exception as e:
    print(e)
    driver.quit()
    exit(1)

try:
    last_date = open('last_date', 'r').read()
    last_title = open('last_title', 'r').read()
except FileNotFoundError as e:
    last_date = ""
    last_title = ""

if((last_date == "" or last_title == "") or (last_date != date and last_title != title)):
    #get pdf
    try:
        rmtree('output')
    except FileNotFoundError:
        pass
    r = requests.get(url, allow_redirects=True)
    open('latest.pdf', 'wb').write(r.content)
    images = convert_from_path('latest.pdf')
    mkdir('output')
    img_path=''
    for img in images:
        img_path = './output/page.jpg'
        img.save(img_path, 'JPEG')
        break

    img_url = uploadImg(img_path)

    sendMessage(title, description, url, img_url)
    last_date = open('last_date', 'w').write(date)
    last_title = open('last_title', 'w').write(title)





