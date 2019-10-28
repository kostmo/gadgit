#!/usr/bin/env python3

from flask import Flask
import threading
import os
import datetime
import contextlib
import string

import db
import ht
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

    :param operation:
    :param op_func:
    :param guard_func:
    :return:
    """
    operation_lock = operation_locks.setdefault(operation, threading.Lock())

    with non_blocking_lock(operation_lock) as did_acquire:
        if did_acquire:

            clone_start_time = datetime.datetime.now()

            if guard_func:
                guard_output = guard_func()
                if guard_output:
                    return guard_output

            else:
                try:
                    foo = op_func()

                    clone_end_time = datetime.datetime.now()
                    elapsed_seconds = (clone_end_time - clone_start_time).total_seconds()

                    db.insert_operation_log(operation, elapsed_seconds, foo)
                    return foo

                except Exception as e:
                    exception_text = "Had a problem: " + str(e)
                    print(exception_text)
                    return exception_text

        else:
            return "Already working..."


def do_git_clone():
    def guard_func():
        if os.path.exists(git.CLONE_PATH):
            return "Clone already exists."

    return generic_git_op("clone", git.bare_clone, guard_func)


def do_pr_fetch():
    return generic_git_op("fetch", git.fetch_pr_refs)


# EB looks for an 'application' callable by default.
application = Flask(__name__)

application.add_url_rule('/', 'index', (lambda: ht.header_text +
    ht.instructions + ht.footer_text))

application.add_url_rule('/git-clone', 'hello2', do_git_clone)

application.add_url_rule('/pr-fetch', 'hello22', do_pr_fetch)


def git_commit_distance(base, branch):

    if not is_hex_string(base):
        return "commit {} is not a hexadecimal string".format(base)

    if not is_hex_string(branch):
        return "commit {} is not a hexadecimal string".format(branch)

    return str(git.commit_distance(git.CLONE_PATH, base, branch))


application.add_url_rule('/commit-distance/<base>/<branch>', 'hello2222', git_commit_distance)


def git_pull_request_head_commit(pr):
    return git.pull_request_head_commit(git.CLONE_PATH, int(pr))


application.add_url_rule('/pr-head-commit/<pr>', 'hello22222', git_pull_request_head_commit)


def git_master_merge_base(commit):

    if not is_hex_string(commit):
        return "commit {} is not a hexadecimal string".format(commit)

    return git.master_merge_base(git.CLONE_PATH, commit)


application.add_url_rule('/master-merge-base/<commit>', 'hello222', git_master_merge_base)


application.add_url_rule('/action-logs/<cmd>', 'hello3', ht.dump_command_logs)


def is_hex_string(s):
    return all(c in string.hexdigits for c in s)


def query_ancestry(ancestor, descendent):

    if not is_hex_string(ancestor):
        return "ancestor commit {} is not a hexadecimal string".format(ancestor)

    if not is_hex_string(descendent):
        return "descendent commit {} is not a hexadecimal string".format(descendent)

    return str(git.is_git_ancestor(git.CLONE_PATH, ancestor, descendent))


application.add_url_rule('/is-ancestor/<ancestor>/<descendent>', 'hello4', query_ancestry)


# run the app.
if __name__ == "__main__":

    db.initialize_db()

    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run(host="0.0.0.0", use_reloader=False)
