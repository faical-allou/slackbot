import os
import psycopg2
import json as simplejson
import collections
import datetime
import numpy as np
import math
import re
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
            print(conn_string)
            conn = psycopg2.connect(conn_string, sslmode='require')
            #conn = psycopg2.connect(conn_string, sslmode='require')
            
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
        query = "SELECT name from partners where partner_id ="+partner_id
        print(query)
        cursor.execute(query)

        rows = ['a']
        rowarray_list = []

        partner_list = []

        rows = cursor.fetchall()

        for row in rows:
            partner_list.extend(row)
        print(partner_list)

        connection.close()

        return partner_list[0]

    def getpartnerid(self, partner_name ):

        connection = self.getconnection()
        cursor = connection.cursor()
        query = "SELECT partner_id, name from partners where name like '%"+partner_name+"%'"
        print(query)
        cursor.execute(query)

        rows = ['a']
        rowarray_list = []

        partner_list = []

        rows = cursor.fetchall()

        for row in rows:
            partner_list.append(row)
        print(partner_list)

        connection.close()
        output = '\n'.join(str(a) for a in partner_list)
        output = re.sub("['(!@#$)]", '', output)
        return output

def __init__(self):
        print ("in init")
