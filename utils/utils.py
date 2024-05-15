import pytz
import requests
import utils.constants as constants
import utils.db as db
import os
import re
from datetime import datetime
from random import choice, randint
from utils.logging import logging
from bs4 import BeautifulSoup
from hashlib import md5
from sys import exc_info
from tika import parser
from io import StringIO
from urllib.parse import quote
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler

#Scheduler
sched = BackgroundScheduler(daemon=True)
sched.start()

def get_current_datetime():
    curr_time = datetime.now()
    return curr_time

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

def get_ollama_tags(ollama_url):

    try:
        tag_url = "{}{}".format(ollama_url, '/api/tags')
        tags = requests.get(tag_url, timeout=3)
        tags_response = tags.json()
        return tags_response
    except Exception as e:
        logging.error("Failed to retrieve tags {}".format(e))
        return None
    
def get_md5_hash(string):
    return md5(string.encode()).hexdigest()

#ChatGPT produced function
def parse_date_with_timezone(date_string, date_format, timezone_name):
    try:
        # Get the timezone object based on the provided timezone name
        timezone = pytz.timezone(timezone_name)
        # Parse the string into a datetime object
        datetime_obj = datetime.strptime(date_string, date_format)
        # Localize the datetime object to the specified timezone
        localized_datetime = timezone.localize(datetime_obj)
        return localized_datetime
    except ValueError as e:
        logging.error(f"Error parsing date: {e}")
        return None

def process_all_docs():
    try:
        documents_url = "{}/documents".format(constants.BASE_FIA_URL)
        req = requests.get(documents_url, allow_redirects=True)
        req.raise_for_status()
        logging.info('Hit to {} successful'.format(req.url))

        html = req.content.decode("utf-8")
        soup = BeautifulSoup(html, 'html.parser')
        
        all_docs = soup.find_all("li", {"class": "document-row"})
        conn = db.get_conn()

        # Loops all links retrieved from webpage
        for doc in all_docs:
            link = doc.a['href']
            doc_time = parse_date_with_timezone(doc.span.text, "%d.%m.%y %H:%M", "CET")
            if "/sites/default/files/decision-document" in link: #and "Miami" in link:
                for enum in constants.DOCUMENT_ENUMS:
                    if enum in link:
                        doc_hash = get_md5_hash(link)
                        db_doc = db.get_document_by_hash(conn, doc_hash)
                        if db_doc == None:
                            doc_split = link.split('/')
                            doc_name = doc_split[len(doc_split)-1].split('.pdf')[0]
                            db.insert_document(conn, doc_name, "{}{}".format(constants.BASE_FIA_URL, quote(link)), link, doc_hash, doc_time)
                            db_doc = db.get_document_by_hash(conn, doc_hash)
                            webhooks = db.get_all_webhooks(conn)
                            for wh in webhooks:
                                document_send_obj = db.search_document_send(conn, wh[0], db_doc[0])
                                if document_send_obj is None:
                                    db.insert_document_send(conn, wh[0], db_doc[0], False, False)
        return True
    except requests.exceptions.HTTPError as e:
        logging.error('Received failed status code from FIA main documents webpage.')
        return None
    except Exception as e:
        exc_type, exc_obj, exc_tb = exc_info()
        logging.error('An error ocurred and the FIA document could not be processed.', exc_type, exc_obj, exc_tb.tb_lineno, e)
        return None
    
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

def summarize_data(prompt):
    
    conn = db.get_conn()
    if(db.get_config_ollama_url(conn) == ""):
        return ""

    try:
        base_url = db.get_config_ollama_url(conn)
        model = db.get_config_ollama_model(conn)
        logging.info('(Model) {}'.format(model))
        url = '/api/generate'
        generate_obj = {
            "model": model,
            "prompt": "{}".format(prompt),
            "stream": False
        }
        logging.info('(Prompt) {}'.format(prompt).replace('\n', ' '))
        generate_res = requests.post("{}{}".format(base_url, url), json=generate_obj)
        generate_res.raise_for_status()
        gen_response = generate_res.json()['response']
        logging.info('(Response) {}'.format(gen_response).replace('\n', ' '))
        return "{}\n\n*Summary is AI Generated\nModel - {}*".format(gen_response, model)
    except Exception as e:
        exc_type, exc_obj, exc_tb = exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error(exc_type, fname, exc_tb.tb_lineno, e)
        return ""

def build_prompt(pdf_data):
    prompt = "Do not greet when responding. {} Bold each header. Stay strictly to the format below.\nRace: [<Year> Name of Race]\nDriver(s) Involved: [Only list the name of the Driver or car number if the name is not available]\nPenalties/Allegation/Decision: [Bullet point driver that was punished and the penalties]\nSummary: [Summarize the event that ocurred in the document]\n{}".format(get_fun_prompt(), pdf_data)
    return prompt
    
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
        result = requests.post(url, json = data)
        result.raise_for_status()
        return True
    except Exception as err:
        logging.error("Embed failed to send. {}".format(err))
        return False

def send_document(send_id):
    conn = db.get_conn()
    send_row = db.join_document_send_documents_webhooks(conn, send_id)[0]
    webhook_url = send_row["webhooks"][0]["webhook_link"]
    title = send_row["document_name"]
    doc_url = send_row["document_link"]
    doc_id = send_row["doc_id"]
    doc_time = send_row["document_date"]
    doc_summary = db.get_document_summary_by_doc_id(conn, doc_id)
    if doc_summary is None or doc_summary[3] == "":
        file_path = get_file_from_url(doc_url)
        pdf_data = get_pdf_data(file_path)
        prompt = build_prompt(pdf_data)
        summary = f"{doc_time}\n\n{summarize_data(prompt)}"
        ollama_url = db.get_config_ollama_url(conn)
        ollama_model = db.get_config_ollama_model(conn)
        db.insert_document_summary(conn, doc_id, summary, prompt, ollama_url, ollama_model)
    else:
        summary = doc_summary[3]
    status = sendMessage(webhook_url, title, summary, doc_url, None)
    if status:
        send_id = send_row["webhooks"][0]["send_id"]
        db.update_document_send_by_id(conn, send_id, 1, 0)
        db.update_document_send_date_by_send_id(conn, send_id)
    return True

def queue_document(send_id):
    conn = db.get_conn()
    queue_row = db.join_document_send_documents_webhooks(conn, send_id)[0]
    if queue_row is None:
        logging.warn(f'Not queuing send id {send_id} as it does not exist')
    else:
        db.update_document_send_by_id(conn, send_id, 0, 0)
    return True

def cancel_document(send_id):
    conn = db.get_conn()
    queue_row = db.join_document_send_documents_webhooks(conn, send_id)[0]
    if queue_row is None:
        logging.warn(f'Not queuing send id {send_id} as it does not exist')
    else:
        db.update_document_send_by_id(conn, send_id, 0, 1)
    return True

def get_latest_fia_docs():
    try:
        logging.info("Running FIA Docs Job")
        process_all_docs()
        conn = db.get_conn()
        doc_ids = db.get_documents_to_send_ids(conn)
        for id in doc_ids:
            send_document(id[0])
    except Exception as e:
        logging.error('An error ocurred in the job process: {}'.format(e))

def update_jobs():
    
    conn = db.get_conn()
    jobs = db.get_all_schedule_rows(conn)

    sched.remove_all_jobs()

    for job in jobs:
        job_id = job[0]
        job_name = job[1]
        try:
            trigger = CronTrigger.from_crontab(job[2])
        except Exception as e:
            logging.warn(f"Job ({job_name}) was not added to the scheduler.")
            continue
        sched.add_job(get_latest_fia_docs, trigger=trigger, id=f"{job_id}", name=job_name)
    return True