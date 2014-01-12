#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
app = Flask(__name__)

from flask import render_template, url_for, redirect
from flask import request
import os

if 'NAVODY_DEBUG' in os.environ:
  app.debug = True

from local_settings import active_config
config = active_config(app)
app.secret_key = config.secret

@app.route('/', methods=['POST', 'GET'])
def index():
  return render_template('index.html')

@app.route('/kategorizacia-publikacii')
def kategorizacia():
  return render_template('kategorizacia.html')

@app.route('/wos-a-scopus')
def wos_a_scopus():
  return render_template('wos-a-scopus.html')

if __name__ == '__main__':
  import sys

  if len(sys.argv) == 2 and sys.argv[1] == 'cherry':
    from cherrypy import wsgiserver
    d = wsgiserver.WSGIPathInfoDispatcher({'/': app})
    server = wsgiserver.CherryPyWSGIServer(('127.0.0.1', 5000), d)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
  else:
    app.run() # werkzeug