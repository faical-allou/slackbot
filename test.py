import psycopg2
import datetime
import numpy as np
from itertools import groupby
from extractdata import *

extractdatahere = extractdata()


connection = extractdatahere.getconnection()
cursor = connection.cursor()
crossbordercondition = ""
crossbordercondition = "and airport_country = usercountry"
airport = 'CGN'
rangekm = '50'
destinationcity = 'BKK'
crossborder = 'N'

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
        ORDER BY sum_seats DESC\
        LIMIT 50"

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
    catchment_list.append([i[0],i[1],i[2],i[3], sum(v[4] for v in g)])

leakage_list = []
for i, g in groupby(sorted(rowarray_list, key=lambda x: (x[0],x[1]) ), key=lambda x: (x[0],x[1])):
    leakage_list.append([i[0],i[1], sum(v[4] for v in g)])



print ('final result')
print catchment_list
print leakage_list

