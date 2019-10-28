"""
Short Git operations
"""

import string

import git


def format_query_result(value):
    return {"status": "complete", "result": value}


def git_commit_distance(base, branch):

    if not is_hex_string(base):
        return "commit {} is not a hexadecimal string".format(base)

    if not is_hex_string(branch):
        return "commit {} is not a hexadecimal string".format(branch)

    cmd_result = git.commit_distance(git.CLONE_PATH, base, branch)
    return format_query_result(int(cmd_result.stdout))


def git_pull_request_head_commit(pr):
    cmd_result = git.pull_request_head_commit(git.CLONE_PATH, int(pr))
    return format_query_result(cmd_result.stdout)


def git_master_merge_base(commit):

    if not is_hex_string(commit):
        return "commit {} is not a hexadecimal string".format(commit)

    cmd_result = git.master_merge_base(git.CLONE_PATH, commit)
    return format_query_result(cmd_result.stdout)


def is_hex_string(s):
    return all(c in string.hexdigits for c in s)


def query_ancestry(ancestor, descendent):

    if not is_hex_string(ancestor):
        return "ancestor commit {} is not a hexadecimal string".format(ancestor)

    if not is_hex_string(descendent):
        return "descendent commit {} is not a hexadecimal string".format(descendent)

    cmd_output_bool = git.is_git_ancestor(git.CLONE_PATH, ancestor, descendent)
    return format_query_result(cmd_output_bool)