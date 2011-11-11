#!/usr/bin/env python

from brubeck.request_handling import Brubeck, WebMessageHandler
from brubeck.templating import load_jinja2_env, Jinja2Rendering
import sys
import datetime
import time
import json
import cgi

from gevent.event import Event

class DemoHandler(WebMessageHandler, Jinja2Rendering):
  def get(self):
    context = {
        'messages': json.dumps(buffer_array)
    }
    return self.render_template('base.html', **context)

class FeedHandler(WebMessageHandler):
  def post(self):
    message = self.get_argument('message')
    if (len(message) > 0):
      buffer_array.append(cgi.escape(message))
    if len(buffer_array) > 20:
      del buffer_array[0]
    self.set_body(json.dumps(buffer_array))
    new_message_event.set()
    new_message_event.clear()
    return self.render()

  def get(self):
    new_message_event.wait(10)
    self.set_body(json.dumps(buffer_array))
    return self.render()

config = {
    'mongrel2_pair': ('ipc://127.0.0.1:9999', 'ipc://127.0.0.1:9998'),
    'handler_tuples': [(r'^/$', DemoHandler),
      (r'^/feed', FeedHandler)],
    'template_loader': load_jinja2_env('./templates/chat'),
    }

new_message_event = Event()
buffer_array = ["Hi there! Welcome to barebones chat."]

app = Brubeck(**config)
app.run()
