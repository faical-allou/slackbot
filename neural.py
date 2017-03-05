import psycopg2
import json
import collections
import datetime
import sys
import numpy as np

from extractdata import *

extractdatahere = extractdata()

class neural_network:
    # sigmoid function
    def nonlin(self,x,deriv=False):
        if(deriv==True):
            return x*(1-x)
        return 1/(1+np.exp(-x))

    def trainneuralnetwork(self, in1,in2,in3,in4,in5,in6, out1,out2,out3,out4,out5,out6):
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
            l1 = self.nonlin(np.dot(l0,syn0))
            l2 = self.nonlin(np.dot(l1,syn1))

            l2_error = y - l2

            if (iter % 10000) == 0:
        	       print ("Error:" + str(np.mean(np.abs(l2_error))))

            l2_delta = l2_error*self.nonlin(l2,deriv=True)
            l1_error = l2_delta.dot(syn1.T)
            l1_delta = l1_error * self.nonlin(l1,deriv=True)

            syn1 += l1.T.dot(l2_delta)
            syn0 += l0.T.dot(l1_delta)

        print ("Output After Training:")
        print (l2)
        array_json_syn0 = []
        array_json_syn1 = [syn1[0][0],syn1[1][0],syn1[2][0],syn1[3][0]]

        for i in range(0,6):
            t = (syn0[i][0],syn0[i][1],syn0[i][2],syn0[i][3] )
            array_json_syn0.append(t)


        return (array_json_syn0,array_json_syn1)

    def predict(self,input_od,syn0received,syn1received):
        # input dataset
        input_predict = [[1.0000,2.0000,1.00000,4.00000,5.0000,6.00000]]
        #input_predict = extractdatahere.getneuralattributes(input_od)
        X = np.array(input_predict,dtype='d')

        syn0 = np.fromstring(syn0received, dtype= 'd', count=24, sep=',').reshape(6,4)
        syn1 = np.fromstring(syn1received, dtype= 'd', count=4, sep=',').reshape(4,1)

        # forward propagation
        l0 = X
        l1 = self.nonlin(np.dot(l0,syn0))
        l2 = self.nonlin(np.dot(l1,syn1))

        print(l2.dtype)
        print(l2)
        sys.stdout.flush()

        t = l2[0][0]

        return (t)

def __init__(self):
        print ("in init")
