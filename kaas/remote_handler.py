#!/usr/bin/env python2.6

# Copyright 2013 Christopher Neugebauer and contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import keynote_script
import remote_json
import slideshow

import StringIO


#response, content_type, body = remote_handler.handle(self.path.split('/')[1:])

def handle(path, show, ws):

    command_type = path[0]

    try:
        return HANDLERS[command_type](path, show, ws)
    except KeyError:
        return (404, "text/plain", "No such URL: " + "/".join(path))



def handle_go(path, show, ws):
    return (404, "text/plain", "lol")


def handle_html(path, show, ws):

    if len(path) > 1:
        next = path[1].strip()
    else:
        next = ""

    if next == "start":
        show.start_slide_show()
    elif next == "next":
        show.next()

    elif next == "previous":
        show.previous()

    elif next == "sync":
        show.synchronise()

    build = show.current_build
    slide = show.current_slide

    ''' Display awful HTML template '''

    format_args = { 
        "image_url" : "/image/{}".format(build),
        "notes" : show.notes(slide)
    }
    output = HTML_TEMPLATE.format(**format_args).encode("utf8")

    return (200, "text/html; charset=utf-8", output)

def handle_json(path, show, ws):
    return remote_json.handle(path, show, ws)




def handle_image(path, show):

    build = int(path[1])
    filename = show.build_preview(build)

    output = open(filename).read()

    return (200, "image/jpeg", output)


def sanitise_notes(notes):
    io = StringIO.StringIO()
    for i in notes:
        if ord(i) < 128:
            io.write(i)
    return io.getvalue()

HANDLERS = {
    "go" : handle_go,
    "html" : handle_html,
    "image" : handle_image,
    "json" : handle_json,
}


HTML_TEMPLATE = '''
<html>
  <body>
      <h1>
        <a href="/html/start">Start</a> 
        - <a href="/html/next">Next</a> 
        - <a href="/html/previous">Previous</a> 
        - <a href="/html/sync">Sync</a>
      </h1>
    <img src="{image_url}" />
    <br/>
    <textarea rows="10" cols="160">
    {notes}
    </textarea>
  </body>

</html>
'''
HTML_TEMPLATE = unicode(HTML_TEMPLATE)
