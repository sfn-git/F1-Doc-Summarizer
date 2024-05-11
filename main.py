import utils.db as db
from utils.discord_webhook import sendMessage
from sys import exit
from utils.logging import logging
import utils.utils as utils

data = db.get_config_obj(db.get_conn())

def main():    
    get_latest_fia_docs()

def get_latest_fia_docs():

    try:
        logging.info("Running FIA Docs Job")
        utils.process_all_docs()
        conn = db.get_conn()
        send_ids = db.get_documents_to_send_ids(conn)

        for id in send_ids:
            print(id)
            utils.send_document(id[0])
    except Exception as e:
        logging.error('An error ocurred in the job process: {}'.format(e))
        exit()

if __name__=='__main__':
    main()