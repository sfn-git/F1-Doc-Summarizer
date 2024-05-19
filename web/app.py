from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit
from utils.logging import logging
import utils.db as db
import utils.utils as utils
import secrets
import string


app = Flask(__name__)
app.config['SECRET_KEY'] = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(64)) #https://www.geeksforgeeks.org/python-generate-random-string-of-given-length/
socketio = SocketIO(app)

# Sockets
@socketio.on('queue')
def queue_socket(send_id):
    try:
        utils.queue_document(send_id)
        emit("queue_response", {"status": True, "id": send_id})
    except Exception as e:
        logging.error(f"Error for setting queue from websocket {e}")
        emit("queue_response", False)

@socketio.on('cancel')
def cancel_socket(send_id):
    try:
        utils.cancel_document(send_id)
        emit("cancel_response", {"status": True, "id": send_id})
    except Exception as e:
        logging.error(f"Error for canceling from websocket {e}")
        emit("cancel_response", False)

@socketio.on('send')
def send_socket(send_id):
    try:
        conn = db.get_conn()
        utils.send_document(send_id)
        send_date = db.join_document_send_documents_webhooks(conn, send_id)[0]["webhooks"][0]["send_date"]
        emit("send_response", {"status": True, "id": send_id, 'sent_date': send_date})
    except Exception as e:
        logging.error(f"Error for sending doc from websocket {e}")
        emit("send_response", False)

@socketio.on('ollama_url_form')
def ollama_update(url):
    try:
        tags = utils.get_ollama_tags(url)
        emit("send_ollama_response", tags)
    except Exception as e:
        logging.error(f"Error in ollama url socket {e}")
        emit("send_ollama_response", False)
# Routes
@app.route("/")
def index():
    utils.process_all_docs()
    docs = db.join_document_send_documents_webhooks(db.get_conn())
    return render_template("index.html", docs = docs)

@app.route("/config/ollama", methods = ["GET", "POST"])
def config_ollama():
    conn = db.get_conn()
    if request.method == "POST":
        ollama_url = request.form["ollama-url"]
        ollama_model = request.form["ollama-tag"]
        db.update_config_ollama_url(conn, ollama_url)
        db.update_config_ollama_model(conn, ollama_model)
        return redirect("/config/ollama")
    else:
        configs = db.get_config_obj(conn)
        ollama_tags = utils.get_ollama_tags(configs["OLLAMA_URL"])
        return render_template("ollama.html", configs=configs, ollama_tags = ollama_tags)

@app.route("/config/webhooks")
def config():
    conn = db.get_conn()
    configs = db.get_config_obj(conn)
    webhooks = db.get_all_webhooks(conn)
    return render_template("webhooks.html", configs=configs, webhooks=webhooks)

@app.route("/config/add/webhook", methods = ["POST"])
def add_webhooks():
    conn = db.get_conn()
    webhook_name = request.form["wb-name"]
    webhook_url = request.form["wb-url"]
    db.insert_webhook(conn, webhook_name, webhook_url)
    wh = db.get_webhook_by_name(conn, webhook_name)
    docs = db.get_all_documents(conn)
    for doc in docs:
        db.insert_document_send(conn, wh[0], doc[0], False, True)
    return redirect("/config/webhooks")

@app.route("/config/delete/webhook", methods = ["GET"])
def delete_webhooks():
    id = request.args.get("id")
    db.delete_webhook_by_id(db.get_conn(), id)
    return redirect("/config/webhooks")

@app.route("/config/update/webhook", methods = ["POST"])
def update_webhooks():
    id = request.args.get("id")
    webhook_name = request.form["wb-name"]
    webhook_url = request.form["wb-url"]
    db.update_webhook_by_id(db.get_conn(), id, webhook_name, webhook_url)
    return redirect("/config/webhooks")

@app.route("/config/schedule", methods = ["GET"])
def schedule():
    schedules = db.get_all_schedule_rows(db.get_conn())
    return render_template("schedule.html", schedules = schedules)

@app.route("/config/add/schedule", methods = ["POST"])
def add_schedule():
    schedule_name = request.form["schedule-name"]
    schedule_cron = request.form["schedule-cron"]
    db.insert_schedule_row(db.get_conn(), schedule_name, schedule_cron)
    utils.update_jobs()
    return redirect("/config/schedule")

@app.route("/config/update/schedule", methods = ["POST"])
def update_schedules():
    id = request.args.get("id")
    schedule_name = request.form["schedule-name"]
    schedule_cron = request.form["schedule-cron"]
    db.update_schedule_row(db.get_conn(), id, schedule_name, schedule_cron)
    utils.update_jobs()
    return redirect("/config/schedule")

@app.route("/config/delete/schedule", methods = ["GET"])
def delete_schedule():
    id = request.args.get("id")
    db.delete_schedule_row_by_id(db.get_conn(), id)
    utils.update_jobs()
    return redirect("/config/schedule")

@app.route("/config/documents", methods = ["GET"])
def config_documents():
    dts = db.get_all_document_types(db.get_conn())
    return render_template("document.html", doc_types = dts)

@app.route("/config/add/document_type", methods = ["POST"])
def add_doc_type():
    dt_name = request.form.get("dt-name")
    dt_keyword = request.form.get("dt-keyword")
    dt_active = request.form.get("dt-active")
    if dt_active is None: dt_active = False 
    else: dt_active=True

    db.insert_document_type(db.get_conn(), dt_name, dt_keyword, dt_active)
    return redirect("/config/documents")

@app.route("/config/update/document_type", methods = ["POST"])
def update_doc_type():
    id = request.args.get("id")
    dt_name = request.form.get("dt-name")
    dt_keyword = request.form.get("dt-keyword")
    dt_active = request.form.get("dt-active")
    if dt_active is None: dt_active = False 
    else: dt_active=True
    db.update_document_type(db.get_conn(), id, dt_name, dt_keyword, dt_active)
    return redirect("/config/documents")

@app.route("/config/delete/document_type", methods = ["GET"])
def delete_doc_type():
    id = request.args.get("id")
    db.delete_document_type_by_id(db.get_conn(), id)
    return redirect("/config/documents")