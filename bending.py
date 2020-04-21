from math import pi, sin, cos, tan, radians
from moment_of_inertia import MomentOfInertia
from parapy.geom import *
from parapy.core import *
import numpy as np
from matplotlib import pyplot as plt


# function to calculate moment due to a distributed force (list1),
# for a spatial list (y_i) set at some spatial value (elementset)
def sumz_moment(list1, y_i, elementset):
    list2 = []
    for i in range(len(list1)):
        if y_i[i] < elementset:
            outcome = list1[i] * (elementset - y_i[i])
        else:
            outcome = 0
        list2.append(outcome)
    return sum(list2)


# function to calculate moments/displacement of the main spoiler plate using as inputs the aerodynamic force on the
# spoiler, the material and sectional properties of the spoiler and the geometric properties of the spoiler design
def mainplate_bending(lift, E, Ixx, spoiler_weight, endplate_weight, spoiler_span, spoiler_chord, spoiler_area,
                      strut_lat_location):
    # retrieve y-location of the struts
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

    # calculating the moment in x along the spoiler
    moment_x_i = []
    for i in range(len(lift) + 1):
        yset = y_i[i]
        if yset >= strut_location_2 and yset >= strut_location_1:
            mom_i = f_strut_z * (yset - strut_location_2) + f_strut_z * (yset - strut_location_1) + \
                    moment_lift_i[i] + moment_weight_i[i]
            moment_x_i.append(mom_i)
        elif strut_location_2 > yset >= strut_location_1:
            mom_i = f_strut_z * (yset - strut_location_1) + moment_lift_i[i] + moment_weight_i[i]
            moment_x_i.append(mom_i)
        elif yset < strut_location_2 and yset < strut_location_1:
            mom_i = moment_lift_i[i] + moment_weight_i[i]
            moment_x_i.append(mom_i)

    # calculate deflection angles and displacement using Euler-Bernoulli beam theory
    # the deflection angle in the centerline of the spoiler is 0
    # the deflection at the struts is considered equal to 0
    theta_i = np.zeros(len(lift) + 1)
    for i in range(int(len(lift) / 2) + 1, len(lift) + 1):
        theta_i[i] = theta_i[i - 1] + 0.5 * (
                moment_x_i[i] / (E * Ixx[i]) + moment_x_i[i - 1] / (E * Ixx[i - 1])) * (
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


class Bending(GeomBase):

    # Inputs for moment of inertia calculations
    airfoil_mid = Input()
    airfoil_tip = Input()
    spoiler_span = Input()
    spoiler_chord = Input()
    spoiler_angle = Input()
    spoiler_skin_thickness = Input()

    # Additional inputs for bending calculations
    spoiler_weight = Input()
    endplate_weight = Input()
    spoiler_area = Input()
    strut_lat_location = Input()
    lift = Input()
    E = Input()

    @Attribute
    def number_of_lateral_cuts(self):
        return int(len(self.lift)/2) + 1

    @Attribute
    def full_moment_of_inertia(self):
        return MomentOfInertia(airfoil_mid=self.airfoil_mid,
                               airfoil_tip=self.airfoil_tip,
                               spoiler_span=self.spoiler_span,
                               spoiler_chord=self.spoiler_chord,
                               spoiler_angle=self.spoiler_angle,
                               spoiler_skin_thickness=self.spoiler_skin_thickness,
                               n_cuts=self.number_of_lateral_cuts).full_moment_of_inertia

    @Attribute
    def x_moment_of_inertia(self):
        return [row[0] for row in self.full_moment_of_inertia]

    @Attribute
    def bending_output(self):
        theta_i, w_i, y_i, moment_x_i = mainplate_bending(self.lift, self.E, self.x_moment_of_inertia,
                                                          self.spoiler_weight, self.endplate_weight, self.spoiler_span,
                                                          self.spoiler_chord, self.spoiler_area,
                                                          self.strut_lat_location)
        return theta_i, w_i, y_i, moment_x_i

    @Attribute
    def plot_w_deflection(self):
        plt.plot(self.bending_output[2], self.bending_output[3])
        plt.xlabel('Spanwise location [m]')
        plt.ylabel('Deflection in z [m]')
        plt.grid(b=True, which='both', color='0.65', linestyle='-')
        plt.title("Close it to refresh the ParaPy GUI")
        plt.show()
        return "Plot generated and closed"


if __name__ == '__main__':
    from parapy.gui import display
    obj = Bending(label="Spoiler",
                  airfoil_mid='9412',
                  airfoil_tip='9408',
                  spoiler_span=3.,
                  spoiler_chord=0.8,
                  spoiler_angle=20.,
                  spoiler_skin_thickness=0.002,
                  spoiler_weight=200,
                  endplate_weight=50,
                  spoiler_area=2.4,
                  strut_lat_location=0.7,
                  lift=-100*np.ones(40),
                  E=6.89*10**7)
    display(obj)
