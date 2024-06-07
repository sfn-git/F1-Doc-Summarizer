from utils.logging import logging
from datetime import datetime
import os
import sqlite3
import utils.constants as constants

def now():
    return datetime.now()

#CHATGPT GENERATED CODE START#
# CURD Functions 
# Function to insert into config table
def insert_config(conn, env, skip_summary, hash_only, ollama_url, ollama_model):
    sql = """INSERT INTO config(env, skip_summary, hash_only, ollama_url, ollama_model, created_date, updated_date) 
             VALUES (?, ?, ?, ?, ?, ?, ?)"""
    created_date = now()
    updated_date = now()
    values = (env, skip_summary, hash_only, ollama_url, ollama_model, created_date, updated_date)
    cursor = conn.cursor()
    cursor.execute(sql, values)
    conn.commit()

# Function to get all rows from config table
def get_all_configs(conn):
    sql = "SELECT * FROM config"
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchone()

# Function to insert into webhooks table
def insert_webhook(conn, name, link):
    sql = """INSERT INTO webhooks(name, link, date_added, date_updated) 
             VALUES (?, ?, ?, ?)"""
    date_added = now()
    date_updated = now()
    values = (name, link, date_added, date_updated)
    cursor = conn.cursor()
    cursor.execute(sql, values)
    conn.commit()

# Function to get all rows from webhooks table
def get_all_webhooks(conn):
    sql = "SELECT * FROM webhooks"
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()

def delete_webhook_by_id(conn, wh_id):
    try:
        cursor = conn.cursor()
        # Attempt to delete from document_send table first
        cursor.execute("""
            DELETE FROM document_send
            WHERE wh_id = ?
        """, (wh_id,))
        # Now delete the webhook from webhooks table
        cursor.execute("""
            DELETE FROM webhooks
            WHERE wh_id = ?
        """, (wh_id,))
        # Commit the transaction
        conn.commit()
        # Check if any rows were affected
        if cursor.rowcount > 0:
            logging.info(f"Webhook with wh_id = {wh_id} deleted successfully.")
        else:
            logging.warn(f"No webhook found with wh_id = {wh_id}. No deletion performed.")
    except sqlite3.Error as e:
        # Rollback the transaction in case of error
        conn.rollback()
        logging.error(f"Error deleting webhook: {e}")

# Function to update values of a webhook by its ID
def update_webhook_by_id(conn, wh_id, new_name=None, new_link=None):
    # Prepare the update assignments for the SQL statement
    update_assignments = []

    # Check if new_name is provided for update
    if new_name is not None:
        update_assignments.append(f" name = '{new_name}'")

    # Check if new_link is provided for update
    if new_link is not None:
        update_assignments.append(f" link = '{new_link}'")

    # Append the 'date_updated' assignment with the current timestamp
    update_assignments.append(f" date_updated = '{now()}'")

    # Construct the SQL UPDATE statement
    sql = "UPDATE webhooks SET "
    sql += ", ".join(update_assignments)
    sql += f" WHERE wh_id = {wh_id}"

    # Execute the SQL UPDATE statement
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()

def get_webhook_by_name(conn, webhook_name):
    try:
        cursor = conn.cursor()

        # SQL query to select the webhook by name
        query = """
            SELECT *
            FROM webhooks
            WHERE name = ?
        """

        cursor.execute(query, (webhook_name,))
        row = cursor.fetchone()

        return row
    except sqlite3.Error as e:
        logging.error(f"Error retrieving webhook: {e}")
        return None

# Function to insert into documents table
def insert_document(conn, name, link, path, hash_value, document_date):
    sql = """INSERT INTO documents(name, link, path, hash, document_date, date_added) 
             VALUES (?,?,?,?,?,?)"""
    date_added = now()
    values = (name, link, path, hash_value, document_date, date_added)
    cursor = conn.cursor()
    cursor.execute(sql, values)
    conn.commit()

# Function to get all rows from documents table
def get_all_documents(conn):
    sql = "SELECT * FROM documents"
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()

def get_document_by_hash(conn, document_hash):
    sql = "SELECT * FROM documents WHERE hash = ?"
    cursor = conn.cursor()
    cursor.execute(sql, (document_hash,))
    document = cursor.fetchone()  # Fetch one row (document) or None if not found
    return document

# Function to insert into document_send table
def insert_document_send(conn, wh_id, doc_id, sent, skip):
    sql = """INSERT INTO document_send(wh_id, doc_id, sent, skip, date) 
             VALUES (?, ?, ?, ?, ?)"""
    date = now()
    values = (wh_id, doc_id, sent, skip, date)
    cursor = conn.cursor()
    cursor.execute(sql, values)
    conn.commit()

# Function to get all rows from document_send table
def get_all_document_sends(conn):
    sql = "SELECT * FROM document_send"
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()

def get_documents_to_send_ids(conn):
    try:
        cursor = conn.cursor()
        # SQL query to select rows from document_send where sent and skip are both 0
        query = """
            SELECT send_id
            FROM document_send
            WHERE sent = 0 and skip = 0
            ORDER BY (
                SELECT document_date FROM documents WHERE documents.doc_id = document_send.doc_id
            ) ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            return rows  # Return the raw rows directly
        else:
            logging.info("No documents found where sent and skip is 0.")
            return []
    except sqlite3.Error as e:
        logging.error(f"Error retrieving documents to send: {e}")
        return []

def update_document_send_by_id(conn, send_id, new_sent_value, new_skip_value):
    try:
        cursor = conn.cursor()
        query = """
            UPDATE document_send
            SET sent = ?,
                skip = ?
            WHERE send_id = ?
        """
        cursor.execute(query, (new_sent_value, new_skip_value, send_id))
        conn.commit()
        if cursor.rowcount > 0:
            logging.info(f"sent and skip columns updated successfully for send_id = {send_id}.")
        else:
            logging.warn(f"No document_send row found with send_id = {send_id}. No update performed.")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error updating document_send sent and skip columns: {e}")

def update_document_send_date_by_send_id(conn, send_id):
    try:
        cursor = conn.cursor()
        current_time = now()
        query = """
            UPDATE document_send
            SET date = ?
            WHERE send_id = ?
        """
        cursor.execute(query, (current_time, send_id))
        conn.commit()
        if cursor.rowcount > 0:
            logging.info(f"Date updated successfully for send_id = {send_id}.")
        else:
            logging.info(f"No document_send row found with send_id = {send_id}. No update performed.")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error updating document_send date column: {e}")

# Function to retrieve the 'env' column value
def get_config_env(conn):
    row = get_all_configs(conn)
    if row:
        return row[0]  # Assuming 'env' is the first column (index 0)
    else:
        return None

# Function to retrieve the 'skip_summary' column value
def get_config_skip_summary(conn):
    row = get_all_configs(conn)
    if row:
        return row[1]  # Assuming 'skip_summary' is the second column (index 1)
    else:
        return None

# Function to retrieve the 'hash_only' column value
def get_config_hash_only(conn):
    row = get_all_configs(conn)
    if row:
        return row[2]  # Assuming 'hash_only' is the third column (index 2)
    else:
        return None

# Function to retrieve the 'ollama_url' column value
def get_config_ollama_url(conn):
    row = get_all_configs(conn)
    if row:
        return row[3]  # Assuming 'ollama_url' is the fourth column (index 3)
    else:
        return None

# Function to retrieve the 'ollama_model' column value
def get_config_ollama_model(conn):
    row = get_all_configs(conn)
    if row:
        return row[4]  # Assuming 'ollama_model' is the fifth column (index 4)
    else:
        return None

# Function to retrieve the 'created_date' column value
def get_config_created_date(conn):
    row = get_all_configs(conn)
    if row:
        return row[5]  # Assuming 'created_date' is the sixth column (index 5)
    else:
        return None

# Function to retrieve the 'updated_date' column value
def get_config_updated_date(conn):
    row = get_all_configs(conn)
    if row:
        return row[6]  # Assuming 'updated_date' is the seventh column (index 6)
    else:
        return None
    
# Function to update the 'env' column value and 'updated_date'
def update_config_env(conn, new_env):
    update_config_column(conn, 'env', new_env)

# Function to update the 'skip_summary' column value and 'updated_date'
def update_config_skip_summary(conn, new_skip_summary):
    update_config_column(conn, 'skip_summary', new_skip_summary)

# Function to update the 'hash_only' column value and 'updated_date'
def update_config_hash_only(conn, new_hash_only):
    update_config_column(conn, 'hash_only', new_hash_only)

# Function to update the 'ollama_url' column value and 'updated_date'
def update_config_ollama_url(conn, new_ollama_url):
    update_config_column(conn, 'ollama_url', new_ollama_url)

# Function to update the 'ollama_model' column value and 'updated_date'
def update_config_ollama_model(conn, new_ollama_model):
    update_config_column(conn, 'ollama_model', new_ollama_model)

# Generic function to update a specific column and 'updated_date'
def update_config_column(conn, column_name, new_value):
    new_updated_date = now()
    sql = f"UPDATE config SET {column_name} = ?, updated_date = ?"
    cursor = conn.cursor()
    cursor.execute(sql, (new_value, new_updated_date))
    conn.commit()

def join_document_send_documents_webhooks(conn, send_id=None):
    try:
        cursor = conn.cursor()
        if send_id == None:
            # SQL query to join document_send, documents, and webhooks tables and sort by document_date DESC and webhook date_added DESC
            query = """
                SELECT d.doc_id, d.name AS document_name, d.link AS document_link, d.path AS document_path, d.hash AS document_hash,
                    d.document_date AS document_date, d.date_added AS document_date_added,
                    ds.send_id, ds.sent, ds.skip, ds.date AS send_date,
                    w.wh_id, w.name AS webhook_name, w.link AS webhook_link, w.date_added AS webhook_date_added
                FROM document_send AS ds
                JOIN webhooks AS w ON ds.wh_id = w.wh_id
                JOIN documents AS d ON ds.doc_id = d.doc_id
                ORDER BY d.document_date DESC, w.date_added DESC
            """
            cursor.execute(query)
        else:
            query = """
                SELECT d.doc_id, d.name AS document_name, d.link AS document_link, d.path AS document_path, d.hash AS document_hash,
                    d.document_date AS document_date, d.date_added AS document_date_added,
                    ds.send_id, ds.sent, ds.skip, ds.date AS send_date,
                    w.wh_id, w.name AS webhook_name, w.link AS webhook_link, w.date_added AS webhook_date_added
                FROM document_send AS ds
                JOIN webhooks AS w ON ds.wh_id = w.wh_id
                JOIN documents AS d ON ds.doc_id = d.doc_id
                WHERE ds.send_id = ?
            """
            cursor.execute(query, [send_id])

        
        rows = cursor.fetchall()
        # Dictionary to store document data by doc_id
        document_data = {}

        for row in rows:
            doc_id = row[0]

            # Create a document entry if not exists
            if doc_id not in document_data:
                document_data[doc_id] = {
                    'doc_id': doc_id,
                    'document_name': row[1],
                    'document_link': row[2],
                    'document_path': row[3],
                    'document_hash': row[4],
                    'document_date': row[5],
                    'document_date_added': row[6],
                    'webhooks': []
                }

            # Create a webhook entry
            webhook_info = {
                'wh_id': row[11],
                'webhook_name': row[12],
                'webhook_link': row[13],
                'webhook_date_added': row[14],
                'send_id': row[7],
                'sent': row[8],
                'skip': row[9],
                'send_date': row[10]
            }

            # Append webhook info to the document's webhooks list
            document_data[doc_id]['webhooks'].append(webhook_info)

        # Convert document_data dictionary values to a list of documents
        result = list(document_data.values())

        return result

    except sqlite3.Error as e:
        logging.error(f"Error executing SQL query: {e}")
        return None

def get_document_by_id(conn, doc_id):
    try:
        cursor = conn.cursor()

        # SQL query to retrieve document details by doc_id
        query = """
            SELECT d.doc_id, d.name AS document_name, d.link AS document_link, d.path AS document_path, d.hash AS document_hash,
                   d.document_date AS document_date, d.date_added AS document_date_added,
                   w.wh_id, w.name AS webhook_name, w.link AS webhook_link, w.date_added AS webhook_date_added,
                   ds.sent, ds.skip, ds.date AS send_date
            FROM documents AS d
            JOIN document_send AS ds ON d.doc_id = ds.doc_id
            JOIN webhooks AS w ON ds.wh_id = w.wh_id
            WHERE d.doc_id = ?
        """

        cursor.execute(query, (doc_id,))
        row = cursor.fetchone()

        if row:
            document_info = {
                'doc_id': row[0],
                'document_name': row[1],
                'document_link': row[2],
                'document_path': row[3],
                'document_hash': row[4],
                'document_date': row[5],
                'document_date_added': row[6],
                'webhook_wh_id': row[7],
                'webhook_name': row[8],
                'webhook_link': row[9],
                'webhook_date_added': row[10],
                'sent': row[11],
                'skip': row[12],
                'send_date': row[13]
            }
            return document_info
        else:
            logging.warn(f"No document found with doc_id {doc_id}")
            return None

    except sqlite3.Error as e:
        logging.error(f"Error executing SQL query: {e}")
        return None

def search_document_send(conn, wh_id, doc_id):
    try:
        cursor = conn.cursor()

        # SQL query to search document_send by webhook ID and document ID
        query = """
            SELECT *
            FROM document_send
            WHERE wh_id = ? AND doc_id = ?
        """

        cursor.execute(query, (wh_id, doc_id))
        row = cursor.fetchone()

        if row:
            send_info = {
                'send_id': row[0],
                'wh_id': row[1],
                'doc_id': row[2],
                'sent': row[3],
                'skip': row[4],
                'date': row[5]
            }
            return send_info
        else:
            logging.warn(f"No rows found for wh_id = {wh_id} and doc_id = {doc_id}")
            return None

    except sqlite3.Error as e:
        logging.error(f"Error executing SQL query: {e}")
        return None
    
def get_document_summary_by_doc_id(conn, doc_id):
    try:
        cursor = conn.cursor()
        query = """
            SELECT summary_id, doc_id, prompt, summary, date, ollama_url, ollama_model
            FROM document_summary
            WHERE doc_id = ?
        """
        cursor.execute(query, (doc_id,))
        rows = cursor.fetchone()
        if rows:
            return rows
        else:
            logging.info(f"No document summaries found for doc_id = {doc_id}.")
            return None
    except sqlite3.Error as e:
        logging.error(f"Error retrieving document summaries: {e}")
        return None
    
def insert_document_summary(conn, doc_id, summary, prompt, ollama_url, ollama_model):
    try:
        cursor = conn.cursor()
        current_date = now()
        query = """
            INSERT INTO document_summary (doc_id, prompt, summary, date, ollama_url, ollama_model)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (doc_id, prompt, summary, current_date, ollama_url, ollama_model))
        conn.commit()
        logging.info(f"Document summary inserted successfully for doc_id = {doc_id}.")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error inserting document summary: {e}")
def insert_schedule_row(conn, job_name, cron_timing):
    try:
        cursor = conn.cursor()
        current_date = now()
        query = """
            INSERT INTO schedule (job_name, cron_timing, date_added, date_updated)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (job_name, cron_timing, current_date, current_date))
        conn.commit()
        logging.info(f"Row inserted successfully into schedule table for job_name = {job_name}.")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error inserting row into schedule table: {e}")
def get_all_schedule_rows(conn):
    try:
        cursor = conn.cursor()
        query = """
            SELECT job_id, job_name, cron_timing, date_added, date_updated
            FROM schedule
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        logging.error(f"Error retrieving rows from schedule table: {e}")
        return []
def update_schedule_row(conn, job_id, job_name, cron_timing):
    try:
        cursor = conn.cursor()
        current_date = now()
        query = """
            UPDATE schedule
            SET job_name = ?, cron_timing = ?, date_updated = ?
            WHERE job_id = ?
        """
        cursor.execute(query, (job_name, cron_timing, current_date, job_id))
        conn.commit()
        logging.info(f"Schedule row updated successfully for job_id = {job_id}.")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error updating schedule row: {e}")
def delete_schedule_row_by_id(conn, job_id):
    try:
        cursor = conn.cursor()
        query = """
            DELETE FROM schedule
            WHERE job_id = ?
        """
        cursor.execute(query, (job_id,))
        conn.commit()
        logging.info(f"Schedule row deleted successfully for job_id = {job_id}.")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error deleting schedule row: {e}")
def get_schedule_row_by_id(conn, job_id):
    try:
        cursor = conn.cursor()
        query = """
            SELECT job_id, job_name, cron_timing, date_added, date_updated
            FROM schedule
            WHERE job_id = ?
        """
        cursor.execute(query, (job_id,))
        row = cursor.fetchone()
        return row
    except sqlite3.Error as e:
        logging.error(f"Error retrieving schedule row by id: {e}")
        return None
def insert_document_type(conn, name, keyword, active):
    try:
        cursor = conn.cursor()
        current_date = now()
        query = """
            INSERT INTO document_type (name, keyword, active, date_added, date_updated)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(query, (name, keyword, active, current_date, current_date))
        conn.commit()
        logging.info(f"Document type inserted successfully: name={name}, keyword={keyword}, active={active}.")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error inserting document type: {e}")
def update_document_type(conn, type_id, name, keyword, active):
    try:
        cursor = conn.cursor()
        current_date = now()
        query = """
            UPDATE document_type
            SET name = ?, keyword = ?, active = ?, date_updated = ?
            WHERE type_id = ?
        """
        cursor.execute(query, (name, keyword, active, current_date, type_id))
        conn.commit()
        logging.info(f"Document type updated successfully: type_id={type_id}, name={name}, keyword={keyword}, active={active}.")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error updating document type: {e}")
def search_document_type_by_name(conn, name):
    try:
        cursor = conn.cursor()
        query = """
            SELECT type_id, name, keyword, active, date_added, date_updated
            FROM document_type
            WHERE name = ?
        """
        cursor.execute(query, (name,))
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        logging.error(f"Error searching document type by name: {e}")
        return []
def delete_document_type_by_id(conn, type_id):
    try:
        cursor = conn.cursor()
        query = """
            DELETE FROM document_type
            WHERE type_id = ?
        """
        cursor.execute(query, (type_id,))
        conn.commit()
        logging.info(f"Document type deleted successfully: type_id={type_id}.")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error deleting document type: {e}")
def get_all_document_types(conn):
    try:
        cursor = conn.cursor()
        query = """
            SELECT type_id, name, keyword, active, date_added, date_updated
            FROM document_type
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        logging.error(f"Error retrieving all document types: {e}")
        return []
def get_active_document_types(conn):
    try:
        cursor = conn.cursor()
        query = """
            SELECT keyword
            FROM document_type
            WHERE active = 1
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        logging.error(f"Error retrieving active document types: {e}")
        return []
    
def insert_prompt(conn, name, prompt, prompt_type, link_id):
    try:
        cursor = conn.cursor()
        current_date = now()
        query = """
            INSERT INTO prompts (name, prompt, prompt_type, link_id, date_added, date_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (name, prompt, prompt_type, link_id, current_date, current_date))
        conn.commit()
        logging.info(f"Prompt inserted successfully: name={name}, prompt_type={prompt_type}, link_id={link_id}.")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error inserting prompt: {e}")

def update_prompt(conn, prompt_id, name=None, prompt=None, prompt_type=None, link_id=None):
    try:
        cursor = conn.cursor()
        current_date = now()
        update_fields = []
        update_values = []
        
        if name is not None:
            update_fields.append("name = ?")
            update_values.append(name)
        if prompt is not None:
            update_fields.append("prompt = ?")
            update_values.append(prompt)
        if prompt_type is not None:
            update_fields.append("prompt_type = ?")
            update_values.append(prompt_type)
        if link_id is not None:
            update_fields.append("link_id = ?")
            update_values.append(link_id)
        
        update_fields.append("date_updated = ?")
        update_values.append(current_date)
        update_values.append(prompt_id)
        
        query = f"""
            UPDATE prompts
            SET {", ".join(update_fields)}
            WHERE prompt_id = ?
        """
        cursor.execute(query, update_values)
        conn.commit()
        logging.info(f"Prompt updated successfully: prompt_id={prompt_id}.")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error updating prompt: {e}")

def get_prompt_by_id(conn, prompt_id):
    try:
        cursor = conn.cursor()
        query = """
            SELECT prompt_id, name, prompt, prompt_type, link_id, date_added, date_updated
            FROM prompts
            WHERE prompt_id = ?
        """
        cursor.execute(query, (prompt_id,))
        row = cursor.fetchone()
        return row
    except sqlite3.Error as e:
        logging.error(f"Error retrieving prompt by id: {e}")
        return None

def get_prompts_by_type(conn, prompt_type):
    try:
        cursor = conn.cursor()
        query = """
            SELECT prompt_id, name, prompt, prompt_type, link_id, date_added, date_updated
            FROM prompts
            WHERE prompt_type = ?
        """
        cursor.execute(query, (prompt_type,))
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        logging.error(f"Error retrieving prompts by type: {e}")
        return []

def delete_prompt_by_id(conn, prompt_id):
    try:
        cursor = conn.cursor()
        query = """
            DELETE FROM prompts
            WHERE prompt_id = ?
        """
        cursor.execute(query, (prompt_id,))
        conn.commit()
        logging.info(f"Prompt deleted successfully: prompt_id={prompt_id}.")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error deleting prompt: {e}")

def get_system_prompt(conn):
    try:
        cursor = conn.cursor()
        query = """
            SELECT prompt_id, name, prompt, prompt_type, link_id, date_added, date_updated
            FROM prompts
            WHERE prompt_type = 'SYSTEM'
            LIMIT 1
        """
        cursor.execute(query)
        row = cursor.fetchone()
        return row
    except sqlite3.Error as e:
        logging.error(f"Error retrieving SYSTEM prompt: {e}")
        return None
#CHATGPT GENERATED CODE END#

def get_config_obj(conn):

    return {
        "ENV": get_config_env(conn),
        "OLLAMA_URL": get_config_ollama_url(conn),
        "OLLAMA_TAG": get_config_ollama_model(conn),
        "CREATED_DATE": get_config_created_date(conn),
        "LAST_UPDATED": get_config_updated_date(conn)
    }

CONFIG_FILE_PATH = "./config/config.db"

if not os.path.exists('./config'):
    os.makedirs('./config')

def get_conn():
    first_run = False
    if not os.path.exists(CONFIG_FILE_PATH):
        first_run = True
    conn = sqlite3.connect(CONFIG_FILE_PATH)
    cur = conn.cursor()
    cur.execute(constants.CREATE_CONFIG_TABLE)
    cur.execute(constants.CREATE_WEBHOOKS_TABLE)
    cur.execute(constants.CREATE_DOCUMENTS_TABLE)
    cur.execute(constants.CREATE_DOCUMENTS_SEND_TABLE)
    cur.execute(constants.CREATE_DOC_SUMMARY_TABLE)
    cur.execute(constants.CREATE_SCHEDULE_TABLE)
    cur.execute(constants.CREATE_DOCUMENT_TYPE_TABLE)
    cur.execute(constants.CREATE_PROMPT_TABLE)

    if first_run:
        insert_config(conn, 'dev', False, True, '', '')
        insert_document_type(conn, 'All', 'all', False)
        insert_document_type(conn, 'Summons', 'summons', False)
        insert_document_type(conn, 'Decision', 'decision', False)
        insert_document_type(conn, 'Infringement', 'infringement', False)
        insert_prompt(conn, "DEFAULT_SYSTEM", constants.DEFAULT_SYSTEM_PROMPT, "SYSTEM", None)

    conn.commit()
    conn.close()
    return sqlite3.connect(CONFIG_FILE_PATH)