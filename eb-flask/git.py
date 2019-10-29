"""
Git operations
"""

import os
import subprocess


GIT_BINARY_PATH = "git"
REPO_CLONE_URL = "https://github.com/pytorch/pytorch.git"


# In contrast with the "/opt/python/current/app" directory, in which the
# python application files are stored, the "/tmp" directory persists across
# application redeployments.  This persistence is desirable as a fresh
# fetch of all of the PR refs can take over 10 minutes.
CLONE_PATH = '/tmp/repo/pytorch.git'


class CommandResult:
    def __init__(self, return_code, stdout, stderr):
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr


def get_command_result(cmd_args):
    p = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return CommandResult(p.returncode, stdout.decode("utf-8").strip(), stderr.decode("utf-8").strip())


def fetch_pr_refs():
    git_objdir = CLONE_PATH

    cmd_args = [
        GIT_BINARY_PATH,
        '--git-dir', git_objdir,
        "fetch",
        "--force",
        "origin",
        "refs/pull/*:refs/remotes/origin/pr/*",
    ]

    return get_command_result(cmd_args)


def master_merge_base(git_objdir, branch_commit_sha1):

    cmd_args = [
        GIT_BINARY_PATH,
        '--git-dir',
        git_objdir,
        "merge-base",
        "master",
        branch_commit_sha1,
    ]

    return get_command_result(cmd_args)


def pull_request_head_commit(git_objdir, pr_number):

    cmd_args = [
        GIT_BINARY_PATH,
        '--git-dir',
        git_objdir,
        "rev-parse",
        "refs/remotes/origin/pr/%d/head" % (pr_number),
    ]
    return get_command_result(cmd_args)


def commit_distance(git_objdir, merge_base_sha1, branch_commit_sha1):

    cmd_args = [
        GIT_BINARY_PATH,
        '--git-dir',
        git_objdir,
        "rev-list",
        "--ancestry-path",
        "--count",
        merge_base_sha1 + ".." + branch_commit_sha1,
    ]

    return get_command_result(cmd_args)


def current_pointing_prs(git_objdir, commit_sha1):

    cmd_args = [
        GIT_BINARY_PATH,
        '--git-dir',
        git_objdir,
        "branch",
        "--all",
        "--list",
        "*/pr/*/head",
        "--points-at",
        commit_sha1,
    ]

    return get_command_result(cmd_args)


def bare_clone():
    os.makedirs(os.path.dirname(CLONE_PATH), mode=0o777, exist_ok=True)

    cmd_args = [
        GIT_BINARY_PATH,
        "clone",
        "--bare",
        "--single-branch",
        REPO_CLONE_URL,
        CLONE_PATH,
    ]

    return get_command_result(cmd_args)


def is_git_ancestor(git_objdir, supposed_ancestor, supposed_descendent):
    cmd_args = [
        GIT_BINARY_PATH,
        '--git-dir', git_objdir,
        'merge-base',
        '--is-ancestor',
        supposed_ancestor,
        supposed_descendent,
    ]

    return get_command_result(cmd_args)

