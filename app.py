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

def getpopularitytable():

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
        cursor = conn.cursor()
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

    conn.close()
    return rowarray_list


@app.route('/popularity', methods=['GET'])
def popularity():

    popular = getpopularitytable()

    #'normalize the table (adding 1 to the sum to return 0 when empty)
    sum_popular = sum(row[3] for row in popular)+1
    for k in range(0,len(popular)-1):
        popular[k][3] = popular[k][3]*10000/sum_popular

    resp = jsonify(data=popular, length = len(popular))

    return resp


@app.route('/traveltrends', methods=['GET'])
def render_page():
    #Renders the chart page
        return render_template("charts.html", title="Here's how busy the city/beach is" )


@app.route('/')
def hello():
    today_flag = datetime.date.today()

    return "today is " + str(today_flag)

@app.route('/<path:filename>', methods=['GET'])
def display_static():
    return send_from_directory(app.static_folder, filename)

@app.route('/js/<path:filename>', methods=['GET'])
def load_js(filename):
    return send_from_directory('js', filename)



if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 80.

    port = int(os.environ.get('PORT', 5000))
    if os.environ.get('ON_HEROKU'):
        app.run(host='0.0.0.0', port=port)
    else :
        app.run(host='localhost', port=port)
