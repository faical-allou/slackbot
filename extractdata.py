import psycopg2
import simplejson
import collections
import datetime

class extractdata:
    def getconnection(self):

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


    def getlasttimeupdate(self, table_name):

        connection = self.getconnection()
        cursor = connection.cursor()

        query = "SELECT to_char(max(dates),'YYYY-MM-DD') FROM log_updates WHERE tables = '"+table_name+"'"
        cursor.execute(query)
        results = cursor.fetchall()
        connection.close()
        return results[0][0]

    def getpopularitytable(self, filtertype, city ):

        connection = self.getconnection()
        cursor = connection.cursor()
        if filtertype == 'o':
            query = "SELECT origincitycode, destinationcitycode, concat(origincitycode, '-',destinationcitycode), seats FROM ptbexits_popular \
            WHERE origincitycode = '"+city+"' and destinationcitycode > 'AAA' \
            ORDER BY seats DESC LIMIT 10"
            cursor.execute(query)
        else:
            query = "SELECT origincitycode, destinationcitycode, concat(origincitycode, '-',destinationcitycode), seats FROM ptbexits_popular \
            WHERE origincitycode > 'AAA' and destinationcitycode = '"+city+"' \
            ORDER BY seats DESC LIMIT 10"
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

        j = simplejson.dumps(rowarray_list)

        connection.close()
        return rowarray_list



    def getnewflightstable(self):

        connection = self.getconnection()
        cursor = connection.cursor()

        query = "SELECT concat(originairport, destinationairport,  carriercode, weekday_mon_1), originairport, destinationairport,  carriercode, weekday_mon_1, to_char(first_exit, 'YYYY-MM-DD'), to_char(first_flight, 'YYYY-MM-DD'), to_char(last_flight, 'YYYY-MM-DD')  FROM ptbexits_airservice \
        ORDER BY first_exit DESC LIMIT 100000"
        cursor.execute(query)

        rows = [('a','b','c', 'd', 'e', 'f', 'g', 'h')]
        rowarray_list = []

        while len(rows) > 0:

            rows = cursor.fetchmany(500)

            # Convert query to row arrays
            for row in rows:
                rows_to_convert = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                t = list(rows_to_convert)
                rowarray_list.append(t)

        j = simplejson.dumps(rowarray_list)

        connection.close()
        return rowarray_list

    def getitintable(self,fromcity,tocity):

        connection = self.getconnection()
        cursor = connection.cursor()

        query = "SELECT * FROM ptbexits_itineraries WHERE origincitycode ='" + fromcity + "' AND destinationcitycode ='" + tocity + "' ORDER BY sum_seats DESC"

        cursor.execute(query)

        rows = [('a','a',1,2,'d','d',1, 2, 'g', 1, 2, 'j', 1,2, 3,4)]
        rowarray_list = []

        while len(rows) > 0:

            rows = cursor.fetchmany(500)

            # Convert query to row arrays
            for row in rows:
                rows_to_convert = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13],row[14] )
                t = list(rows_to_convert)
                rowarray_list.append(t)

        j = simplejson.dumps(rowarray_list)
        connection.close()
        return rowarray_list

    def getairporttable(self,airport):

        connection = self.getconnection()
        cursor = connection.cursor()

        query = "SELECT * \
        FROM ptbexits_airport \
        WHERE originairport ='" + airport + "' or destinationairport ='" + airport + "' "
        cursor.execute(query)

        rows = [('a','b','c', 1)]
        rowarray_list = []

        while len(rows) > 0:

            rows = cursor.fetchmany(500)
            # Convert query to row arrays
            for row in rows:
                rows_to_convert = (row[0], row[1], row[2], row[3], row[4])
                t = list(rows_to_convert)
                rowarray_list.append(t)

        j = simplejson.dumps(rowarray_list)

        connection.close()
        return rowarray_list

    def gettrendingtable(self,cityfrom, cityto):

        connection = self.getconnection()
        cursor = connection.cursor()

        query = "SELECT origincitycode, destinationcitycode, search_month, ranking \
        FROM ptbsearches_trending \
        WHERE origincitycode ='" + cityfrom + "' and destinationcitycode ='" + cityto + "' \
        ORDER BY search_month ASC"
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

        j = simplejson.dumps(rowarray_list)

        connection.close()
        return rowarray_list

    def getneuralattributes(self,od):
        connection = self.getconnection()
        cursor = connection.cursor()

        query = "SELECT sum_seats_cy, rank_from_org_cy, rank_from_dest_cy, \
        sum_seats_ly, rank_from_org_ly, rank_from_dest_ly  \
        FROM ptbexits_neural \
        WHERE origdestcitycode ='" + od + "'"

        cursor.execute(query)

        rows = (1,2,3,4,5,6)
        rowarray_list = []

        while len(rows) > 0:

            rows = cursor.fetchmany(1)
            # Convert query to row arrays
            for row in rows:
                rows_to_convert = (row[0], row[1], row[2], row[3], row[4], row[5])
                t = list(rows_to_convert)
                rowarray_list.append(t)

        j = simplejson.dumps(rowarray_list)

        if len(rowarray_list) == 0 : rowarray_list.append([0,0,0,0,0,0])
        connection.close()
        return rowarray_list[0]

    def getcatchment(self, airport, rangekm, destinationcity):
        connection = self.getconnection()
        cursor = connection.cursor()

        query = "SELECT usercountry, usercity, sum(seats) as sum_seats from (\
                SELECT * from (\
                SELECT *, \
                acos( \
                      cos(radians( latitude )) \
                    * cos(radians( airport_lat )) \
                    * cos(radians( longitude ) - radians( airport_long )) \
                    + sin(radians( latitude ))  \
                    * sin(radians( airport_lat )) \
                  )*6380 AS greatCircleDistance_in_km\
                from citypopandlocations CROSS JOIN \
                (\
                SELECT airport, latitude as airport_lat, longitude as airport_long \
                FROM iatatogeo \
                WHERE airport = '"+ airport +"' \
                ) as airport_coord \
                ) as full_table\
                where greatCircleDistance_in_km < " + str(rangekm) + " \
                ) as catchment \
                JOIN ptbexits_leakage on (usercity = accentcity and usercountry = countrycode) \
                WHERE destinationcitycode = '"+ destinationcity +"' \
                GROUP BY usercountry, usercity \
                ORDER BY sum_seats DESC\
                LIMIT 100"

        cursor.execute(query)

        rows = ('a', 'b',1)
        rowarray_list = []

        while len(rows) > 0:

            rows = cursor.fetchall()
            # Convert query to row arrays
            for row in rows:
                rows_to_convert = (row[0], row[1].encode('UTF-8'), row[2])
                t = list(rows_to_convert)
                rowarray_list.append(t)

        j = simplejson.dumps(rowarray_list)

        if len(rowarray_list) == 0 : rowarray_list.append([0,0,0])
        connection.close()
        return rowarray_list

    def getleakage(self, airport, rangekm, destinationcity):
        connection = self.getconnection()
        cursor = connection.cursor()

        query = "SELECT origincitycode, destinationcitycode, sum(seats) as sum_seats from (\
                SELECT * from (\
                SELECT *, \
                acos( \
                      cos(radians( latitude )) \
                    * cos(radians( airport_lat )) \
                    * cos(radians( longitude ) - radians( airport_long )) \
                    + sin(radians( latitude ))  \
                    * sin(radians( airport_lat )) \
                  )*6380 AS greatCircleDistance_in_km\
                from citypopandlocations CROSS JOIN \
                (\
                SELECT airport, latitude as airport_lat, longitude as airport_long \
                FROM iatatogeo \
                WHERE airport = '"+ airport +"' \
                ) as airport_coord \
                ) as full_table\
                where greatCircleDistance_in_km < " + str(rangekm) + " \
                ) as catchment \
                JOIN ptbexits_leakage on (usercity = accentcity and usercountry = countrycode) \
                WHERE destinationcitycode = '"+ destinationcity +"' \
                GROUP BY origincitycode, destinationcitycode \
                ORDER BY sum_seats DESC\
                LIMIT 100"

        cursor.execute(query)

        rows = ('a', 'b',1)
        rowarray_list = []

        while len(rows) > 0:

            rows = cursor.fetchall()
            # Convert query to row arrays
            for row in rows:
                rows_to_convert = (row[0], row[1], row[2])
                t = list(rows_to_convert)
                rowarray_list.append(t)

        j = simplejson.dumps(rowarray_list)

        if len(rowarray_list) == 0 : rowarray_list.append([0,0,0])
        connection.close()
        return rowarray_list



def __init__(self):
        print ("in init")
