import psycopg2
import json
import collections
import datetime
import numpy as np

from extractdata import *


extractdata = extractdata()

#train1 = extractdata.getneuralattributes('LON-NYC')
#train2 = extractdata.getneuralattributes('LON-BCN')
#train3 = extractdata.getneuralattributes('LON-ALC')
#train4 = extractdata.getneuralattributes('LON-AGP')
#train5 = extractdata.getneuralattributes('LON-BKK')
#train6 = extractdata.getneuralattributes('LON-TYO')

input_training =    [[1,2,1,4,5,6],
                    [1,2,1,4,5,6],
                    [1,2,100,23234,5,6],
                    [1,2,2,4,5,6],
                    [1,2,6,4,5,6],
                    [1,2,9,4,5,6]]

max_size = max(max(input_row[0] for input_row in input_training), max(input_row[3] for input_row in input_training))

for input_row in input_training :
    input_row[0] = input_row[0]/max_size
    input_row[3] = input_row[3]/max_size

output_training =   [[1],
                    [1],
                    [1],
                    [0],
                    [0],
                    [0]]

# sigmoid function
def nonlin(x,deriv=False):
    if(deriv==True):
        return x*(1-x)
    return 1/(1+np.exp(-x))

# input dataset
X = np.array(input_training,dtype='d')
print(X)
# output dataset
y = np.array(output_training,dtype='d')

# seed random numbers to make calculation
# deterministic (just a good practice)
np.random.seed(1)

# initialize weights randomly with mean 0
syn0 = 2*np.random.random((6,4)) - 1
syn1 = 2*np.random.random((4,1)) - 1

for iter in range(60000):

    # forward propagation
    l0 = X
    l1 = nonlin(np.dot(l0,syn0))
    l2 = nonlin(np.dot(l1,syn1))

    l2_error = y - l2

    if (iter % 10000) == 0:
	       print ("Error:" + str(np.mean(np.abs(l2_error))))

    l2_delta = l2_error*nonlin(l2,deriv=True)
    l1_error = l2_delta.dot(syn1.T)
    l1_delta = l1_error * nonlin(l1,deriv=True)

    syn1 += l1.T.dot(l2_delta)
    syn0 += l0.T.dot(l1_delta)

print ("Output After Training:")
array_json_syn0 = []
array_json_syn1 = []
print('ssyn0)
for i in range(0,3):
    t = (syn0[i][0],syn0[i][1],syn0[i][2],syn0[i][3])
    r = (syn1[i][0])
    array_json_syn0.append(t)
    array_json_syn1.append(r)

print (array_json_syn0, array_json_syn1)
