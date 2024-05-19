import utils.utils as utils
from web.app import socketio as io
from web.app import app

def main():    
    # Create Schedules
    utils.update_jobs()
    io.run(app, host="0.0.0.0", port=8080, allow_unsafe_werkzeug=True) #Will look at WSGI server in the future

if __name__=='__main__':
    main()