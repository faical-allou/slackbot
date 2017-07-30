import os
import psycopg2
import simplejson
import collections
import datetime
import numpy as np
import math
from itertools import groupby
from operator import itemgetter
from configdatabase import connectionStringDatabase

class extractdata:
    def getconnection(self):

        #Define our connection string to heroku basic database
        if os.environ.get('ON_HEROKU'):
            conn_string = os.environ.get('DATABASE_URL')
        else :
            conn_string = connectionStringDatabase
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

        connection.close()
        #normalize the table (adding 1 to the sum to return 0 when empty)
        if len(rowarray_list) == 10:
            max_popular = max(max(row[3] for row in rowarray_list),1)
        else :
            max_popular = 99999

        for k in range(0,len(rowarray_list)):
            rowarray_list[k][3] = round(rowarray_list[k][3]*100/max_popular)

        return rowarray_list

    def getnewflightstable(self):

        connection = self.getconnection()
        cursor = connection.cursor()

        query = "SELECT concat(originairport, destinationairport,  carriercode, weekday_mon_1), \
        originairport, destinationairport,  carriercode, weekday_mon_1, to_char(first_exit, 'YYYY-MM-DD'), \
        to_char(first_flight, 'YYYY-MM-DD'), to_char(last_flight, 'YYYY-MM-DD')  \
        FROM ptbexits_airservice \
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

        connection.close()
        # formatting the row label
        for k in range(0,len(rowarray_list)-1):
            rowarray_list[k][0] = rowarray_list[k][1] + "-" + rowarray_list[k][2]+ "\n" + " by " + rowarray_list[k][3] + " on "+ rowarray_list[k][4]

        return rowarray_list

    def getitintable(self,fromcity,tocity):

        connection = self.getconnection()
        cursor = connection.cursor()

        query = "SELECT * FROM ptbexits_itineraries \
        WHERE origincitycode ='" + fromcity + "' AND destinationcitycode ='" + tocity + "' \
        ORDER BY sum_seats DESC"

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

        connection.close()
        #Converting to float and normalize the table (adding 1 to the sum to return 0 when empty)
        if len(rowarray_list) == 0:
            max_itin = 1
        else:
            max_itin = max(row[14] for row in rowarray_list)+1

        for k in range(0,len(rowarray_list)):
            rowarray_list[k][14] = max(rowarray_list[k][14]*3/max_itin,1)

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

        connection.close()
        hub = [['id','ap','time',0,0,0,0]]
        if len(rowarray_list) > 0 :
            #Converting to float normalize the table (adding 1 to the sum to return 0 when empty)
            # and formatting for easy consumption by the chart
            # getting the list of airports to consider, the final table is based on airport
            transpose = list(zip(*rowarray_list))
            transposelist = list(transpose[0])
            transposelist1 = list(transpose[1])
            transposelist.extend(transposelist1)
            airport_list = list(set(transposelist))
            airport_list.remove('xxx')

            # getting size of the large table from the database to iterate on
            airport_size = len(rowarray_list)

            # initializing the hub table that wil be returned with first column as ID AIrport/timeofday
            # also building an index table to retrieve the right row to fill in when iterating later
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

                if rowarray_list[k][0] == 'xxx' :
                    airport_to_fill = rowarray_list[k][1]
                else:
                    airport_to_fill = rowarray_list[k][0]
                    rowarray_list[k][4] = -1*rowarray_list[k][4]
                    departureflag = 1

                #reading from hub_col0 to find the row to fill in the hub table
                index0 = hub_col0.index(airport_to_fill + rowarray_list[k][2])

                if 'local' in rowarray_list[k][3]:
                    hub[index0][3+departureflag] = hub[index0][3+departureflag] + float(rowarray_list[k][4])
                else: hub[index0][5+departureflag] = hub[index0][5+departureflag] + float(rowarray_list[k][4])

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
        resp = (hub, len(rowarray_list))
        return resp

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

        if len(rowarray_list) == 0 : rowarray_list.append([0,0,0,0,0,0])
        connection.close()
        return rowarray_list[0]


    def getfullcatchment(self, airport, rangekm, destinationcity, crossborder):
        connection = self.getconnection()
        cursor = connection.cursor()
        crossbordercondition = ""
        if crossborder != 'Y': crossbordercondition = "and airport_country = usercountry"

        query = "SELECT originairport, destinationcitycode, usercountry, usercity, sum(sum_seats) as sum_seats, city_latitude, city_longitude, airport_lat, airport_long\
                from (\
                    SELECT usercountry, usercity, originairport, destinationcitycode, catchment.latitude as city_latitude, catchment.longitude as city_longitude, airport_lat, airport_long, \
                    iata1.latitude,iata1.longitude, ground_transport,airport_country, \
                    acos((cos(radians( catchment.latitude )) * cos(radians( iata1.latitude )) * cos(radians( iata1.longitude ) - radians( airport_long )) \
                     + sin(radians( catchment.latitude )) * sin(radians( iata1.latitude ))))*6300 as distance_alternate,  \
                    acos((cos(radians(airport_lat )) * cos(radians(  iata2.latitude )) * cos(radians( airport_long ) - radians( iata2.longitude )) \
                     + sin(radians( airport_lat )) * sin(radians(  iata2.latitude ))))*6300 as distance_od, \
                    acos((cos(radians(iata1.latitude )) * cos(radians(  iata2.latitude )) * cos(radians( iata1.longitude ) - radians( iata2.longitude )) \
                     + sin(radians( iata1.latitude )) * sin(radians(  iata2.latitude ))))*6300 as distance_newod, \
                    sum(seats) as sum_seats \
                      from (\
                      SELECT *\
                           from (\
                        SELECT *, \
                        acos(cos(radians( latitude )) * cos(radians( airport_lat )) * cos(radians( longitude ) - radians( airport_long )) + sin(radians( latitude )) * sin(radians( airport_lat )))*6380 AS ground_transport\
                        from citypopandlocations \
                        CROSS JOIN \
                          (\
                          SELECT airport, countrycode as airport_country, latitude as airport_lat, longitude as airport_long \
                          FROM iatatogeo iata0\
                          WHERE airport = '"+airport+"'\
                          ) as airport_coord \
                       ) as interim_table\
                      where ground_transport < "+rangekm+"\
                      ) as catchment \
                    JOIN ptbexits_leakage on (usercity = accentcity and usercountry = airport_country) \
                    JOIN iatatogeo iata1 on (originairport = iata1.airport)\
                    JOIN iatatogeo iata2 on (destinationcitycode = iata2.airport)\
                    GROUP BY usercountry, usercity, originairport, destinationcitycode, \
                    catchment.latitude, catchment.longitude, airport_lat, airport_long, distance_alternate, \
                    iata1.latitude,iata1.longitude , ground_transport, distance_od, distance_newod,airport_country \
                    ) as fulltable\
                WHERE destinationcitycode = '"+destinationcity+"' and \
                originairport is not NULL and distance_alternate < distance_od/3 \
                and distance_newod + distance_alternate < 1.5*distance_od\
                "+ crossbordercondition +"\
                GROUP BY originairport, destinationcitycode, usercountry, usercity, city_latitude, city_longitude, airport_lat, airport_long \
                ORDER BY sum_seats DESC"

        cursor.execute(query)

        rows = ('a', 'b','c', 'd', 1,2,3,4,5)
        rowarray_list = []

        while len(rows) > 0:

            rows = cursor.fetchall()
            # Convert query to row arrays
            for row in rows:
                rows_to_convert = (row[0], row[1], row[2], row[3], row[4],row[5],row[6],row[7],row[8] )
                t = list(rows_to_convert)
                rowarray_list.append(t)

        if len(rowarray_list) == 0 : rowarray_list.append([0,0,0,0,0,0,0,0,0])
        connection.close()

        catchment_list = []
        for i, g in groupby(sorted(rowarray_list, key=lambda x: (x[2],x[3],x[5],x[6]) ), key=lambda x: (x[2],x[3],x[5],x[6])):
            catchment_list.append([i[0],i[1],i[2],i[3], float(sum(v[4] for v in g))])

        catchment_list.sort(key=itemgetter(4), reverse=True)
        del catchment_list[30:]
        

        leakage_list = []
        for i, g in groupby(sorted(rowarray_list, key=lambda x: (x[0],x[1]) ), key=lambda x: (x[0],x[1])):
            leakage_list.append([i[0],i[1], float(sum(v[4] for v in g))])

        leakage_list.sort(key=itemgetter(2), reverse=True)
        del leakage_list[5:]

        #normalizing the data
        peak_catchment = max(row[4] for row in catchment_list )+1
        for row in catchment_list:
            row[4] = round(row[4]*100/peak_catchment)

        airport_coord = (rowarray_list[0][7], rowarray_list[0][8])

        #normalize data, removes airports with less than 1%;
        sum_leakage = sum(row[2] for row in leakage_list )+1
        leakage_list = [row for row in leakage_list if row[2]> sum_leakage/100]

        sum_leakage = sum(row[2] for row in leakage_list )+1

        #identify the home airport and its share of total
        home_size = 0
        sample_size = 1
        for row in leakage_list:
            if row[0] == airport : sample_size = float(row[2])
            row[2] = round(row[2]*100/sum_leakage)
            if row[0] == airport : home_size = row[2]

        airport_share = home_size / (sum(row[2] for row in leakage_list)+1)
        #calculate the confidence factor for 95% of a sample of unknown size
        confidence = 1.96* math.sqrt(airport_share*(1-airport_share)/(sample_size))

        resp = (catchment_list, airport_coord,leakage_list,airport_share, confidence, peak_catchment)
        return resp


    def getpopularitytablealexa(self, filtertype, city ):

        connection = self.getconnection()
        cursor = connection.cursor()
        query = "SELECT iata2.city \
            FROM ptbexits_popular \
            join iatatogeo iata1 \
            ON iata1.airport = origincitycode\
            JOIN iatatogeo iata2\
            ON iata2.airport = destinationcitycode\
            WHERE iata1.city = '"+city+"' and destinationcitycode > 'AAA' \
            ORDER BY seats DESC LIMIT 3"
        cursor.execute(query)

        rows = ['a']
        rowarray_list = []

        dest_list = []

        rows = cursor.fetchall()

        for row in rows:
            dest_list.extend(row)
        print(dest_list)

        connection.close()

        return dest_list

    def moving_average(self,a, n=3) :
        #function is used in the get fastest growing
        ret = np.cumsum(a, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n

    def getfastestgrowing(self, city):
        connection = self.getconnection()
        cursor = connection.cursor()
        query = "SELECT * FROM ptbsearches_trending \
            WHERE  origincitycode = '"+city+"' \
            ORDER BY destinationcitycode, search_month ASC"

        cursor.execute(query)

        rows = cursor.fetchall()

        rows_converted = np.asarray(rows)
        save_dest = rows_converted[0][1]
        result = [[save_dest]]

        i = 0
        j = 0
        for res in rows_converted:
            if res[1] == save_dest:
                result[i].append(res[4])
            else:
                save_dest = res[1]
                result.append([])
                i = i+1
                result[i].append(res[1])
                result[i].append(res[4])

        rows_smoothed = []
        x = []
        z = []
        y = []

        #ensure we have enough data points <=> meaning no month where rank went below 200
        lastupdate = extractdata.getlasttimeupdate(self,'ptbexits_popular')
        lastupdate_date = datetime.datetime.strptime(lastupdate, '%Y-%m-%d')
        earliest_date = datetime.datetime.strptime('2014-02-02', '%Y-%m-%d')

        max_range_data = (lastupdate_date.year - earliest_date.year)*12 + (lastupdate_date.month - earliest_date.month) + 1

        #we calculate the 12 month rolling average of the rank and measure the slope of the curve
        for index, rows_to_smooth in enumerate(result):
            mov_avg_row = self.moving_average(np.asarray(rows_to_smooth[1:], dtype=float),12)
            rows_smoothed.append(mov_avg_row)
            x=np.arange(0,len(mov_avg_row))
            dest = [str(rows_to_smooth[0])]

            if len(x) == max_range_data-11:
                z.append(list(np.append(dest,np.polyfit (x,mov_avg_row,1))))

        for t in z:
            y.append( [t[0], t[1].astype(float), t[2].astype(float)] )

        y.sort(key=lambda k: (k[1]), reverse=False)

        rows = ('a', 1,1)
        rowarray_list = []
        i=0
        # Convert query to row arrays
        for row in y:
            i=i+1
            if i <=10 and  row[1] < 0:
                rows_to_convert = (row[0], -row[1], row[2])
                t = list(rows_to_convert)
                rowarray_list.append(t)

        return rowarray_list


def __init__(self):
        print ("in init")
