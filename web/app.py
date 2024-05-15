from flask import Flask, render_template, request, redirect
import utils.db as db
import utils.utils as utils

app = Flask(__name__)

# Routes
@app.route("/")
def index():
    utils.process_all_docs()
    docs = db.join_document_send_documents_webhooks(db.get_conn())
    return render_template("index.html", docs = docs)

@app.route("/send")
def send():
    conn = db.get_conn()
    send_id = request.args.get("id")
    utils.send_document(send_id)
    return redirect("/")

@app.route("/queue")
def queue():
    send_id = request.args.get("id")
    utils.queue_document(send_id)
    return redirect("/")

@app.route("/cancel")
def cancel():
    send_id = request.args.get("id")
    utils.cancel_document(send_id)
    return redirect("/")

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
    conn = db.get_conn()
    id = request.args.get("id")
    db.delete_webhook_by_id(conn, id)
    return redirect("/config/webhooks")

@app.route("/config/update/webhook", methods = ["POST"])
def update_webhooks():
    conn = db.get_conn()
    id = request.args.get("id")
    webhook_name = request.form["wb-name"]
    webhook_url = request.form["wb-url"]
    db.update_webhook_by_id(conn, id, webhook_name, webhook_url)
    return redirect("/config/webhooks")

@app.route("/config/schedule", methods = ["GET"])
def schedule():
    conn = db.get_conn()
    schedules = db.get_all_schedule_rows(conn)
    return render_template("schedule.html", schedules = schedules)

@app.route("/config/add/schedule", methods = ["POST"])
def add_schedule():
    conn = db.get_conn()
    schedule_name = request.form["schedule-name"]
    schedule_cron = request.form["schedule-cron"]
    db.insert_schedule_row(conn, schedule_name, schedule_cron)
    utils.update_jobs()
    return redirect("/config/schedule")

@app.route("/config/update/schedule", methods = ["POST"])
def update_schedules():
    conn = db.get_conn()
    id = request.args.get("id")
    schedule_name = request.form["schedule-name"]
    schedule_cron = request.form["schedule-cron"]
    db.update_schedule_row(conn, id, schedule_name, schedule_cron)
    utils.update_jobs()
    return redirect("/config/schedule")

@app.route("/config/delete/schedule", methods = ["GET"])
def delete_schedule():
    conn = db.get_conn()
    id = request.args.get("id")
    db.delete_schedule_row_by_id(conn, id)
    utils.update_jobs()
    return redirect("/config/schedule")