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
            ORDER BY sum_seats DESC LIMIT 3"
        print(city)
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

    def getpopularitytablealexa_hotels(self, filtertype, city ):

        connection = self.getconnection()
        cursor = connection.cursor()
        query = "SELECT name from traveltrends.popular_hotels_alexa where city ='"+city+"'\
            ORDER BY clicks DESC LIMIT 3"
        print(city)
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



def __init__(self):
        print ("in init")
