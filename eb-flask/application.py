#!/usr/bin/env python3

from flask import Flask

import long_git_operations
import short_git_operations
import db
import ht


def generate_rules(app):
    app.add_url_rule('/', 'index', (lambda: ht.header_text + ht.instructions + ht.footer_text))

    # Actions
    app.add_url_rule('/git-clone', 'hello1', long_git_operations.do_git_clone)
    app.add_url_rule('/pr-fetch', 'hello2', long_git_operations.do_pr_fetch)

    # Queries
    app.add_url_rule('/commit-distance/<base>/<branch>', 'hello3', short_git_operations.git_commit_distance)
    app.add_url_rule('/pr-head-commit/<pr>', 'hello4', short_git_operations.git_pull_request_head_commit)
    app.add_url_rule('/master-merge-base/<commit>', 'hello5', short_git_operations.git_master_merge_base)
    app.add_url_rule('/is-ancestor/<ancestor>/<descendent>', 'hello7', short_git_operations.query_ancestry)

    # Diagnostics
    app.add_url_rule('/action-logs/<cmd>', 'hello6', ht.dump_command_logs)


# EB looks for an 'application' callable by default.
application = Flask(__name__)

generate_rules(application)


if __name__ == "__main__":

    db.initialize_db()

    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run(host="0.0.0.0", use_reloader=False)
