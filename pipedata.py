
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

names_id = "partner_id, name"
my_data = np.genfromtxt('partners.csv', delimiter=',',dtype=None, invalid_raise=False, names= names_id)

print(my_data[1]['partner_id'],my_data[1]['name'] )


conn = extractdata.getconnection()
cursor = conn.cursor()

my_data = np.delete(my_data, (0), axis=0)

for data in my_data:
    partner_id = data['partner_id']
    name = unicode(data['name'], "utf-8", errors='ignore')

    query =  "INSERT INTO partners (partner_id, name) VALUES (%s, %s);"
    data = (partner_id, name)

    cursor.execute(query, data)
    
    print (data)

conn.commit()