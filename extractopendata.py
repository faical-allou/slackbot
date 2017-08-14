import os
import psycopg2
import simplejson
import collections
import datetime
import numpy as np

class extractopendata:

    def getopenairportdata(self):
        filename = './static/text/airport_table.dat'
        data = []
        with open(filename, "rt",encoding="utf8") as f1:
            for line in f1:
                x = line.split(',')
                if len(x[4]) == 5:
                    data.append([x[4][1]+x[4][2]+x[4][3],float(x[6]),float(x[7]), x[1],x[2],x[3]])
        return data


def __init__(self):
        print ("in init")
