"""
Long Git operations
"""

import threading
import os
import datetime
import contextlib
import subprocess
from multiprocessing.pool import ThreadPool

import db
import git


my_thread_pool = ThreadPool(1)

last_fetch_time = datetime.datetime.now() - datetime.timedelta(minutes=5)


class OperationInfo:
    def __init__(self):
        self.operation = None
        self.started_at = None
        self.is_ongoing = False
        self.mutating_operation_lock = threading.Lock()


# A singleton
current_operation_info = OperationInfo()


def render_status():
    if current_operation_info.is_ongoing:
        return "<p>Operation <code>{}</code> has been running since {}</p>".format(current_operation_info.operation, current_operation_info.started_at)
    else:
        return "<p>No operations ongoing.</p>"


def generic_git_op(operation, op_func, guard_func=None):
    """
    If the guard function exists and returns output, then
    the operation is skipped.
    """

    acquired = current_operation_info.mutating_operation_lock.acquire(blocking=False)
    if acquired:

        if guard_func:
            guard_output = guard_func()
            if guard_output:
                current_operation_info.mutating_operation_lock.release()
                return {"status": "skipped", "message": guard_output}

        def wrapped_func():

            try:
                clone_start_time = datetime.datetime.now()
                current_operation_info.operation = operation
                current_operation_info.started_at = clone_start_time
                current_operation_info.is_ongoing = True

                foo = op_func()

                clone_end_time = datetime.datetime.now()
                elapsed_seconds = (clone_end_time - clone_start_time).total_seconds()

                db.insert_operation_log(operation, elapsed_seconds, foo)

            except subprocess.CalledProcessError as e:
                exception_text = "Had a problem: " + str(e)
                print(exception_text)

            finally:
                current_operation_info.is_ongoing = False
                current_operation_info.mutating_operation_lock.release()

        my_thread_pool.apply_async(wrapped_func)
        return {"status": "started"}

    else:
        return {"status": "ongoing", "message": "Already working"}


def do_git_clone():

    def guard_func():
        if os.path.exists(git.CLONE_PATH):
            return "Clone already exists."

    return generic_git_op("clone", git.bare_clone, guard_func)


def do_pr_fetch():

    def guard_func():
        global last_fetch_time

        current_time = datetime.datetime.now()
        if (current_time - last_fetch_time).total_seconds() < 60:
            return "Will not fetch more than once per minute. Last fetch completed at {}".format(last_fetch_time)

    def operation_function():
        result = git.fetch_pr_refs()
        global last_fetch_time
        last_fetch_time = datetime.datetime.now()
        return result

    return generic_git_op("fetch", operation_function, guard_func)


def get_last_fetch_time():

    global last_fetch_time
    mydict = {
        "status": "complete",
        "success": True,
        "result": {
            "seconds_ago": (datetime.datetime.now() - last_fetch_time).total_seconds(),
            "timestamp": last_fetch_time,
        },
    }
    return mydict