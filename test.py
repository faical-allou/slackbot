import psycopg2
import json
import collections
import datetime

from extractdata import *

extractdata = extractdata()

print(extractdata.getlasttimeupdate('ptbexits_airservice'))
