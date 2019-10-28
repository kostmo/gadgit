import os
import sqlite3

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')


def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con


def initialize_db():
    with db_connect() as conn:
        cur = conn.cursor()  # instantiate a cursor obj
        cur.execute(CREATE_TABLE_LOGS)


def insert_operation_log(operation, duration, content):

    with db_connect() as conn:
        cur = conn.cursor()  # instantiate a cursor obj

        # Insert a row of data
        cur.execute("INSERT INTO command_logs (operation, duration, content) VALUES (?, ?, ?)", (operation, duration, content))

        # Save (commit) the changes
        conn.commit()


def get_operation_logs(operation):

    sql = "SELECT duration, content, created_at FROM command_logs WHERE operation = ? ORDER BY created_at DESC"
    with db_connect() as conn:
        cur = conn.cursor()  # instantiate a cursor obj
        cur.execute(sql, (operation,))
        return cur.fetchall()


CREATE_TABLE_LOGS = """
CREATE TABLE IF NOT EXISTS command_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation text,
    duration float,
    content text,
    created_at integer DEFAULT CURRENT_TIME
)
"""