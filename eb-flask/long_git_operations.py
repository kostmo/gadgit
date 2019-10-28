"""
Long Git operations
"""

import threading
import os
import datetime
import contextlib
import subprocess

import db
import git


operation_locks = {}


@contextlib.contextmanager
def non_blocking_lock(lock=threading.Lock()):
    try:
        yield lock.acquire(blocking=False)
    finally:
        lock.release()


def generic_git_op(operation, op_func, guard_func=None):
    """
    If the guard function exists and returns output, then
    the operation is skipped.
    """

    operation_lock = operation_locks.setdefault(operation, threading.Lock())
    with non_blocking_lock(operation_lock) as did_acquire:

        if did_acquire:

            if guard_func:

                guard_output = guard_func()

                if guard_output:
                    return guard_output

            try:
                clone_start_time = datetime.datetime.now()

                foo = op_func()

                clone_end_time = datetime.datetime.now()
                elapsed_seconds = (clone_end_time - clone_start_time).total_seconds()

                db.insert_operation_log(operation, elapsed_seconds, foo)
                return {"status": "complete", "result": foo}

            except subprocess.CalledProcessError as e:
                exception_text = "Had a problem: " + str(e)
                print(exception_text)
                return {"status": "failed", "message": exception_text}

        else:
            return {"status": "ongoing", "message": "Already working"}


def do_git_clone():

    def guard_func():
        if os.path.exists(git.CLONE_PATH):
            return "Clone already exists."

    return generic_git_op("clone", git.bare_clone, guard_func)


def do_pr_fetch():
    return generic_git_op("fetch", git.fetch_pr_refs)

