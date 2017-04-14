import psycopg2
import datetime
import numpy as np


def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


#Define connection string to heroku
conn_string1 = "host='ec2-54-235-125-135.compute-1.amazonaws.com' port='5432' dbname='d4sjjjfm3g35dc' user='swobzoejynjhpk' password='aJS-yO6EBUg6DgzVQSFwp3Ac1v'"

today_flag = datetime.date.today()

    # Connect and send query
try:
        conn_heroku = psycopg2.connect(conn_string1)
except psycopg2.Error as e:
        print ("Unable to connect to heroku!")
        print (e.pgerror)
        print (e.diag.message_detail)
        sys.exit(1)
else:
        print ("Connected to heroku!")
        cursor_heroku = conn_heroku.cursor()
        query = "SELECT * FROM ptbsearches_trending \
        WHERE  origincitycode = 'EDI' \
        ORDER BY destinationcitycode, search_month ASC"


        print (query)
        cursor_heroku.execute(query)

rows = cursor_heroku.fetchall()

rows_converted = np.asarray(rows)


save_dest = rows_converted[0][1]
result = [[save_dest]]

i = 0
j = 0
for res in rows_converted:
    if res[1] == save_dest:
        result[i].append(res[4])
    else:
        save_dest = res[1]
        result.append([])
        i = i+1
        result[i].append(res[1])
        result[i].append(res[4])



rows_smoothed = []
x = []
z = []
y = []

for index, rows_to_smooth in enumerate(result):
    mov_avg_row = moving_average(np.asarray(rows_to_smooth[1:], dtype=float),12)
    rows_smoothed.append(mov_avg_row)

    x=np.arange(0,len(mov_avg_row))

    dest = [str(rows_to_smooth[0])]
    if len(x) >= 28:
        z.append(list(np.append(dest,np.polyfit (x,mov_avg_row,1))))


for t in z:
    y.append( [t[0], t[1].astype(float), t[2].astype(float)] )

y.sort(key=lambda k: (k[1]), reverse=False)


for rows_y in y:
    print (rows_y)
