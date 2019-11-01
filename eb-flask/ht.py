"""
HTML rendering
"""

import os
import arrow

import db


STATIC_FILES_DIR = os.path.join(os.path.dirname(__file__), 'static')

header_text = '''
<html>
<head><title>Git repo clone</title></head>
<body>
'''


def get_instructions():
    with open(os.path.join(STATIC_FILES_DIR, "index.partial.html")) as fh:
        return fh.read()


home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '''<hr/><i>by <a href="https://github.com/kostmo" rel="author">kostmo</a></i>
<span style="float: right">See <a href="https://github.com/kostmo/gadgit/blob/master/README.md">project README</a> for details.</span>
</body>\n</html>'''


def render_log_entry_html(duration, created_at, return_code, stdout, stderr):
    val = "<dt>%s, duration %.1f sec; returned <code>%d</code></dt><dd><dl><dt>STDOUT</dt><dd><code style='white-space: pre;'>%s</code></dd><dt>STDERR</dt><dd><code style='white-space: pre;'>%s</code></dd></dl></dd>"
    return val % (
        arrow.get(created_at).humanize(), duration, return_code, stdout, stderr)


def dump_command_logs(cmd):
    list_content = ""
    for x in db.get_operation_logs(cmd):
        list_content += render_log_entry_html(*x)

    return '''
    <html>\n<head> <title>Action logs</title> </head>\n<body>
    <h2>For <code>''' + cmd + '''</code></h2>

    <dl>
    ''' + list_content + '''
    </dl>
    </body>
    </html>
    '''


def render_github_event_entry_html(id, event, received_at):
    val = "<li>row %d %s: <code>%s</code></li>"
    return val % (id, received_at, event)


def dump_github_event_logs():
    list_content = ""
    for x in db.get_github_event_logs():
        list_content += render_github_event_entry_html(*x)

    return '''
    <html>\n<head> <title>Github event logs</title> </head>\n<body>
    <h2>Github event logs</h2>

    <ul>
    ''' + list_content + '''
    </ul>
    </body>
    </html>
    '''
