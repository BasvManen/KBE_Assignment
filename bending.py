# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 15:55:16 2020

@author: Stijn
"""

from math import pi, sin, cos, tan, radians
import numpy as np
from matplotlib import pyplot as plt


def sumz_moment(list1, yi, elementset):         # this function calculates the moment induced by a force ditribution
    list2 = []
    for i in range(len(list1)):
        if yi[i] < elementset:
            outcome = list1[i] * (elementset - yi[i])
        else:
            outcome = 0
        list2.append(outcome)
    return sum(list2)


spoiler_weight = 20 * 9.80665
spoiler_span = 2
spoiler_chord = 0.8
spoiler_area = 2.4
strut_lat_location = 0.5
strut_location_1 = spoiler_span/2*(1-strut_lat_location)
strut_location_2 = spoiler_span/2*(1+strut_lat_location)

lift = -100*np.ones(30)

yi = np.zeros(len(lift)+1)
yii = np.zeros(len(lift))
Si = np.zeros(len(lift))
Wi = np.zeros(len(lift))
di = spoiler_span/len(lift)

for i in range(len(lift)+1):
    yi[i] = i*di

for i in range(len(lift)):
    yii[i] = yi[i] + (yi[i+1]-yi[i])/2
    Si[i] = spoiler_chord*di
    Wi[i] = -spoiler_weight/spoiler_area*Si[i]  # force downward

f_strut_z = -(sum(lift) + sum(Wi))/2

momentLi = []
momentWi = []
for i in range(len(lift)+1):
    yset = yi[i]
    momentL = sumz_moment(lift, yii, yset)
    momentW = sumz_moment(Wi, yii, yset)
    momentLi.append(momentL)
    momentWi.append(momentW)

# moment along strut in x
momentxi = []
for i in range(len(lift)+1):
    yset = yi[i]
    if yset >= strut_location_2 and yset >= strut_location_1:
        momi = f_strut_z*(yset-strut_location_2) + f_strut_z*(yset-strut_location_1) + momentLi[i] + momentWi[i]
        momentxi.append(momi)
    elif yset < strut_location_2  and yset >= strut_location_1:
        momi = f_strut_z*(yset-strut_location_1) + momentLi[i] + momentWi[i]
        momentxi.append(momi)
    elif yset < strut_location_2 and yset < strut_location_1:
        momi = momentLi[i] + momentWi[i]
        momentxi.append(momi)

plt.plot(yi, momentxi)
