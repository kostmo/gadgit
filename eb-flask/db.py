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


def insert_operation_log(operation, duration, command_result_obj):

    with db_connect() as conn:
        cur = conn.cursor()

        cur.execute("INSERT INTO command_logs (operation, duration, return_code, stdout, stderr) VALUES (?, ?, ?, ?, ?)",
                    (operation, duration, command_result_obj.return_code, command_result_obj.stdout, command_result_obj.stderr))

        conn.commit()


def get_operation_logs(operation):

    sql = "SELECT duration, created_at, return_code, stdout, stderr FROM command_logs WHERE operation = ? ORDER BY created_at DESC"
    with db_connect() as conn:
        cur = conn.cursor()  # instantiate a cursor obj
        cur.execute(sql, (operation,))
        return cur.fetchall()


CREATE_TABLE_LOGS = """
CREATE TABLE IF NOT EXISTS command_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation text,
    duration float,
    return_code INTEGER,
    stdout text,
    stderr text,
    created_at integer DEFAULT CURRENT_TIME
)
"""