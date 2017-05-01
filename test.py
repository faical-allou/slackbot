import psycopg2
import datetime
import numpy as np

from extractdata import *

extractdatahere = extractdata()


connection = extractdatahere.getconnection()
cursor = connection.cursor()

query = "SELECT originairport, destinationcitycode, sum_seats\
        from (\
            SELECT usercountry, usercity, originairport, destinationcitycode, catchment.latitude as city_latitude, catchment.longitude as city_longitude, airport_lat, airport_long, \
            iata1.latitude,iata1.longitude, ground_transport, \
            acos((cos(radians( catchment.latitude )) * cos(radians( iata1.latitude )) * cos(radians( iata1.longitude ) - radians( airport_long )) \
             + sin(radians( catchment.latitude )) * sin(radians( iata1.latitude ))))*6300 as distance_alternate,  \
            acos((cos(radians(airport_lat )) * cos(radians(  iata2.latitude )) * cos(radians( airport_long ) - radians( iata2.longitude )) \
             + sin(radians( airport_lat )) * sin(radians(  iata2.latitude ))))*6300 as distance_od, \
            sum(seats) as sum_seats \
              from (\
              SELECT *\
                   from (\
                SELECT *, \
                acos(cos(radians( latitude )) * cos(radians( airport_lat )) * cos(radians( longitude ) - radians( airport_long )) + sin(radians( latitude )) * sin(radians( airport_lat )))*6380 AS ground_transport\
                from citypopandlocations \
                CROSS JOIN \
                  (\
                  SELECT airport, latitude as airport_lat, longitude as airport_long \
                  FROM iatatogeo iata0\
                  WHERE airport = 'LRH'\
                  ) as airport_coord \
               ) as interim_table\
              where ground_transport < 300\
              ) as catchment \
            JOIN ptbexits_leakage on (usercity = accentcity and usercountry = countrycode) \
            JOIN iatatogeo iata1 on (originairport = iata1.airport)\
            JOIN iatatogeo iata2 on (destinationcitycode = iata2.airport)\
            GROUP BY usercountry, usercity, originairport, destinationcitycode, catchment.latitude, catchment.longitude, airport_lat, airport_long, distance_alternate, iata1.latitude,iata1.longitude , ground_transport, distance_od \
            ) as fulltable\
        WHERE destinationcitycode = 'LON' and originairport is not NULL and distance_alternate < 0.5*distance_od and ground_transport < distance_od\
        ORDER BY sum_seats DESC\
        LIMIT 10"
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

print(rowarray_list)
