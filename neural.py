import psycopg2
import json
import collections
import datetime
import sys
import numpy as np
import ast

from extractdata import *

extractdatahere = extractdata()

class neural_network:
    # sigmoid function
    def nonlin(self,x,deriv=False):
        if(deriv==True):
            return x*(1-x)
        return 1/(1+np.exp(-x))

    def trainneuralnetwork(self, in1,in2,in3,in4,in5,in6, out1,out2,out3,out4,out5,out6):
        train1 = extractdatahere.getneuralattributes(in1)
        train2 = extractdatahere.getneuralattributes(in2)
        train3 = extractdatahere.getneuralattributes(in3)
        train4 = extractdatahere.getneuralattributes(in4)
        train5 = extractdatahere.getneuralattributes(in5)
        train6 = extractdatahere.getneuralattributes(in6)

        input_training = [train1, train2, train3, train4, train5, train6]
        print('input_training=', input_training)
        max_input_from_database = [0,0,0,0,0,0]

        for i in range(0,6):
            max_input_from_database[i] = max(max(input_row[i] for input_row in input_training), 1000)
            for input_row in input_training :
                input_row[i] = input_row[i]/max_input_from_database[i]

        print('input after normal= ', input_training)

        output_training =   [[out1], [out2], [out3], [out4], [out5], [out6]]

        # input dataset
        X = np.array(input_training,dtype='d')
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

        array_json_l2 = [l2[0][0],l2[1][0],l2[2][0],l2[3][0],l2[4][0],l2[5][0]]

        return (array_json_syn0,array_json_syn1,max_input_from_database,array_json_l2)

    def predict(self,input_od,syn0received,syn1received, normalizer_received):
        # input dataset
        #input_predict = [[1.0000,2.0000,1.00000,4.00000,5.0000,6.00000]]
        input_predict = extractdatahere.getneuralattributes(input_od)
        print('input_predict=', input_predict)

        normalizer = ast.literal_eval(normalizer_received)

        for i in range(0,6):
            input_predict[i] = input_predict[i]/float(normalizer[i])

        X = np.array(input_predict,dtype='d')

        syn0 = np.array(ast.literal_eval(syn0received)).reshape(6,4)
        syn1 = np.array(ast.literal_eval(syn1received)).reshape(4,1)

        # forward propagation
        l0 = X
        l1 = self.nonlin(np.dot(l0,syn0))
        l2 = self.nonlin(np.dot(l1,syn1))

        t = l2[0]

        print('normalizer= ', normalizer)
        print('X= ', X)
        print('syn0= ',syn0)
        print('syn1= ',syn1)

        print(l1)
        print(l2)
        print(t)

        return (t)

def __init__(self):
        print ("in init")
