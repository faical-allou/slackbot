import psycopg2
import json
import collections
import datetime
import numpy as np

from extractdata import *

# sigmoid function
def nonlin(x,deriv=False):
    if(deriv==True):
        return x*(1-x)
    return 1/(1+np.exp(-x))

l0 = [0.30827911,   0.17741935,   0.62222222,   0.45303303,   0.08695652,  64.]
syn0=  [[ 1.75454973 , 2.70669757, -5.78549999, -6.49556612], [-0.06202339, -1.41462215, -2.40972605, -3.21430068], [ 1.02760372,  2.91801657, -3.35877642, -3.82644499], [ 0.08637284, -0.91458126,  4.08457981,  4.78190343], [-0.07369381, -2.08231119,  0.85565128,  0.49731896], [ 1.33789304,  3.10584774,  2.4490087,   3.9109122 ]]

syn1=  [[  3.32726845], [  8.37401836], [-16.50255589], [-17.51222328]]

# forward propagation

l1 = nonlin(np.dot(l0,syn0))
l2 = nonlin(np.dot(l1,syn1))

print('l0=' , l0)
print('l1=' , l1)
print('l2=' , l2)
