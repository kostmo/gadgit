#!/usr/bin/env python3

"""
Short Git operations

Defines the structure of JSON responses for the web API
"""

import string

import git


def is_hex_string(s):
    return all(c in string.hexdigits for c in s)


def format_error(error_message):
    return {
        "status": "complete",
        "success": False,
        "error": error_message,
    }


def format_query_result(
        cmd_result,
        value_process_func=lambda x: x.stdout,
        success_process_func=lambda x: not x.return_code):

    succeeded = success_process_func(cmd_result)
    mydict = {
        "status": "complete",
        "success": succeeded,
    }

    if succeeded:
        mydict["result"] = value_process_func(cmd_result)
    else:
        mydict["error"] = cmd_result.stderr

    return mydict


def fetch_metadata_batch(commit_sha1_list):

    metadata_list = []

    failed_sha1s = []
    for i, commit_sha1 in enumerate(commit_sha1_list):
        print("Progress: %d/%d" % (i + 1, len(commit_sha1_list)))
        try:
            metadata_list.append(git.get_all_metadata_aspects(git.CLONE_PATH, commit_sha1))
        except:
            print("Skipping", commit_sha1)
            failed_sha1s.append(commit_sha1)

    return metadata_list


def git_pointing_prs(commit):
    """
    A bit slow; may take around 0.5 seconds
    """

    if not is_hex_string(commit):
        return format_error("commit {} is not a hexadecimal string".format(commit))

    cmd_result = git.current_pointing_prs(git.CLONE_PATH, commit)
    return format_query_result(cmd_result, lambda x: list(map(lambda x: int(x.split("/")[-2]), x.stdout.split())))


def parse_refs_with_individual_error_handling(refs):

    results = []
    for ref in refs:
        cmd_result = git.parse_bulk_refs(git.CLONE_PATH, [ref])
        formatted_result = format_query_result(cmd_result)

        entry_dict = {
            "ref": ref,
            "output": formatted_result,
        }
        results.append(entry_dict)

    return results


def git_commit_distance(base, branch):

    if not is_hex_string(base):
        return format_error("commit {} is not a hexadecimal string".format(base))

    if not is_hex_string(branch):
        return format_error("commit {} is not a hexadecimal string".format(branch))

    cmd_result = git.commit_distance(git.CLONE_PATH, base, branch)
    return format_query_result(cmd_result, lambda x: int(x.stdout))


def git_pull_request_head_commit(pr):
    cmd_result = git.pull_request_head_commit(git.CLONE_PATH, int(pr))
    return format_query_result(cmd_result)


def git_master_merge_base(commit):

    if not is_hex_string(commit):
        return format_error("commit {} is not a hexadecimal string".format(commit))

    cmd_result = git.master_merge_base(git.CLONE_PATH, commit)
    return format_query_result(cmd_result)


def single_rev_parse(ref):

    cmd_result = git.parse_bulk_refs(git.CLONE_PATH, [ref])
    return format_query_result(cmd_result)


def query_ancestry_html(ancestor, descendant):

    cmd_result = git.is_git_ancestor(git.CLONE_PATH, ancestor, descendant)

    # 0 or 1 are expected exit codes of --is-ancestor,
    # while other codes indicate a malfunction.
    if cmd_result.return_code == 0:
        return "<code>%s</code> <b style='color: green'>is an ancestor</b> of <code>%s</code>" % (ancestor, descendant)
    elif cmd_result.return_code == 1:
        return "<code>%s</code> <b style='color: red'>is <i>not</i> an ancestor</b> of <code>%s</code>" % (ancestor, descendant)
    else:
        return "ERROR: Problem determining if {} is ancestor of {}: <code>{}</code>".format(ancestor, descendant, cmd_result.stderr)


def query_ancestry_hexadecimal_only(ancestor, descendant):

    if not is_hex_string(ancestor):
        return format_error("ancestor commit {} is not a hexadecimal string".format(ancestor))

    if not is_hex_string(descendant):
        return format_error("descendant commit {} is not a hexadecimal string".format(descendant))

    return query_ancestry(ancestor, descendant)


def query_ancestry(ancestor, descendant):

    cmd_result = git.is_git_ancestor(git.CLONE_PATH, ancestor, descendant)

    def process_result(x):

        # 0 or 1 are expected exit codes of --is-ancestor,
        # while other codes indicate a malfunction.
        if x.return_code == 0:
            return True
        elif x.return_code == 1:
            return False
        else:
            return format_error("Problem determining if {} is ancestor of {}"
                               .format(ancestor, descendant))

    return format_query_result(cmd_result, process_result, lambda x: x.return_code in [0, 1])


if __name__ == "__main__":
    x = parse_refs_with_individual_error_handling(["master", "masters"])
    import json
    print(json.dumps(x))