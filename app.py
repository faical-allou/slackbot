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
import sys
from extractdata import *
from neural import *
import gc
app = Flask(__name__, static_folder='static')

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app
extractdata = extractdata()
neural_network = neural_network()
@app.route('/popularity_data/<filtertype>/<city>', methods=['GET'])
def popularity_data(filtertype,city):

    popular = extractdata.getpopularitytable(filtertype,city)
    lastupdate = extractdata.getlasttimeupdate('ptbexits_popular')
    #normalize the table (adding 1 to the sum to return 0 when empty)
    max_popular = max(max(row[3] for row in popular),1)
    for k in range(0,len(popular)):
        popular[k][3] = round(popular[k][3]*100/max_popular)

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

@app.route('/itineraries_data/<fromcity>/<tocity>', methods=['GET'])
def itineraries_data(fromcity, tocity):
    itin = extractdata.getitintable(fromcity, tocity)

    lastupdate = extractdata.getlasttimeupdate('ptbexits_itineraries')
    #Converting to float and normalize the table (adding 1 to the sum to return 0 when empty)
    if len(itin) == 0:
        max_itin = 1
    else:
        max_itin = max(row[14] for row in itin)+1

    for k in range(0,len(itin)):
        itin[k][14] = max(itin[k][14]*3/max_itin,1)

    resp = jsonify(data=itin, update = lastupdate, length = len(itin))

    return resp

@app.route('/airport_data/<airport>', methods=['GET'])
def airport_data(airport):
    if len(airport) < 3: airport = 'xxx'
    airports = extractdata.getairporttable(airport)
    lastupdate = extractdata.getlasttimeupdate('ptbexits_airport')
    #Converting to float normalize the table (adding 1 to the sum to return 0 when empty)
    # and formatting for easy consumption by the chart
    # getting the list of airports to consider, the final table is based on airport
    transpose = list(zip(*airports))
    transposelist = list(transpose[0])
    transposelist1 = list(transpose[1])
    transposelist.extend(transposelist1)
    airport_list = list(set(transposelist))
    airport_list.remove('xxx')

    # getting size of the large table from the database to iterate on
    airport_size = len(airports)

    # initializing the hub table that wil be returned with first column as ID AIrport/timeofday
    # also building an index table to retrieve the right row to fill in when iterating later
    hub = [['id','ap','time',0,0,0,0]]
    hub_col0 = [0]

    for i in range(0,len(airport_list)):
        for j in range(0,24):
            hub.append([airport_list[i] + str(j).zfill(2), airport_list[i], str(j).zfill(2),0,0,0,0])
            hub_col0.append(airport_list[i] + str(j).zfill(2))

    # filling the hub table by iterating on the airport table
    for k in range(0,airport_size-1):

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

    peak_arrival = max(hub[k][3]+hub[k][5] for k in range (0, 24) )
    peak_departure = max(-hub[k][4]-hub[k][6] for k in range (0, 24) )
    peak_activity = max(peak_departure, peak_arrival)

    for k in range (0, 24):
        hub[k][3] = round(hub[k][3]*100 / peak_activity)
        hub[k][4] = round(hub[k][4]*100 / peak_activity)
        hub[k][5] = round(hub[k][5]*100 / peak_activity)
        hub[k][6] = round(hub[k][6]*100 / peak_activity)



    #calculating size of hub table for the json
    datasize = len(airports)
    resp = jsonify(data=hub, update = lastupdate, length = datasize)

    return resp

@app.route('/trending_data/<cityfrom>/<cityto>', methods=['GET'])
def trending_data(cityfrom, cityto):
        trend = extractdata.gettrendingtable(cityfrom, cityto)
        lastupdate = extractdata.getlasttimeupdate('ptbsearches_trending')

        lastupdate_date = datetime.datetime.strptime(lastupdate, '%Y-%m-%d')
        earliest_date = datetime.datetime.strptime('2014-02-02', '%Y-%m-%d')

        max_range_data = (lastupdate_date.year - earliest_date.year)*12 + (lastupdate_date.month - earliest_date.month) + 1

        resp = jsonify(data=trend, update = lastupdate, length = len(trend), max_length = max_range_data)

        return resp

@app.route('/neural_data/<in1>/<in2>/<in3>/<in4>/<in5>/<in6>/<out1>/<out2>/<out3>/<out4>/<out5>/<out6>', methods=['GET'])
def trainednetwork(in1,in2,in3,in4,in5,in6, out1,out2,out3,out4,out5,out6):

        neural = neural_network.trainneuralnetwork(in1,in2,in3,in4,in5,in6, out1,out2,out3,out4,out5,out6)
        lastupdate = extractdata.getlasttimeupdate('ptbexits_neural')
        resp = jsonify(syn0=neural[0], syn1=neural[1], normalizer=neural[2], end_result= neural[3],update = lastupdate, length = len(neural))


        return resp

@app.route('/neural_predict/<in1>/', methods=['GET', 'POST'])

def predict_od(in1):
        gc.collect()
        syn0received = request.form['syn0']
        syn1received = request.form['syn1']
        normalizer_received = request.form['normalizer']

        prediction = neural_network.predict(in1,syn0received,syn1received, normalizer_received)

        resp = jsonify(data=prediction,  length = 1)

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

@app.route('/trending_view', methods=['GET'])
def render_trends():
    #Renders the passenger chart page
        return render_template("trending_view.html", title="What are they searching for" )

@app.route('/neural_view', methods=['GET'])
def render_neuralnetwork():
    #Renders the passenger chart page
        return render_template("neural_view.html", title="What are they searching for" )

@app.route('/extract_view', methods=['GET'])
def render_extract():
    #Renders the passenger chart page
        return render_template("extract_view.html", title="What are they searching for" )

@app.route('/')
def render_home():
    return render_template("home.html", title="What are they searching for" )

@app.route('/home')
def render_homepage():
    return render_template("home.html", title="What are they searching for" )


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
