import utils.db as db
from utils.discord_webhook import sendMessage
from sys import exit
from utils.logging import logging
import utils.utils as utils
from web.app import app
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

data = db.get_config_obj(db.get_conn())

def main():    
    # Create Schedules
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(
        get_latest_fia_docs,
        trigger=CronTrigger(day_of_week="fri, sat, sun", minute="*"),
        id='1',
        name='race_weekends'
    )
    sched.add_job(
        get_latest_fia_docs,
        trigger=CronTrigger(day_of_week="mon, tue, wed, thu", hour="*"),
        id='2',
        name='weekdays'
    )
    sched.start()
    from waitress import serve
    serve(app, host='0.0.0.0', port=8080)

def get_latest_fia_docs():
    try:
        logging.info("Running FIA Docs Job")
        utils.process_all_docs()
        conn = db.get_conn()
        doc_ids = db.get_documents_to_send_ids(conn)

        for id in doc_ids:
            utils.send_document(id[0])
    except Exception as e:
        logging.error('An error ocurred in the job process: {}'.format(e))

if __name__=='__main__':
    main()