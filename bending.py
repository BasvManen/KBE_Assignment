from math import pi, sin, cos, tan, radians
import numpy as np
from matplotlib import pyplot as plt


# formula to calculate moment due to a distributed force
def sumz_moment(list1, yi, elementset):
    list2 = []
    for i in range(len(list1)):
        if yi[i] < elementset:
            outcome = list1[i] * (elementset - yi[i])
        else:
            outcome = 0
        list2.append(outcome)
    return sum(list2)


# input parameters of the geometry
g = 9.80665
spoiler_weight = 20 * g
endplate_weight = 0.5 * g
spoiler_span = 2
spoiler_chord = 0.8
spoiler_area = 2.4
strut_lat_location = 0.9
strut_location_1 = spoiler_span / 2 * (1 - strut_lat_location)
strut_location_2 = spoiler_span / 2 * (1 + strut_lat_location)

# list with the lift force at each increment i
lift = -100 * np.ones(200)

# input sectional parameters
E = 70 * 10 ** 9
Ixx = 10 ** -6 * np.ones(len(lift) + 1)

# calculating y-coordinate, area and weight at each increment i
yi = np.zeros(len(lift) + 1)
yii = np.zeros(len(lift))
Si = np.zeros(len(lift))
Wi = np.zeros(len(lift))
di = spoiler_span / len(lift)

for i in range(len(lift) + 1):
    yi[i] = round(i * di, 3)

for i in range(len(lift)):
    yii[i] = yi[i] + (yi[i + 1] - yi[i]) / 2
    Si[i] = spoiler_chord * di
    Wi[i] = -spoiler_weight / spoiler_area * Si[i]  # force downward

# adding the weight of the endplate to the first and last Wi
Wi[0] += endplate_weight
Wi[-1] += endplate_weight

# calculate the z-force on the strut by sum of forces in z
f_strut_z = -(sum(lift) + sum(Wi)) / 2

# calculate the influence of the lift and weight on the bending moment for each increment i
momentLi = []
momentWi = []
for i in range(len(lift) + 1):
    yset = yi[i]
    momentL = sumz_moment(lift, yii, yset)
    momentW = sumz_moment(Wi, yii, yset)
    momentLi.append(momentL)
    momentWi.append(momentW)

# calculating the moment along strut in x
momentxi = []
for i in range(len(lift) + 1):
    yset = yi[i]
    if yset >= strut_location_2 and yset >= strut_location_1:
        momi = f_strut_z * (yset - strut_location_2) + f_strut_z * (yset - strut_location_1) + momentLi[i] + momentWi[i]
        momentxi.append(momi)
    elif yset < strut_location_2 and yset >= strut_location_1:
        momi = f_strut_z * (yset - strut_location_1) + momentLi[i] + momentWi[i]
        momentxi.append(momi)
    elif yset < strut_location_2 and yset < strut_location_1:
        momi = momentLi[i] + momentWi[i]
        momentxi.append(momi)

# calculate deflection angles and displacment
# the deflection angle in the centerline of the spoiler is 0
# the deflection at the struts is considered equal to 0
thetai = np.zeros(len(lift) + 1)
for i in range(int(len(lift) / 2) + 1, len(lift) + 1):
    thetai[i] = thetai[i - 1] + 0.5 * (momentxi[i] / (E * Ixx[i]) + momentxi[i - 1] / (E * Ixx[i - 1])) * (
                yi[i] - yi[i - 1])

index_strut = np.where(yi == strut_location_2)[0][0]
vi = np.zeros(len(lift) + 1)
for i in range(index_strut, len(lift) + 1):
    vi[i] = vi[i - 1] + 0.5 * (thetai[i] + thetai[i - 1]) * (yi[i] - yi[i - 1])

for i in range(index_strut + 1, int(len(lift) / 2), -1):
    vi[i - 1] = vi[i] - 0.5 * (thetai[i] + thetai[i - 1]) * (yi[i] - yi[i - 1])

for i in range(int(len(lift) / 2)):
    thetai[i] = thetai[len(lift) - i]
    vi[i] = vi[len(lift) - i]

# # plotting
# plt.figure()
# plt.plot(yi, thetai)
# plt.plot(yi, vi)
# plt.grid()
#
# plt.figure()
# plt.plot(yi, momentxi)
# plt.grid()