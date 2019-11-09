#!/usr/bin/env python3

"""
Git operations
"""

import os
import subprocess


GIT_BINARY_PATH = "git"


# In contrast with the "/opt/python/current/app" directory in which the
# python application files are stored, the "/tmp" directory persists across
# application redeployments.  This persistence is desirable as a fresh
# fetch of all of the pytorch PR refs can take over 10 minutes.
CLONE_PATH = '/tmp/repo/pytorch.git'


PULL_REQUEST_REF_MAPPING = "refs/pull/*:refs/remotes/origin/pr/*"

PR_REF_TEMPLATE = "refs/remotes/origin/pr/%d/head"


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
        PULL_REQUEST_REF_MAPPING,
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


def parse_bulk_refs(git_objdir, refs):

    cmd_args = [
        GIT_BINARY_PATH,
        '--git-dir',
        git_objdir,
        "rev-parse",
    ] + refs

    return get_command_result(cmd_args)


def pull_request_head_commit(git_objdir, pr_number):
    return parse_bulk_refs(git_objdir, [PR_REF_TEMPLATE % pr_number])


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
        "*/pr/*/head",  # See PULL_REQUEST_REF_MAPPING
        "--points-at",
        commit_sha1,
    ]

    return get_command_result(cmd_args)


def bare_clone(repo_clone_url):
    os.makedirs(os.path.dirname(CLONE_PATH), mode=0o777, exist_ok=True)

    cmd_args = [
        GIT_BINARY_PATH,
        "clone",
        "--bare",
        "--single-branch",
        repo_clone_url,
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


def get_metadata_aspect(git_objdir, commit_sha1, format_specifier):

    cmd_args = [
        GIT_BINARY_PATH,
        '--git-dir', git_objdir,
        'log',
        '--format=' + format_specifier,
        '-n', '1',
        commit_sha1,
    ]

    return get_command_result(cmd_args)


KEYS_AND_FORMAT_SPECIFIERS = {
    "message": "%B",
    "sha1": "%H",
    "subject": "%f",
    "tree_sha1": "%T",
    "author_name": "%an",
    "author_email": "%aE",
    "author_date": "%ai",
    "committer_name": "%cN",
    "committer_email": "%cE",
    "committer_date": "%ci",
}


def get_all_metadata_aspects(git_objdir, commit_sha1):

    newdict = {}
    for k, v in KEYS_AND_FORMAT_SPECIFIERS.items():
        cmd_results = get_metadata_aspect(git_objdir, commit_sha1, v)
        newdict[k] = cmd_results.stdout

    return newdict


if __name__ == "__main__":
    # Test rev-parse

    parse_bulk_refs(CLONE_PATH, ["master", "add_xla_cpp_test", "boolPrint"])