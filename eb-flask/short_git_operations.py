"""
Short Git operations
"""

import string

import git


def is_hex_string(s):
    return all(c in string.hexdigits for c in s)


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


def git_commit_distance(base, branch):

    if not is_hex_string(base):
        return "commit {} is not a hexadecimal string".format(base)

    if not is_hex_string(branch):
        return "commit {} is not a hexadecimal string".format(branch)

    cmd_result = git.commit_distance(git.CLONE_PATH, base, branch)
    return format_query_result(cmd_result, lambda x: int(x.stdout))


def git_pull_request_head_commit(pr):
    cmd_result = git.pull_request_head_commit(git.CLONE_PATH, int(pr))
    return format_query_result(cmd_result)


def git_master_merge_base(commit):

    if not is_hex_string(commit):
        return "commit {} is not a hexadecimal string".format(commit)

    cmd_result = git.master_merge_base(git.CLONE_PATH, commit)
    return format_query_result(cmd_result)


def query_ancestry(ancestor, descendent):

    if not is_hex_string(ancestor):
        return "ancestor commit {} is not a hexadecimal string".format(ancestor)

    if not is_hex_string(descendent):
        return "descendent commit {} is not a hexadecimal string".format(descendent)

    cmd_result = git.is_git_ancestor(git.CLONE_PATH, ancestor, descendent)

    def process_result(x):

        # 0 or 1 are expected exit codes of --is-ancestor,
        # while other codes indicate a malfunction.
        if x.return_code == 0:
            print("Got here A")
            return True
        elif x.return_code == 1:
            print("Got here B")
            return False
        else:
            print("Got here C")
            raise RuntimeError("Problem determining if {} is ancestor of {}"
                               .format(ancestor, descendent))

    return format_query_result(cmd_result, process_result, lambda x: x.return_code in [0, 1])