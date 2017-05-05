import psycopg2
import datetime
import numpy as np

from extractdata import *

extractdatahere = extractdata()


connection = extractdatahere.getconnection()
cursor = connection.cursor()

query = "SELECT iata1.city, iata2.city \
    FROM ptbexits_popular \
    join iatatogeo iata1 \
    ON iata1.airport = origincitycode\
    JOIN iatatogeo iata2\
    ON iata2.airport = destinationcitycode\
    WHERE iata1.city = 'London' and destinationcitycode > 'AAA' \
    ORDER BY seats DESC LIMIT 10"
cursor.execute(query)

rows = [('a','b')]
rowarray_list = []

while len(rows) > 0:

    rows = cursor.fetchmany(500)
    # Convert query to row arrays
    for row in rows:
        rows_to_convert = (row[0], row[1])
        t = list(rows_to_convert)
        rowarray_list.append(t)

j = simplejson.dumps(rowarray_list)

connection.close()

print(rowarray_list)
