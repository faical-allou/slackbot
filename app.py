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
    lastupdate = extractdata.getlasttimeupdate('ptbexits_popular')
    #normalize the table (adding 1 to the sum to return 0 when empty)
    sum_popular = sum(row[3] for row in popular)+1
    for k in range(0,len(popular)-1):
        popular[k][3] = popular[k][3]*100000000/sum_popular

    resp = jsonify(data=popular, update = lastupdate, length = len(popular))

    return resp

@app.route('/newflights_data', methods=['GET'])
def airservice():

    newflights = extractdata.getnewflightstable()
    lastupdate = extractdata.getlasttimeupdate('ptbexits_airservice')
    # formatting the row label
    for k in range(0,len(newflights)-1):
        newflights[k][0] = newflights[k][1] + "-" + newflights[k][2]+ "\n" + " by " + newflights[k][3] + " on "+ newflights[k][4]

    resp = jsonify(data=newflights, update = lastupdate, length = len(newflights))

    return resp

@app.route('/itineraries_data', methods=['GET'])
def itineraries_data():

    itin = extractdata.getitintable()
    lastupdate = extractdata.getlasttimeupdate('ptbexits_itineraries')
    #Converting to float and normalize the table (adding 1 to the sum to return 0 when empty)
    max_itin = max(row[14] for row in itin)+1
    for k in range(0,len(itin)-1):
        itin[k][14] = max(itin[k][14]*100/max_itin,1)

    resp = jsonify(data=itin, update = lastupdate, length = len(itin))

    return resp

@app.route('/airport_data', methods=['GET'])
def airport_data():

    airports = extractdata.getairporttable()
    lastupdate = extractdata.getlasttimeupdate('ptbexits_airport')
    #Converting to float normalize the table (adding 1 to the sum to return 0 when empty)
    # and formatting for easy consumption by the chart
    # getting the list of airports to consider, the final table is based on airport
    transpose = list(zip(*airports))
    transposelist = list(transpose[0])
    transposelist1 = list(transpose[1])
    transposelist.extend(transposelist1)
    airport_list = list(set(transposelist))

    # getting size of the large table from the database to iterate on
    airport_size = len(airports)

    peak = max(row[4] for row in airports)+1

    # initializing the hub table that wil be returned with first column as ID AIrport/timeofday
    # also building an index table to retrieve the right row to fill in when iterating later
    hub = [['id','ap','time',0,0,0,0]]
    hub_col0 = [0]

    for i in range(0,len(airport_list)):
        for j in range(0,24):
            hub.append([airport_list[i] + str(j).zfill(2), airport_list[i], str(j).zfill(2),0,0,0,0])
            hub_col0.append(airport_list[i] + str(j).zfill(2))

    # filling the hub table by iterating on the airport table and normalizing as we go
    for k in range(0,airport_size-1):
        airports[k][4] = max(airports[k][4]*100000/peak,1)

        # hub table structure is ID/airport/timeofday/paxlocalarrival/paxlocaldeparture/paxconnectarrival/paxconnectdeparture
        # when it is a departure we switch one column to the left and we use negative number
        departureflag = 0

        if airports[k][0] == 'xxx' :
            airport_to_fill = airports[k][1]
        else:
            airport_to_fill = airports[k][0]
            airports[k][4] = -1*airports[k][4]
            departureflag = 1

        #reading from hub_col0 to find the row to fill in the hub table
        index0 = hub_col0.index(airport_to_fill + airports[k][2])

        if 'local' in airports[k][3]:
            hub[index0][3+departureflag] = hub[index0][3+departureflag] + float(airports[k][4])
        else: hub[index0][5+departureflag] = hub[index0][5+departureflag] + float(airports[k][4])

    # removing the first row (empty)
    hub.pop(0)

    #calculating size of hub table for the json
    datasize = len(hub)
    resp = jsonify(data=hub, update = lastupdate, length = datasize)

    return resp


@app.route('/popularity_view', methods=['GET'])
def render_pax():
    #Renders the passenger chart page
        return render_template("popularity_view.html", title="What are they searching for" )

@app.route('/newflights_view', methods=['GET'])
def render_service():
    #Renders the passenger chart page
        return render_template("newflights_view.html", title="What are they searching for" )

@app.route('/itineraries_view', methods=['GET'])
def render_itineraries():
    #Renders the passenger chart page
        return render_template("itineraries_view.html", title="What are they searching for" )

@app.route('/airport_view', methods=['GET'])
def render_airport():
    #Renders the passenger chart page
        return render_template("airport_view.html", title="What are they searching for" )

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
