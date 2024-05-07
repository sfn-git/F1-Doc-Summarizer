from discord_webhook import sendMessage
from sys import exit
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from tika import parser
from io import StringIO
import re
import sys, os
from discord_webhook import sendMessage
import config

DOCUMENT_ENUMS = ["Summons", "Decision", "Infringement"]

def main():
    get_latest_fia_doc()

def get_latest_fia_doc():

    try:
        base_url = "https://www.fia.com"
        req = requests.get("{}/documents".format(base_url), allow_redirects=True)
        req.raise_for_status()

        html = req.content.decode("utf-8")
        soup = BeautifulSoup(html, 'html.parser')

        # Get Latest Entry List
        # entry_data = ''
        # for links in soup.find_all('a'):
        #     link = links.get('href')
        #     if "/sites/default/files/decision-document" in link and "Entry List" in link:
        #         doc_url = "{}{}".format(base_url, quote(link))
        #         file_name = get_file_from_url(doc_url)
        #         entry_data = get_pdf_data(file_name).split("No. Driver Nat Team Constructor", 1)[1]
        
        # New Docs
        for links in soup.find_all('a'):
            link = links.get('href')
            if "/sites/default/files/decision-document" in link: #and "Miami" in link:
                check_break = False
                for enum in DOCUMENT_ENUMS:
                    if enum in link:
                        doc_url = "{}{}".format(base_url, quote(link))
                        file_name = get_file_from_url(doc_url)
                        data = get_pdf_data(file_name)
                        doc_summary = summarize_data("Do not greet when responding. In the format of a discord embed, please summarize the text below. Bold each header. Stay strictly to the format below.\nRace: [Name of Race]\nDriver(s) Involved: [Bullet Point Drivers]\nPenalties/Allegation: [Bullet point driver that was punished and the penalties]\nSummary: [Summarize the event that ocurred in the document]\n{}".format(data))
                        title = link.split('/')
                        sendMessage(title[len(title)-1].split('.pdf')[0], doc_summary, doc_url, None)
                        check_break = True
                        break
                if check_break: break
        
    except requests.exceptions.HTTPError as e:
        print('Received failed status code from webpage.')
        exit()

def get_file_from_url (url):
    #get pdf
    file_name = 'latest.pdf'
    r = requests.get(url, allow_redirects=True)
    file = open(file_name, 'wb').write(r.content)
    return file_name

def summarize_data(prompt):
    
    open('prompt.txt', 'w').write(prompt)
    # create_model()
    base_url = config.data['OLLAMA_URL']
    
    try:
        tags = requests.get("{}{}".format(base_url, '/api/tags'))
        tags_response = tags.json()
        model_name = 'dolphin-phi:latest'

        for models in tags_response['models']:
            if config.data['OLLAMA_MODEL'] in models['name']:
                model_name = models['name']
                break
        
        url = '/api/generate'
        generate_obj = {
            "model": model_name,
            "prompt": "{}".format(prompt),
            "stream": False
        }

        generate_res = requests.post("{}{}".format(base_url, url), json=generate_obj)
        generate_res.raise_for_status()
        gen_response = generate_res.json()['response']
        return gen_response
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print (exc_type, fname, exc_tb.tb_lineno)
        return None

# def create_model():
#     url = 'http://localhost:11434/api/create'
#     create_obj = {
#         "name": "fia_doc_summary",
#         "modelfile": "FROM phi:2.7b"
#     }

def get_pdf_data(file_name):

    parsed_pdf = parser.from_file(filename=file_name)
    raw_data = parsed_pdf['content']    
    s = StringIO(raw_data)
    return_s = ''
    for line in s:
        new_line = line.replace("\n", "")
        if(len(new_line) == 0):
            continue
        return_s += '{} '.format(line)
    return  re.sub(r"\xa0", " ", return_s)

if __name__=='__main__':
    main()