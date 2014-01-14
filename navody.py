#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
app = Flask(__name__)

from flask import render_template, url_for, redirect
from flask import request
import os
import psycopg2
from contextlib import closing
import stdnum.issn

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

@app.route('/impakt-faktor/')
def impakt_faktor():
  if request.remote_user:
    return redirect(url_for('impakt_faktor_moje'))
  return redirect(url_for('impakt_faktor_fmfi'))

@app.route('/impakt-faktor/vsetky')
def impakt_faktor_vsetky():
  def query(cursor):
    cursor.execute('SELECT DISTINCT id, source_title, source_abbr, snip_2012, if_2013, issn FROM impact_factors, impact_factors_issn WHERE id = impact_factors_id AND (snip_2012 IS NOT NULL OR if_2013 IS NOT NULL) ORDER BY source_title, id, issn')
  return show_impakt_faktor(query, tab='vsetky')

@app.route('/impakt-faktor/fmfi')
def impakt_faktor_fmfi():
  def query(cursor):
    cursor.execute('SELECT DISTINCT id, source_title, source_abbr, snip_2012, if_2013, impact_factors_issn.issn FROM impact_factors, impact_factors_issn, issn_login WHERE id = impact_factors_id AND (snip_2012 IS NOT NULL OR if_2013 IS NOT NULL) AND issn_login.issn = impact_factors_issn.issn ORDER BY source_title, id, issn')
  return show_impakt_faktor(query, tab='fmfi')

@app.route('/impakt-faktor/moje')
def impakt_faktor_moje():
  user = request.remote_user
  def query(cursor):
    cursor.execute('SELECT DISTINCT id, source_title, source_abbr, snip_2012, if_2013, impact_factors_issn.issn FROM impact_factors, impact_factors_issn, issn_login WHERE id = impact_factors_id AND (snip_2012 IS NOT NULL OR if_2013 IS NOT NULL) AND issn_login.issn = impact_factors_issn.issn  AND issn_login.login = %s ORDER BY source_title, id, issn', (user,))
  return show_impakt_faktor(query, tab='moje')

def show_impakt_faktor(run_query, **kwargs):
  data = []
  with closing(psycopg2.connect(config.conn_str)) as conn:
    with closing(conn.cursor()) as cursor:
      psycopg2.extensions.register_type(psycopg2.extensions.UNICODE, cursor) # unicode support
      run_query(cursor)
      lastid = None
      issns = []
      for id, source_title, source_abbr, snip_2012, if_2013, issn in cursor:
        if lastid != id:
          data.append((id, source_title, source_abbr, snip_2012, if_2013, [stdnum.issn.format(issn)]))
          lastid = id
        else:
          data[-1][5].append(stdnum.issn.format(issn))
  return render_template('impakt-faktor.html', data=data, **kwargs)

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