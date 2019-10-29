"""
Short Git operations
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


def git_pointing_prs(commit):
    """
    May take around 0.5sec
    """

    if not is_hex_string(commit):
        return format_error("commit {} is not a hexadecimal string".format(commit))

    cmd_result = git.current_pointing_prs(git.CLONE_PATH, commit)
    return format_query_result(cmd_result, lambda x: list(map(lambda x: int(x.split("/")[-2]), x.stdout.split())))


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


def query_ancestry(ancestor, descendent):

    if not is_hex_string(ancestor):
        return format_error("ancestor commit {} is not a hexadecimal string".format(ancestor))

    if not is_hex_string(descendent):
        return format_error("descendent commit {} is not a hexadecimal string".format(descendent))

    cmd_result = git.is_git_ancestor(git.CLONE_PATH, ancestor, descendent)

    def process_result(x):

        # 0 or 1 are expected exit codes of --is-ancestor,
        # while other codes indicate a malfunction.
        if x.return_code == 0:
            return True
        elif x.return_code == 1:
            return False
        else:
            return format_error("Problem determining if {} is ancestor of {}"
                               .format(ancestor, descendent))

    return format_query_result(cmd_result, process_result, lambda x: x.return_code in [0, 1])