from flask import Flask, render_template, request, redirect
import utils.db as db
import utils.constants as const
import utils.utils as utils 

app = Flask(__name__)

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

@app.route("/config")
def config():
    conn = db.get_conn()
    configs = db.get_config_obj(conn)
    ollama_tags = utils.get_ollama_tags(configs["OLLAMA_URL"])
    webhooks = db.get_all_webhooks(conn)
    return render_template("config.html", configs=configs, ollama_tags = ollama_tags, webhooks=webhooks)

@app.route("/config/ollama", methods = ["POST"])
def config_ollama():
    conn = db.get_conn()
    ollama_url = request.form["ollama-url"]
    ollama_model = request.form["ollama-tag"]
    db.update_config_ollama_url(conn, ollama_url)
    db.update_config_ollama_model(conn, ollama_model)
    return redirect("/config")

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
    return redirect("/config")

@app.route("/config/delete/webhook", methods = ["GET"])
def delete_webhooks():
    conn = db.get_conn()
    id = request.args.get("id")
    db.delete_webhook_by_id(conn, id)
    return redirect("/config")

@app.route("/config/update/webhook", methods = ["POST"])
def update_webhooks():
    conn = db.get_conn()
    id = request.args.get("id")
    webhook_name = request.form["wb-name"]
    webhook_url = request.form["wb-url"]
    db.update_webhook_by_id(conn, id, webhook_name, webhook_url)
    return redirect("/config")