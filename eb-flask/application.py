#!/usr/bin/env python3

from flask import Flask, request, abort, send_from_directory
import json
import hmac
import os

import long_git_operations
import short_git_operations
import db
import ht
import git


def cmd_logs_clear_operation():
    db.clear_command_logs()
    return "Cleared."


def generate_rules(app):
    app.add_url_rule('/', 'index', (lambda: ht.header_text + "<h2>Operational status</h2>" + long_git_operations.render_status() + ht.get_instructions() + ht.footer_text))

    # Actions
    app.add_url_rule('/git-clone', 'action1', long_git_operations.do_git_clone)
    app.add_url_rule('/pr-fetch', 'action2', long_git_operations.do_pr_fetch)
    app.add_url_rule('/restore-head', 'action3', git.restore_head_ref)

    # Queries
    app.add_url_rule('/commit-distance/<base>/<branch>', 'query1', short_git_operations.git_commit_distance)
    app.add_url_rule('/pr-head-commit/<pr>', 'query2', short_git_operations.git_pull_request_head_commit)
    app.add_url_rule('/master-merge-base/<commit>', 'query3', short_git_operations.git_master_merge_base)
    app.add_url_rule('/head-of-pull-requests/<commit>', 'query4', short_git_operations.git_pointing_prs)
    app.add_url_rule('/is-ancestor/<ancestor>/<descendant>', 'query5', short_git_operations.query_ancestry_hexadecimal_only)
    app.add_url_rule('/rev-parse/<ref>', 'query6', short_git_operations.single_rev_parse)

    # Diagnostics
    app.add_url_rule('/action-logs/<cmd>', 'diag1', ht.dump_command_logs)
    app.add_url_rule('/github-event-logs', 'diag2', ht.dump_github_event_logs)
    app.add_url_rule('/clear-logs', 'diag3', cmd_logs_clear_operation)
    app.add_url_rule('/last-fetch-time', 'diag4', long_git_operations.get_last_fetch_time)


# EB looks for an 'application' callable by default.
application = Flask(__name__)

generate_rules(application)


def event_should_trigger_fetch(event_type, payload, event_record_id):
    if event_type == "push":
        pushed_ref = payload["ref"]
        print("pushed ref:", pushed_ref)
        return True

    elif event_type == "pull_request":

        pr_action = payload["action"]
        pr_number = payload["number"]
        print("Pull request event details :: action:", pr_action, "; number:", pr_number)

        if pr_action in ["opened", "edited", "reopened", "synchronize"]:
            return True

    return False


def enforce_signature(req):

    secret = os.environ.get('GITHUB_WEBHOOK_SECRET')
    if secret:
        header_signature = req.headers.get('X-Hub-Signature')
        if header_signature is None:
            abort(403)

        sha_name, signature = header_signature.split('=')
        if sha_name != 'sha1':
            abort(501)

        mac = hmac.new(secret.encode('utf-8'), msg=req.data, digestmod='sha1')
        if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
            abort(403)


@application.route('/rev-parse-query', methods=['GET'])
def rev_parse_query_handler():

    ref = request.args.get('ref')
    return short_git_operations.single_rev_parse(ref)


@application.route('/is-ancestor-html', methods=['GET'])
def ancestor_query_html_handler():

    ancestor_ref = request.args.get('ancestor')
    descendant_ref = request.args.get('descendant')

    return short_git_operations.query_ancestry_html(ancestor_ref, descendant_ref)


@application.route('/api/is-ancestor', methods=['GET'])
def ancestor_query_handler():

    ancestor_ref = request.args.get('ancestor')
    descendant_ref = request.args.get('descendant')

    return short_git_operations.query_ancestry(ancestor_ref, descendant_ref)


@application.route('/github-webhook-event', methods=['POST'])
def webhook_handler():

    # Aborts this function early if signature does not match.
    enforce_signature(request)

    event_type = request.headers['X-GitHub-Event']

    event_record_id = db.insert_event(event_type)
    # print("Inserted %s event with row ID %d" % (event_type, event_record_id))

    payload = json.loads(request.get_data())

    should_fetch = event_should_trigger_fetch(event_type, payload, event_record_id)
    print("Should fetch?", should_fetch)
    if should_fetch:
        # This is idempotent; if there is already an ongoing fetch,
        # it will just return without doing anything.

        print("About to re-fetch...")
        response_dict = long_git_operations.do_pr_fetch()
        print("Finished re-fetch with response:", response_dict)

    return "", 200, None


@application.route('/commit-metadata', methods=['POST'])
def handle_batch_commit_metadata_request():

    payload = json.loads(request.get_data())
    metadata_list = short_git_operations.fetch_metadata_batch(payload)

    # TODO: Error handling
    mydict = {
        "status": "complete",
        "success": True,
        "result": metadata_list,
    }
    return mydict


@application.route('/bulk-rev-parse', methods=['POST'])
def handle_batch_rev_parse_request():
    """
    To test:

    curl --data '["0c7537c~", "0c7537c~2"]' http://localhost:5000/bulk-rev-parse
    """

    refs = json.loads(request.get_data())
    cmd_result = git.parse_bulk_refs(git.CLONE_PATH, refs)

    def value_process_func(result):
        ref_associations = []

        for ref, commit_sha1 in zip(refs, result.stdout.splitlines()):
            mydict = {
                "ref": ref,
                "commit_sha1": commit_sha1,
            }

            ref_associations.append(mydict)

        return ref_associations

    return short_git_operations.format_query_result(cmd_result, value_process_func)


# Has individual error handling on each PR
@application.route('/bulk-pull-request-heads', methods=['POST'])
def handle_batch_pull_request_heads_request():
    """
    To test:

    curl --data '[22201, 23463, 9999999]' http://localhost:5000/bulk-pull-request-heads
    """

    pr_numbers = json.loads(request.get_data())

    results = []
    for pr_number in pr_numbers:
        ref = git.PR_REF_TEMPLATE % pr_number
        cmd_result = git.parse_bulk_refs(git.CLONE_PATH, [ref])
        formatted_result = short_git_operations.format_query_result(cmd_result)

        entry_dict = {
            "pr_number": pr_number,
            "output": formatted_result,
        }
        results.append(entry_dict)

    mydict = {
        "status": "complete",
        "success": True,
        "result": results,
    }

    return mydict


# No individual error handling on each ref
@application.route('/bulk-pull-request-heads-simple', methods=['POST'])
def handle_batch_pull_request_heads_simple_request():
    """
    To test:

    curl --data '[22201, 23463]' http://localhost:5000/bulk-pull-request-heads
    """

    pr_numbers = json.loads(request.get_data())
    pr_refs = list(map(lambda x: git.PR_REF_TEMPLATE % x, pr_numbers))

    cmd_result = git.parse_bulk_refs(git.CLONE_PATH, pr_refs)

    def value_process_func(result):

        pr_head_associations = []

        for pr_number, head_commit in zip(pr_numbers, result.stdout.splitlines()):
            mydict = {
                "pr_number": pr_number,
                "head_commit": head_commit,
            }

            pr_head_associations.append(mydict)

        return pr_head_associations

    return short_git_operations.format_query_result(cmd_result, value_process_func)


@application.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(application.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == "__main__":

    db.initialize_db()

    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
#    application.debug = True
    application.run(host="0.0.0.0", use_reloader=False)
