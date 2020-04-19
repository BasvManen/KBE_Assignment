from math import pi, sin, cos, tan, radians
import numpy as np
from matplotlib import pyplot as plt


# function to calculate moment due to a distributed force
def sumz_moment(list1, y_i, elementset):
    list2 = []
    for i in range(len(list1)):
        if y_i[i] < elementset:
            outcome = list1[i] * (elementset - y_i[i])
        else:
            outcome = 0
        list2.append(outcome)
    return sum(list2)


# function to calculate stresses/displacement of the main spoiler plate
def mainplate_bending(lift, E, Ixx, spoiler_weight, endplate_weight, spoiler_span, spoiler_chord, spoiler_area, strut_lat_location):
    strut_location_1 = spoiler_span / 2 * (1 - strut_lat_location)
    strut_location_2 = spoiler_span / 2 * (1 + strut_lat_location)
    
    # calculating y-coordinate, area and weight at each increment i
    y_i = np.zeros(len(lift) + 1)
    y_ii = np.zeros(len(lift))
    area_i = np.zeros(len(lift))
    weight_i = np.zeros(len(lift))
    di = spoiler_span / len(lift)
    
    for i in range(len(lift) + 1):
        y_i[i] = round(i * di, 3)
    
    for i in range(len(lift)):
        y_ii[i] = y_i[i] + (y_i[i + 1] - y_i[i]) / 2
        area_i[i] = spoiler_chord * di
        weight_i[i] = -spoiler_weight / spoiler_area * area_i[i]  # force downward
    
    # adding the weight of the endplate to the first and last weight_i
    weight_i[0] += endplate_weight
    weight_i[-1] += endplate_weight
    
    # calculate the z-force on the strut by sum of forces in z
    f_strut_z = -(sum(lift) + sum(weight_i)) / 2
    
    # calculate the influence of the lift and weight on the bending moment for each increment i
    moment_lift_i = []
    moment_weight_i = []
    for i in range(len(lift) + 1):
        yset = y_i[i]
        momentL = sumz_moment(lift, y_ii, yset)
        momentW = sumz_moment(weight_i, y_ii, yset)
        moment_lift_i.append(momentL)
        moment_weight_i.append(momentW)
    
    # calculating the moment along strut in x
    moment_x_i = []
    for i in range(len(lift) + 1):
        yset = y_i[i]
        if yset >= strut_location_2 and yset >= strut_location_1:
            mom_i = f_strut_z * (yset - strut_location_2) + f_strut_z * (yset - strut_location_1) + moment_lift_i[i] + moment_weight_i[i]
            moment_x_i.append(mom_i)
        elif strut_location_2 > yset >= strut_location_1:
            mom_i = f_strut_z * (yset - strut_location_1) + moment_lift_i[i] + moment_weight_i[i]
            moment_x_i.append(mom_i)
        elif yset < strut_location_2 and yset < strut_location_1:
            mom_i = moment_lift_i[i] + moment_weight_i[i]
            moment_x_i.append(mom_i)
    
    # calculate deflection angles and displacement
    # the deflection angle in the centerline of the spoiler is 0
    # the deflection at the struts is considered equal to 0
    theta_i = np.zeros(len(lift) + 1)
    for i in range(int(len(lift) / 2) + 1, len(lift) + 1):
        theta_i[i] = theta_i[i - 1] + 0.5 * (moment_x_i[i] / (E * Ixx[i]) + moment_x_i[i - 1] / (E * Ixx[i - 1])) * (
                    y_i[i] - y_i[i - 1])
    
    index_strut = np.where(y_i == strut_location_2)[0][0]
    v_i = np.zeros(len(lift) + 1)
    for i in range(index_strut, len(lift) + 1):
        v_i[i] = v_i[i - 1] + 0.5 * (theta_i[i] + theta_i[i - 1]) * (y_i[i] - y_i[i - 1])
    
    for i in range(index_strut + 1, int(len(lift) / 2), -1):
        v_i[i - 1] = v_i[i] - 0.5 * (theta_i[i] + theta_i[i - 1]) * (y_i[i] - y_i[i - 1])
    
    for i in range(int(len(lift) / 2)):
        theta_i[i] = theta_i[len(lift) - i]
        v_i[i] = v_i[len(lift) - i]
        
    return theta_i, v_i, y_i, moment_x_i


# input parameters of the geometry
g = 9.80665
spoiler_weight = 20 * g
endplate_weight = 0.5 * g
spoiler_span = 2
spoiler_chord = 0.8
spoiler_area = 2.4
strut_lat_location = 0.9

# list with the lift force at each increment i
lift = -100 * np.ones(200)

# input sectional parameters
E = 70 * 10 ** 9
Ixx = 10 ** -6 * np.ones(len(lift) + 1)

theta_i, v_i, y_i, moment_x_i = mainplate_bending(lift, E, Ixx, spoiler_weight, endplate_weight, spoiler_span, spoiler_chord, spoiler_area, strut_lat_location)

# plotting
plt.figure()
plt.plot(y_i, theta_i)
plt.plot(y_i, v_i)
plt.grid()

plt.figure()
plt.plot(y_i, moment_x_i)
plt.grid()