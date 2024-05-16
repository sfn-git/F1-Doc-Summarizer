import utils.db as db
import utils.utils as utils
from web.app import socketio

data = db.get_config_obj(db.get_conn())

def main():    
    # Create Schedules
    utils.update_jobs()
    from waitress import serve
    serve(socketio, host='0.0.0.0', port=8080)

if __name__=='__main__':
    main()