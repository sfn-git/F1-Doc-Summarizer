# CREATES -----------------------------------------------
CREATE_CONFIG_TABLE = """CREATE TABLE IF NOT EXISTS config(
    env TEXT, 
    skip_summary BOOLEAN,
    hash_only BOOLEAN,
    ollama_url TEXT,
    ollama_model TEXT,
    created_date DATE,
    updated_date DATE
    )"""
CREATE_WEBHOOKS_TABLE = """CREATE TABLE IF NOT EXISTS webhooks(
    wh_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    link TEXT,
    date_added DATE,
    date_updated DATE
)
"""
CREATE_DOCUMENTS_TABLE = """CREATE TABLE IF NOT EXISTS documents(
    doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    link TEXT,
    path TEXT,
    hash TEXT,
    document_date DATE,
    date_added DATE
)"""
CREATE_DOCUMENTS_SEND_TABLE = """CREATE TABLE IF NOT EXISTS document_send(
    send_id INTEGER PRIMARY KEY AUTOINCREMENT,
    wh_id INTEGER,
    doc_id INTEGER,
    sent BOOLEAN,
    skip BOOLEAN,
    date DATE,
    CONSTRAINT webhook_fk
        FOREIGN KEY (wh_id) REFERENCES webhooks (wh_id)
    CONSTRAINT docs_fk
    FOREIGN KEY (doc_id) REFERENCES webhooks (doc_id)
)"""

BASE_FIA_URL = "https://www.fia.com"
DOCUMENT_ENUMS = ["Summons", "Decision", "Infringement"]