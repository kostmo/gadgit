import os
import sqlite3


DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')


CREATE_TABLE_LOGS = """
CREATE TABLE IF NOT EXISTS command_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT,
    duration FLOAT,
    return_code INTEGER,
    stdout TEXT,
    stderr TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_TABLE_GITHUB_EVENTS = """
CREATE TABLE IF NOT EXISTS github_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


TABLE_CREATION_COMMANDS = [
    CREATE_TABLE_LOGS,
    CREATE_TABLE_GITHUB_EVENTS,
]


def db_connect(db_path=DEFAULT_PATH):
    return sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)


def initialize_db():
    with db_connect() as conn:
        cur = conn.cursor()

        for table_creation_sql in TABLE_CREATION_COMMANDS:
            cur.execute(table_creation_sql)


def insert_operation_log(operation, duration, command_result_obj):

    with db_connect() as conn:
        cur = conn.cursor()
        values_to_insert = (operation, duration, command_result_obj.return_code, command_result_obj.stdout, command_result_obj.stderr)
        cur.execute("INSERT INTO command_logs (operation, duration, return_code, stdout, stderr) VALUES (?, ?, ?, ?, ?)", values_to_insert)
        conn.commit()


def insert_event(event_type):

    with db_connect() as conn:
        cur = conn.cursor()

        cur.execute("INSERT INTO github_events (event) VALUES (?);", (event_type,))

        cur.execute("SELECT last_insert_rowid();")
        row_id = cur.fetchone()[0]

        conn.commit()
        return row_id


def get_operation_logs(operation):

    sql = "SELECT duration, created_at, return_code, stdout, stderr FROM command_logs WHERE operation = ? ORDER BY created_at DESC LIMIT 30"
    with db_connect() as conn:
        cur = conn.cursor()  # instantiate a cursor obj
        cur.execute(sql, (operation,))
        return cur.fetchall()


def get_github_event_logs():

    sql = "SELECT id, event, received_at FROM github_events ORDER BY id DESC LIMIT 50"
    with db_connect() as conn:
        cur = conn.cursor()  # instantiate a cursor obj
        cur.execute(sql)
        return cur.fetchall()


def clear_command_logs():
    os.remove(DEFAULT_PATH)
    initialize_db()

