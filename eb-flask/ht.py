"""
HTML rendering
"""

import db


def render_log_entry_html(duration, content, created_at):
    return "<dt>At {}, duration {} sec</dt><dd><code>{}</code></dd>".format(
        created_at, duration, content.decode("utf-8"))


# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>Git repo clone</title> </head>\n<body>'''
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
    
    <li><a href="/master-merge-base/f5d59f654ab1a8193fb40541cbd98eed86346b7d">Merge base with master</a> (should say <code>764e0ee88245c435be6934a5a06316c64ea171cc</code>)</li>
    <li><a href="/pr-head-commit/27445">PR head commit</a> (should say <code>477b0c816b493b648a29c3fb53b19e7bef151e7d</code></li>
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
