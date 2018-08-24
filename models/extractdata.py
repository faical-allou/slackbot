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


    def getpartnername(self, partner_id ):

        connection = self.getconnection()
        cursor = connection.cursor()
        query = "SELECT name from partners where partner_id ='"+partner_id
        print(partner_id)
        cursor.execute(query)

        rows = ['a']
        rowarray_list = []

        partner_list = []

        rows = cursor.fetchall()

        for row in rows:
            partner_list.extend(row)
        print(partner_list)

        connection.close()

        return partner_list



def __init__(self):
        print ("in init")
