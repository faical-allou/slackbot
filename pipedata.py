
import os
import psycopg2
import json as simplejson
import collections
import datetime
import numpy as np
import math
from itertools import groupby
from operator import itemgetter
from configdatabase import connectionStringDatabase
from models.extractdata import *

extractdata = extractdata()

names_id = "ID, name, city,clicks"
my_data = np.genfromtxt('x_hotels_popular.txt', delimiter='\t',dtype=None, invalid_raise=False, names= names_id)

print(my_data[1]['ID'],my_data[1]['name'],my_data[1]['city'],my_data[1]['clicks'] )


conn = extractdata.getconnection()
cursor = conn.cursor()

my_data = np.delete(my_data, (0), axis=0)

for data in my_data:
    ID = data['ID']
    name = unicode(data['name'], "utf-8", errors='ignore')
    city = unicode(data['city'], "utf-8", errors='ignore')
    clicks = data['clicks']

    query =  "INSERT INTO popular_hotels_alexa (ID, name, city, clicks) VALUES (%s, %s, %s, %s);"
    data = (ID, name, city, clicks)

    cursor.execute(query, data)
    
    print (data)

conn.commit()