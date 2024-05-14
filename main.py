import utils.db as db
import utils.utils as utils
from web.app import app
from apscheduler.schedulers.background import BackgroundScheduler

data = db.get_config_obj(db.get_conn())
sched = BackgroundScheduler(daemon=True)

def main():    
    # Create Schedules
    sched.start()
    utils.update_jobs(sched)
    from waitress import serve
    serve(app, host='0.0.0.0', port=8080)

if __name__=='__main__':
    main()