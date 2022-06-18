from discord_webhook import sendMessage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
options.headless = True
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options, executable_path="./chromedriver")

driver.get("https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season-2022-2005")
latest_document = driver.find_element(By.XPATH, "/html/body/div[3]/div/div[3]/div[2]/div/div[3]/div/div[2]/div/ul[1]/li/ul/li/ul/li[1]")
title = latest_document.find_element(By.CLASS_NAME,'title').text
date = latest_document.find_element(By.CLASS_NAME, "date-display-single").text
document_url = latest_document.find_element(By.TAG_NAME, "a").get_attribute("href")
url = document_url
description = "{}".format(date)

last_date = open('last_date', 'r').read()
last_title = open('last_title', 'r').read()

if((last_date == "" or last_title == "") or (last_date != date and last_title != title)):
    sendMessage(title, description, url)
    last_date = open('last_date', 'w').write(date)
    last_title = open('last_title', 'w').write(title)





