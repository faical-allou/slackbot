import psycopg2
import datetime
import numpy as np

from extractdata import *

extractdatahere = extractdata()


catchment = extractdatahere.getcatchment('CGN', 20, 'NYC')

print (catchment)
