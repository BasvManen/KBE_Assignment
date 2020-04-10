from math import pi, sin, cos, tan, radians
import numpy as np

from spoiler_files.strut import Strut


def sumz_moment(list1, yi, elementset):
    list2 = []
    for i in range(len(list1)):
        if yi[i] < elementset:
            outcome = list1[i] * (elementset - yi[i])
        else:
            outcome = 0
        list2.append(outcome)
    return sum(list2)


spoiler_weight = 20 * 9.80665
spoiler_span = 3
spoiler_chord = 0.8
spoiler_area = 2.4
strut_lat_location = 0.5
strut_location_1 = spoiler_span/2*(1-strut_lat_location)
strut_location_2 = spoiler_span/2*(1+strut_lat_location)

lift = [-10, -60, -80, -90, -100, -90, -80, -60, -10]

yi = np.zeros(len(lift)+1)
Si = np.zeros(len(lift))
Wi = np.zeros(len(lift))
di = spoiler_span/len(lift)

for i in range(len(lift)+1):
    yi[i] = i*di

for i in range(len(lift)):
    Si[i] = spoiler_chord*di
    Wi[i] = -spoiler_weight/spoiler_area*Si[i]  # force downward

f_strut_z = -(sum(lift) + sum(Wi))/2

momentLi = []
momentWi = []
for i in range(len(lift)+1):
    yset = yi[i]
    momentL = sumz_moment(lift, yi, yset)
    momentW = sumz_moment(Wi, yi, yset)
    momentLi.append(momentL)
    momentWi.append(momentW)

# moment along strut in x
momentxi = []
for i in range(len(lift)+1):
    yset = yi[i]
    if yset >= strut_location_2 and yset >= strut_location_1:
        momi = f_strut_z/2*(strut_location_2-yset) + f_strut_z/2*(strut_location_1-yset) - momentLi[i] - momentWi[i]
        momentxi.append(momi)
    elif strut_location_2 > yset >= strut_location_1:
        momi = f_strut_z/2*(strut_location_1-yset) - momentLi[i] - momentWi[i]
        momentxi.append(momi)
    elif yset < strut_location_2 and yset < strut_location_1:
        momi = -momentLi[i] - momentWi[i]
        momentxi.append(momi)

print(momentxi)
print(momentLi)
print(momentWi)