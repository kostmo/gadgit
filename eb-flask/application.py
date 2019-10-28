#!/usr/bin/env python3

from flask import Flask, request
import json

import long_git_operations
import short_git_operations
import db
import ht


def cmd_logs_clear_operation():
    db.clear_command_logs()
    return "Cleared."


def parse_request(req):
    """
    Parses application/json request body data into a Python dictionary
    """
    payload = req.get_data()
    payload = json.loads(payload)

    return payload["ref"]


def generate_rules(app):
    app.add_url_rule('/', 'index', (lambda: ht.header_text + "<h2>Operational status</h2>" + long_git_operations.render_status() + ht.instructions + ht.footer_text))

    # Actions
    app.add_url_rule('/git-clone', 'hello1', long_git_operations.do_git_clone)
    app.add_url_rule('/pr-fetch', 'hello2', long_git_operations.do_pr_fetch)

    # Queries
    app.add_url_rule('/commit-distance/<base>/<branch>', 'hello3', short_git_operations.git_commit_distance)
    app.add_url_rule('/pr-head-commit/<pr>', 'hello4', short_git_operations.git_pull_request_head_commit)
    app.add_url_rule('/master-merge-base/<commit>', 'hello5', short_git_operations.git_master_merge_base)
    app.add_url_rule('/is-ancestor/<ancestor>/<descendent>', 'hello6', short_git_operations.query_ancestry)

    # Diagnostics
    app.add_url_rule('/action-logs/<cmd>', 'hello7', ht.dump_command_logs)

    app.add_url_rule('/clear-logs', 'hello8', cmd_logs_clear_operation)


# EB looks for an 'application' callable by default.
application = Flask(__name__)

generate_rules(application)


@application.route('/github-webhook-event', methods=['POST'])
def print_test():
    """
    Send a POST request to localhost:5000/api/print with a JSON body with a "p" key
    to print that message in the server console.
    """

    pushed_ref = parse_request(request)
    print("pushed ref:", pushed_ref)

    # This is idempotent; if there is already an ongoing fetch,
    # it will just return without doing anything.
    long_git_operations.do_pr_fetch()

    return "", 200, None


if __name__ == "__main__":

    db.initialize_db()

    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run(host="0.0.0.0", use_reloader=False)
