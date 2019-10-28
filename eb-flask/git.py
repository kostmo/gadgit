"""
Git operations
"""

import os
import subprocess


GIT_BINARY_PATH = "/usr/bin/git"
REPO_CLONE_URL = "https://github.com/pytorch/pytorch.git",

CLONE_PATH = os.path.expanduser("~/repo/pytorch.git")


def fetch_pr_refs():
    git_objdir = CLONE_PATH
    foo = subprocess.check_output([
        GIT_BINARY_PATH,
        '--git-dir', git_objdir,
        "fetch",
        "--force",
        "origin",
        "refs/pull/*:refs/remotes/origin/pr/*",
    ])
    return foo


def master_merge_base(git_objdir, branch_commit_sha1):

    foo = subprocess.check_output([
        GIT_BINARY_PATH,
        '--git-dir',
        git_objdir,
        "merge-base",
        "master",
        branch_commit_sha1,
    ])
    return foo.decode("utf-8").strip()


def pull_request_head_commit(git_objdir, pr_number):

    foo = subprocess.check_output([
        GIT_BINARY_PATH,
        '--git-dir',
        git_objdir,
        "rev-parse",
        "refs/remotes/origin/pr/%d/head" % (pr_number),
    ])
    return foo


def commit_distance(git_objdir, merge_base_sha1, branch_commit_sha1):

    foo = subprocess.check_output([
        GIT_BINARY_PATH,
        '--git-dir',
        git_objdir,
        "rev-list",
        "--ancestry-path",
        "--count",
        merge_base_sha1 + ".." + branch_commit_sha1,
    ])
    return int(foo.decode("utf-8").strip())


def bare_clone():
    os.makedirs(os.path.dirname(CLONE_PATH), mode=0o777, exist_ok=True)

    foo = subprocess.check_output([
        GIT_BINARY_PATH,
        "clone",
        "--bare",
        REPO_CLONE_URL,
        CLONE_PATH,
    ])

    return foo


def is_git_ancestor(git_objdir, supposed_ancestor, supposed_descendent) -> bool:
    cmd_args = [
        GIT_BINARY_PATH,
        '--git-dir', git_objdir,
        'merge-base',
        '--is-ancestor',
        supposed_ancestor, supposed_descendent]

    # 0 or 1 are expected exit codes of --is-ancestor,
    # while other codes indicate a malfunction.
    return_code = subprocess.call(cmd_args)
    if return_code == 0:
        return True
    elif return_code == 1:
        return False
    else:
        raise RuntimeError("Problem determining if {} is ancestor of {}"
            .format(supposed_ancestor, supposed_descendent))
