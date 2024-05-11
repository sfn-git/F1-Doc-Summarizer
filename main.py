import utils.db as db
from utils.discord_webhook import sendMessage
from sys import exit
from utils.logging import logging

data = db.get_config_obj(db.get_conn())

def main():    
    get_latest_fia_docs()

def get_latest_fia_docs():

    try:
        print("Main job")
    except Exception as e:
        logging.error('An error ocurred and the FIA document could not be processed: {}'.format(e))
        exit()

if __name__=='__main__':
    main()