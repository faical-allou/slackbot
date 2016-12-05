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
app = Flask(__name__, static_folder='static')

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

def getconnection():

    #Define our connection string to localhost
    #conn_string = "host='localhost' port='5432' dbname='postgres' user='postgres' password='satf..'"
    #Define our connection string to heroku basic database
    conn_string = "host='ec2-54-235-125-135.compute-1.amazonaws.com' port='5432' dbname='d4sjjjfm3g35dc' user='swobzoejynjhpk' password='aJS-yO6EBUg6DgzVQSFwp3Ac1v'"
    #Connection string to redshift
    #conn_string = "host='travelinsights-redshiftcluster-1vmmqnro7byz7.cbkwytfo7n8s.eu-west-1.redshift.amazonaws.com' port='5439' dbname='b2baggrarch' user='awsuser' password='asnou32mvdoQEsd!!24fgs6yhuU'"
 	#connect
    try:
        conn = psycopg2.connect(conn_string)
    except psycopg2.Error as e:
        print ("Unable to connect!")
        print (e.pgerror)
        print (e.diag.message_detail)
    else:
        print ("Connected!")

    return conn

def getpopularitytable():

    connection = getconnection()
    cursor = connection.cursor()

    query = "SELECT origincitycode, destinationcitycode, concat(origincitycode, '-',destinationcitycode), seats FROM ptbexits_popular \
    WHERE origincitycode > 'AAA' and destinationcitycode > 'AAA' ORDER BY seats DESC LIMIT 10000"
    cursor.execute(query)

    rows = [('a','b','c', 1)]
    rowarray_list = []

    while len(rows) > 0:

        rows = cursor.fetchmany(500)
        # Convert query to row arrays
        for row in rows:
            rows_to_convert = (row[0], row[1], row[2], row[3])
            t = list(rows_to_convert)
            rowarray_list.append(t)

    j = json.dumps(rowarray_list)

    connection.close()
    return rowarray_list


@app.route('/popularity_data', methods=['GET'])
def popularity_data():

    popular = getpopularitytable()

    #'normalize the table (adding 1 to the sum to return 0 when empty)
    sum_popular = sum(row[3] for row in popular)+1
    for k in range(0,len(popular)-1):
        popular[k][3] = popular[k][3]*10000/sum_popular

    resp = jsonify(data=popular, length = len(popular))

    return resp

def getnewflightstable():

    connection = getconnection()
    cursor = connection.cursor()

    query = "SELECT concat(originairport, destinationairport,  carriercode, weekday_mon_1), originairport, destinationairport,  carriercode, weekday_mon_1, to_char(first_exit, 'YYYY-MM-DD'), to_char(first_flight, 'YYYY-MM-DD') FROM ptbexits_airservice \
    ORDER BY first_exit DESC LIMIT 10000"
    cursor.execute(query)

    rows = [('a','b','c', 'd', 'e', 'f', 'g')]
    rowarray_list = []

    while len(rows) > 0:

        rows = cursor.fetchmany(500)
        # Convert query to row arrays
        for row in rows:
            rows_to_convert = (row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            t = list(rows_to_convert)
            rowarray_list.append(t)

    j = json.dumps(rowarray_list)

    connection.close()
    return rowarray_list

@app.route('/newflights_data', methods=['GET'])
def airservice():

    newflights = getnewflightstable()

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
