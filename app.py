"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, jsonify, render_template, request, send_from_directory
import psycopg2
import os
import json
import collections
import datetime
from extractdata import *
app = Flask(__name__, static_folder='static')

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app
extractdata = extractdata()

@app.route('/popularity_data', methods=['GET'])
def popularity_data():

    popular = extractdata.getpopularitytable()

    #'normalize the table (adding 1 to the sum to return 0 when empty)
    sum_popular = sum(row[3] for row in popular)+1
    for k in range(0,len(popular)-1):
        popular[k][3] = popular[k][3]*10000/sum_popular

    resp = jsonify(data=popular, length = len(popular))

    return resp

@app.route('/newflights_data', methods=['GET'])
def airservice():

    newflights = extractdata.getnewflightstable()

    for k in range(0,len(newflights)-1):
        newflights[k][0] = newflights[k][1] + "-" + newflights[k][2]+ "\n" + " by " + newflights[k][3] + " on "+ newflights[k][4]

    resp = jsonify(data=newflights, length = len(newflights))

    return resp

@app.route('/pax', methods=['GET'])
def render_pax():
    #Renders the passenger chart page
        return render_template("pax.html", title="What are they searching for" )

@app.route('/airservice', methods=['GET'])
def render_service():
    #Renders the passenger chart page
        return render_template("airservice.html", title="What are they searching for" )

@app.route('/')
def hello():
    today_flag = datetime.date.today()

    return "today is " + str(today_flag) + "  => your installation works"

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


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 80.

    port = int(os.environ.get('PORT', 5000))
    if os.environ.get('ON_HEROKU'):
        app.run(host='0.0.0.0', port=port)
    else :
        app.run(host='localhost', port=port)
