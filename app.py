from flask import Flask, jsonify, render_template, request, send_from_directory
import psycopg2
import os
import json
import collections
import datetime
import sys
import math
import gc
from models.extractdata import *
from models.alexa import *

app = Flask(__name__, static_folder='static')

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app
app.config['JSON_AS_ASCII'] = False
extractdata = extractdata()

@app.route('/slackbot', methods=['GET', 'POST'])
def popularity_hotel_data_alexa():
    gc.collect()
    json_request = request.get_json(force=True, silent=False, cache=True)
    print(json_request)
    partner_id = request.form.get('text', None)
    popular = extractdata.getpartnername(partner_id)

    resp = jsonify(alexa_skill.speak_popularhotels(popular))
    return resp





@app.route('/')
def render_home():
    return "it works"



@app.route('/<path:filename>', methods=['GET'])
def display_static():
    return send_from_directory(app.static_folder, filename)

@app.route('/js/<path:filename>', methods=['GET'])
def load_js(filename):
    return send_from_directory('js', filename)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(404)
def pageNotFound(error):
    return render_template("500.html", title="Sorry!" )

@app.errorhandler(500)
def erroronpage(error):
    return render_template("500.html", title="Sorry!" )

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 80.
    port = int(os.environ.get('PORT', 5000))
    if os.environ.get('ON_HEROKU'):
        app.run(host='0.0.0.0', port=port)
    else :
        app.run(host='localhost', port=port)
