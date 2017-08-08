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
import math
from extractdata import *
from neural import *
from alexa import *
import gc
app = Flask(__name__, static_folder='static')

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app
app.config['JSON_AS_ASCII'] = False
extractdata = extractdata()
neural_network = neural_network()
alexa_skill = alexa_skill()

@app.route('/popularity_data/<filtertype>/<city>', methods=['GET'])
def popularity_data(filtertype,city):

    popular_redirects = extractdata.getpopularitytableredirects(filtertype,city)
    popular_searches = extractdata.getpopularitytablesearches(filtertype,city)

    lastupdate = extractdata.getlasttimeupdate('ptbexits_popular')
    resp = jsonify(dataredirects=popular_redirects,datasearches=popular_searches, update = lastupdate, length = len(popular_redirects))

    return resp

@app.route('/newflights_data', methods=['GET'])
def airservice():

    newflights = extractdata.getnewflightstable()
    lastupdate = extractdata.getlasttimeupdate('ptbexits_airservice')
    resp = jsonify(data=newflights, update = lastupdate, length = len(newflights))

    return resp

@app.route('/itineraries_data/<fromcity>/<tocity>', methods=['GET'])
def itineraries_data(fromcity, tocity):
    itin = extractdata.getitintable(fromcity, tocity)
    lastupdate = extractdata.getlasttimeupdate('ptbexits_itineraries')
    resp = jsonify(data=itin, update = lastupdate, length = len(itin))

    return resp

@app.route('/airport_data/<airport>', methods=['GET'])
def airport_data(airport):
    if len(airport) < 3: airport = 'xxx'
    airports = extractdata.getairporttable(airport)

    lastupdate = extractdata.getlasttimeupdate('ptbexits_airport')
    hub= airports[0]
    datasize = airports[1]
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
        resp = jsonify(syn0=neural[0], syn1=neural[1], normalizer=neural[2], end_result= neural[3],update = lastupdate, length = len(neural), validity = neural[4])

        return resp

@app.route('/neural_predict/<in1>/', methods=['GET', 'POST'])

def predict_od(in1):
        gc.collect()
        syn0received = request.form['syn0']
        syn1received = request.form['syn1']
        normalizer_received = request.form['normalizer']

        prediction = neural_network.predict(in1,syn0received,syn1received, normalizer_received)

        resp = jsonify(data=prediction[0], validity = prediction[1],  length = 1)

        return resp


@app.route('/catchment_data/<airport>/<rangekm>/<destinationcity>/<crossborder>', methods=['GET'])
def catchment_data(airport, rangekm, destinationcity,crossborder):
        lastupdate = extractdata.getlasttimeupdate('ptbexits_leakage')
        fullcatchment = extractdata.getfullcatchment(airport, rangekm, destinationcity,crossborder)
        resp = jsonify (catchment=fullcatchment[0], leakage=fullcatchment[2], airport_share = fullcatchment[3], airport_coord = fullcatchment[1], update = lastupdate, confidence = fullcatchment[4], length = [len(fullcatchment[0]), len(fullcatchment[2])])
        if fullcatchment[5] == 1 : resp = jsonify(catchment=0, leakage=0, airport_share = 0, airport_coord = 0, update = 0, confidence = 0, length = [0, 0])

        return resp

@app.route('/popularity_fastest_data/<city>', methods=['GET'])
def popularity_fastest_data(city):
    gc.collect()

    fastest = extractdata.getfastestgrowing(city)
    lastupdate = extractdata.getlasttimeupdate('ptbexits_popular')

    resp = jsonify(data=fastest, update = lastupdate, length=len(fastest))
    return resp

@app.route('/popularity_data_alexa/', methods=['GET', 'POST'])
def popularity_data_alexa():
    gc.collect()
    json_request = request.get_json(force=True, silent=False, cache=True)
    request_city = json_request['request']['intent']['slots']['origin']['value']
    print("resquest_city= ", request_city)
    popular = extractdata.getpopularitytablealexa('o',request_city)
    print(popular)

    resp = jsonify(alexa_skill.speak_populardestinations(popular))
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


@app.route('/extract_view', methods=['GET'])
def render_extract():
    #Renders the passenger chart page
        return render_template("extract_view.html", title="What are they searching for" )

@app.route('/catchment_view', methods=['GET'])
def render_catchment():
    #Renders the passenger chart page
        return render_template("catchment_view.html", title="What are they searching for" )

@app.route('/fastestgrowing_view', methods=['GET'])
def render_fastest():
    #Renders the passenger chart page
        return render_template("fastestgrowing_view.html", title="What are they searching for" )


@app.route('/')
def render_home():
    return render_template("_home.html", title="What are they searching for" )

@app.route('/home')
def render_homepage():
    return render_template("_home.html", title="What are they searching for" )

@app.route('/labs')
def render_labs():
    return render_template("x__labs.html", title="Artificial Intelligence" )

@app.route('/price_elasticity')
def render_price_elasticity():
    return render_template("x_price_elasticity.html", title="Price Elasticity" )

@app.route('/neural_view', methods=['GET'])
def render_neuralnetwork():
    #Renders the passenger chart page
        return render_template("x_neural_view.html", title="What are they searching for" )

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
