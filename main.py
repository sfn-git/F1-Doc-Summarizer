from utils.discord_webhook import sendMessage
from sys import exit
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from tika import parser
from io import StringIO
import re
import sys, os
from utils.discord_webhook import sendMessage
import utils.config as config
from random import choice
from random import randint
from hashlib import md5
import json
from utils.logging import logging

DOCUMENT_ENUMS = ["Summons", "Decision", "Infringement"]

def main():
    get_latest_fia_docs()

def get_latest_fia_docs():

    try:
        base_url = "https://www.fia.com"
        documents_url = "{}/documents".format(base_url)
        req = requests.get(documents_url, allow_redirects=True)
        req.raise_for_status()
        logging.info('Hit to {} successful'.format(req.url))

        html = req.content.decode("utf-8")
        soup = BeautifulSoup(html, 'html.parser')
        
        all_links = soup.find_all('a')
        all_links.reverse()
        
        # Loops all links retrieved from webpage
        for links in all_links:
            link = links.get('href')
            if "/sites/default/files/decision-document" in link: #and "Miami" in link:
                check_break = False
                for enum in DOCUMENT_ENUMS:
                    if enum in link:
                        sent_hash_data = get_hash_data()
                        link_hash = md5(link.encode()).hexdigest()
                        if link_hash in sent_hash_data['link_hash']:
                            break
                        if config.data['HASH_ONLY']:
                            add_hash(link_hash, link)
                            logging.warn('Only adding hash, skipping other steps')
                            continue
                        doc_url = "{}{}".format(base_url, quote(link))
                        logging.info('Found document type {} for url: {}'.format(enum, doc_url))
                        file_name = get_file_from_url(doc_url)
                        if file_name is None:
                            raise Exception
                        data = get_pdf_data(file_name)
                        doc_summary = summarize_data("Do not greet when responding. {} Bold each header. Stay strictly to the format below.\nRace: [<Year> Name of Race]\nDocument Type: {}\nDriver(s) Involved: [Only list the name of the Driver or car number if the name is not available]\nPenalties/Allegation/Decision: [Bullet point driver that was punished and the penalties]\nSummary: [Summarize the event that ocurred in the document]\n{}".format(get_fun_prompt(), enum, data))
                        title = link.split('/')
                        sendMessage(title[len(title)-1].split('.pdf')[0], doc_summary, doc_url, None)
                        add_hash(link_hash, link)
                        # check_break = True
                        # break
                if check_break: break
    except requests.exceptions.HTTPError as e:
        logging.error('Received failed status code from FIA main documents webpage. {}'.format(e))
        exit()
    except Exception as e:
        logging.error('An error ocurred and the FIA document could not be processed: {}'.format(e))
        exit()

def get_file_from_url (url):
    #get pdf
    if not os.path.exists('./temp'):
        os.makedirs('./temp')
        logging.warn('Created temp dir')
    file_name = './temp/latest.pdf'
    try:
        r = requests.get(url, allow_redirects=True)
        r.raise_for_status()
        file = open(file_name, 'wb').write(r.content)
        logging.info('Downloaded {} to {}'.format(url, file_name))
        return file_name
    except Exception as e:
        logging.error('Error retrieving file: {}'.format(e))
        return None

def summarize_data(prompt):
    #open('prompt.txt', 'w').write(prompt)
    # create_model()

    if(config.data['SKIP_SUMMARY']):
        return ""

    base_url = config.data['OLLAMA_URL']
    tag_url = "{}{}".format(base_url, '/api/tags')
    try:
        tags = requests.get(tag_url)
        tags_response = tags.json()
        model_name = 'dolphin-phi:latest'
        logging.info('Retrieved tags from {}'.format(tag_url))
        for models in tags_response['models']:
            if config.data['OLLAMA_MODEL'] in models['name']:
                model_name = models['name']
                break
        logging.info('(Model) {}'.format(model_name))
        url = '/api/generate'
        generate_obj = {
            "model": model_name,
            "prompt": "{}".format(prompt),
            "stream": False
        }
        logging.info('(Prompt) {}'.format(prompt).replace('\n', ' '))
        generate_res = requests.post("{}{}".format(base_url, url), json=generate_obj)
        generate_res.raise_for_status()
        gen_response = generate_res.json()['response']
        logging.info('(Response) {}'.format(gen_response).replace('\n', ' '))
        return "{}\n\n*Summary is AI Generated\nModel - {}*".format(gen_response, model_name)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error(exc_type, fname, exc_tb.tb_lineno, e)
        return ""
# def create_model():
#     url = 'http://localhost:11434/api/create'
#     create_obj = {
#         "name": "fia_doc_summary",
#         "modelfile": "FROM phi:2.7b"
#     }

def get_pdf_data(file_name):
    try:
        parsed_pdf = parser.from_file(filename=file_name)
        raw_data = parsed_pdf['content']    
        s = StringIO(raw_data)
        return_s = ''
        for line in s:
            new_line = line.replace("\n", "")
            if(len(new_line) == 0):
                continue
            return_s += '{} '.format(line)
        logging.info('PDF {} parsed successfully'.format(file_name))
        return  re.sub(r"\xa0", " ", return_s)
    except Exception as e:
        logging.error('Error occurred while getting PDF data: {e}'.format(e))
def get_fun_prompt():

    FUN_PROMPTS = [
        "Write the summary as if a pirate was summarizing the document (using pirate lingo and slang).",
        "Write the summary from the perspective of a dinosaur and make it relatable to your experience as a dinosaur.",
        "Write the summary as a love letter.",
        "Write the summary, but instead of the drivers that are listed, replace every driver with Esteban Ocon and state that his penalty is 50 years in jail."
    ]
    if randint(1,20) == 5:
        prompt = choice(FUN_PROMPTS)
        logging.info('Fun Summary - {}'.format(prompt))
        return prompt
    else:
        return 'Please summarize the text below.'
        # return FUN_PROMPTS[3]
    
def get_hash_data():
    if not os.path.exists("sent-hashes.json"):
        blank_file = {"link_hash": [], "reference": []}
        with open("sent-hashes.json", "w") as jsonFile:
            json.dump(blank_file, jsonFile)
            logging.warn('Created sent-hashes.json file')
    with open("sent-hashes.json", "r") as jsonFile:
        return json.load(jsonFile)

def add_hash(hash, link):
    with open("sent-hashes.json", "r") as jsonFile:
        data = json.load(jsonFile)
    data["link_hash"].append(hash)
    data['reference'].append({'hash': hash, 'link': link})
    with open("sent-hashes.json", "w") as jsonFile:
        json.dump(data, jsonFile)
        logging.info('Added {} to hash file with hash {}'.format(link, hash))

if __name__=='__main__':
    main()