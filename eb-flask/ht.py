"""
HTML rendering
"""

import db


def render_log_entry_html(duration, created_at, return_code, stdout, stderr):
    val = "<dt>At {}, duration {} sec; returned {}</dt><dd><dl><dt>STDOUT</dt><dd><code style='white-space: pre;'>{}</code></dd><dt>STDERR</dt><dd><code style='white-space: pre;'>{}</code></dd></dl></dd>"
    return val.format(
        created_at, duration, return_code, stdout, stderr)


header_text = '''<html>\n<head> <title>Git repo clone</title> </head>\n<body>'''


instructions = '''
    <h2>Actions</h2>
    <ul>
    <li><a href="/git-clone">Clone</a></li>
    <li><a href="/pr-fetch">Fetch</a></li>
    </ul>
    <h2>Queries</h2>
    <ul>
    <li>Ancestry
    <ul>
        <li><a href="/is-ancestor/657430e1f0aff3a234eb89ba2e5d16945a215791/e4f40bf3b23326d7bddd0f5017019d3c7dcc7567">false example</a></li>
        <li><a href="/is-ancestor/e4f40bf3b23326d7bddd0f5017019d3c7dcc7567/657430e1f0aff3a234eb89ba2e5d16945a215791">true example</a></li>
    </ul>
    </li>
    <li><a href="/pr-head-commit/27445">PR head commit</a> (should say <code>477b0c816b493b648a29c3fb53b19e7bef151e7d</code></li>
    <li><a href="/head-of-pull-requests/9533931b38ff814807f32cb79319f04bdce29f5e">Pointing PRs</a> (should say <code>28784</code></li>    
    <li><a href="/master-merge-base/f5d59f654ab1a8193fb40541cbd98eed86346b7d">Merge base with master</a> (should say <code>764e0ee88245c435be6934a5a06316c64ea171cc</code>)</li>
    <li><a href="commit-distance/764e0ee88245c435be6934a5a06316c64ea171cc/f5d59f654ab1a8193fb40541cbd98eed86346b7d">Commit distance</a> (should say <code>4</code>)</li>
    <li>Action logs
        <ul>
            <li><a href="/action-logs/clone">Clone logs</a></li>
            <li><a href="/action-logs/fetch">Fetch logs</a></li>
        </ul>
    </li>
    </ul>
    '''


home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'


def dump_command_logs(cmd):
    list_content = ""
    for x in db.get_operation_logs(cmd):
        list_content += render_log_entry_html(*x)

    return '''
    <html>\n<head> <title>Action logs</title> </head>\n<body>
    <h2>For <code>''' + cmd + '''</code></h2>

    <h2>Actions</h2>
    <dl>
    ''' + list_content + '''
    </dl>
    </body>
    </html>
    '''
