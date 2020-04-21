from math import pi, sin, cos, tan, radians
from section_properties import SectionProperties
from weight_estimation import WeightEstimation
from parapy.geom import *
from parapy.core import *
import numpy as np
from matplotlib import pyplot as plt

g = 9.80665


# this function is used in the calculation of the moment due to the distributed lift/weight/drag force of the spoiler
# as used in mainplate_bending_x and mainplate_bending_z below. it uses a distributed force (force_list), the
# y-positions of that distributed force (y_i) and a current y location (y_current)
def sumz_moment(force_list, y_i, y_current):
    moment_list = []
    for i in range(len(force_list)):
        if y_i[i] < y_current:
            outcome = force_list[i] * (y_current - y_i[i])
        else:
            outcome = 0
        moment_list.append(outcome)
    return sum(moment_list)


# function to calculate moments/displacement of the main spoiler plate using as inputs the aerodynamic force in z on the
# spoiler, the material and sectional properties of the spoiler and the geometric properties of the spoiler design
def mainplate_bending_x(lift, E, Ixx, spoiler_weight, endplate_weight, spoiler_span, spoiler_chord, spoiler_area,
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
        weight_i[i] = -spoiler_weight * g / spoiler_area * area_i[i]  # force downward

    # adding the weight of the endplate to the first and last weight_i
    weight_i[0] += endplate_weight * g
    weight_i[-1] += endplate_weight * g

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


# function to calculate moments/displacement of the main spoiler plate using as inputs the aerodynamic force in x on the
# spoiler, the material and sectional properties of the spoiler and the geometric properties of the spoiler design
def mainplate_bending_z(drag, E, Izz, spoiler_span, strut_lat_location):
    # retrieve y-location of the struts
    strut_location_1 = spoiler_span / 2 * (1 - strut_lat_location)
    strut_location_2 = spoiler_span / 2 * (1 + strut_lat_location)

    # calculating y-coordinate, area and weight at each increment i
    y_i = np.zeros(len(drag) + 1)
    y_ii = np.zeros(len(drag))
    di = spoiler_span / len(drag)

    for i in range(len(drag) + 1):
        y_i[i] = round(i * di, 3)  # this was done to get rid of weird machine errors

    for i in range(len(drag)):
        y_ii[i] = y_i[i] + (y_i[i + 1] - y_i[i]) / 2

    # calculate the z-force on the strut by sum of forces in z
    f_strut_x = -sum(drag) / 2

    # calculate the influence of the drag and weight on the bending moment for each increment i
    moment_drag_i = []
    for i in range(len(drag) + 1):
        yset = y_i[i]
        momentD = sumz_moment(drag, y_ii, yset)
        moment_drag_i.append(momentD)

    # calculating the moment in x along the spoiler
    moment_z_i = []
    for i in range(len(drag) + 1):
        yset = y_i[i]
        if yset >= strut_location_2 and yset >= strut_location_1:
            mom_i = f_strut_x * (yset - strut_location_2) + f_strut_x * (yset - strut_location_1) + \
                    moment_drag_i[i]
            moment_z_i.append(mom_i)
        elif strut_location_2 > yset >= strut_location_1:
            mom_i = f_strut_x * (yset - strut_location_1) + moment_drag_i[i]
            moment_z_i.append(mom_i)
        elif yset < strut_location_2 and yset < strut_location_1:
            mom_i = moment_drag_i[i]
            moment_z_i.append(mom_i)

    # calculate deflection angles and displacement using Euler-Bernoulli beam theory
    # the deflection angle in the centerline of the spoiler is 0
    # the deflection at the struts is considered equal to 0
    theta_i = np.zeros(len(drag) + 1)
    for i in range(int(len(drag) / 2) + 1, len(drag) + 1):
        theta_i[i] = theta_i[i - 1] + 0.5 * (
                moment_z_i[i] / (E * Izz[i]) + moment_z_i[i - 1] / (E * Izz[i - 1])) * (
                             y_i[i] - y_i[i - 1])

    index_strut = np.where(y_i == strut_location_2)[0][0]
    v_i = np.zeros(len(drag) + 1)
    for i in range(index_strut, len(drag) + 1):
        v_i[i] = v_i[i - 1] + 0.5 * (theta_i[i] + theta_i[i - 1]) * (y_i[i] - y_i[i - 1])

    for i in range(index_strut + 1, int(len(drag) / 2), -1):
        v_i[i - 1] = v_i[i] - 0.5 * (theta_i[i] + theta_i[i - 1]) * (y_i[i] - y_i[i - 1])

    for i in range(int(len(drag) / 2)):
        theta_i[i] = theta_i[len(drag) - i]
        v_i[i] = v_i[len(drag) - i]

    return theta_i, v_i, y_i, moment_z_i


class Bending(GeomBase):
    # MainPlate Inputs
    airfoil_mid = Input()
    airfoil_tip = Input()
    spoiler_span = Input()
    spoiler_chord = Input()
    spoiler_angle = Input()
    spoiler_skin_thickness = Input()

    # Strut Inputs
    strut_airfoil_shape = Input(False)
    strut_lat_location = Input()
    strut_height = Input()
    strut_chord = Input()
    strut_thickness = Input()
    strut_sweep = Input()
    strut_cant = Input()

    # Endplate Inputs
    endplate_present = Input(True)
    endplate_thickness = Input()
    endplate_sweep = Input()
    endplate_cant = Input()

    # Additional inputs for bending calculations
    spoiler_area = Input()
    force_z = Input()
    force_x = Input()
    youngs_modulus = Input()
    material_density = Input()

    @Attribute
    def weights(self):
        model = WeightEstimation(label="Weight Estimator",
                                 material_density=self.material_density,
                                 mid_airfoil=self.airfoil_mid,
                                 tip_airfoil=self.airfoil_tip,
                                 spoiler_span=self.spoiler_span * 1000,
                                 spoiler_chord=self.spoiler_chord * 1000,
                                 spoiler_skin_thickness=self.spoiler_skin_thickness * 1000,
                                 spoiler_angle=self.spoiler_angle,
                                 strut_airfoil_shape=self.strut_airfoil_shape,
                                 strut_lat_location=self.strut_lat_location,
                                 strut_height=self.strut_height * 1000,
                                 strut_chord=self.strut_chord * 1000,
                                 strut_thickness=self.strut_thickness * 1000,
                                 strut_sweep=self.strut_sweep,
                                 strut_cant=self.strut_cant,
                                 endplate_present=self.endplate_present,
                                 endplate_thickness=self.endplate_thickness * 1000,
                                 endplate_sweep=self.endplate_sweep,
                                 endplate_cant=self.endplate_cant)
        return model.weight_mainplate, model.weight_endplate

    @Attribute
    def number_of_lateral_cuts(self):
        return int(len(self.force_z) / 2) + 1

    @Attribute
    def full_moment_of_inertia(self):
        return SectionProperties(airfoil_mid=self.airfoil_mid,
                                 airfoil_tip=self.airfoil_tip,
                                 spoiler_span=self.spoiler_span,
                                 spoiler_chord=self.spoiler_chord,
                                 spoiler_angle=self.spoiler_angle,
                                 spoiler_skin_thickness=self.spoiler_skin_thickness,
                                 n_cuts=self.number_of_lateral_cuts).full_moment_of_inertia

    @Attribute
    def moment_of_inertia(self):
        moment_of_inertia_x = [row[0] for row in self.full_moment_of_inertia]
        moment_of_inertia_z = [row[1] for row in self.full_moment_of_inertia]
        moment_of_inertia_xz = [row[2] for row in self.full_moment_of_inertia]
        return moment_of_inertia_x, moment_of_inertia_z, moment_of_inertia_xz

    @Attribute
    def bending_x(self):
        theta_i, delta_i, y_i, moment_i = mainplate_bending_x(self.force_z, self.youngs_modulus,
                                                              self.moment_of_inertia[0],
                                                              self.weights[0], self.weights[1],
                                                              self.spoiler_span, self.spoiler_chord, self.spoiler_area,
                                                              self.strut_lat_location)
        return theta_i, delta_i, y_i, moment_i

    @Attribute
    def bending_z(self):
        theta_i, delta_i, y_i, moment_i = mainplate_bending_z(self.force_x, self.youngs_modulus,
                                                              self.moment_of_inertia[1],
                                                              self.spoiler_span, self.strut_lat_location)
        return theta_i, delta_i, y_i, moment_i

    @Attribute
    def plot_force_deflection(self):
        plt.plot(self.bending_x[2], self.bending_x[1])
        plt.plot(self.bending_z[2], self.bending_z[1])
        plt.xlabel('Spanwise location [m]')
        plt.ylabel('Deflection [m]')
        plt.grid(b=True, which='both', color='0.65', linestyle='-')
        plt.title("Close it to refresh the ParaPy GUI")
        plt.legend(['Deflection in z', 'Deflection in x'])
        plt.show()
        return "Plot generated and closed"

    @Attribute
    def plot_bending_moment(self):
        plt.plot(self.bending_x[2], self.bending_x[3])
        plt.plot(self.bending_z[2], self.bending_z[3])
        plt.xlabel('Spanwise location [m]')
        plt.ylabel('Bending moment [Nm]')
        plt.grid(b=True, which='both', color='0.65', linestyle='-')
        plt.title("Close it to refresh the ParaPy GUI")
        plt.legend(['Moment about x', 'Moment about z'])
        plt.show()
        return "Plot generated and closed"


if __name__ == '__main__':
    from parapy.gui import display

    obj = Bending(label="Aerodynamic Bending",
                  material_density=1600.,
                  airfoil_mid='9412',
                  airfoil_tip='9408',
                  spoiler_span=2.5,
                  spoiler_chord=.8,
                  spoiler_skin_thickness=.002,
                  spoiler_angle=20.,
                  strut_airfoil_shape=True,
                  strut_lat_location=0.8,
                  strut_height=.25,
                  strut_chord=.4,
                  strut_thickness=.04,
                  strut_sweep=15.,
                  strut_cant=15.,
                  endplate_present=True,
                  endplate_thickness=.005,
                  endplate_sweep=15.,
                  endplate_cant=10.,
                  spoiler_area=2000000.,
                  force_z=-100 * np.ones(40),
                  force_x=-100 * np.ones(40),
                  youngs_modulus=6.89 * 10 ** 7)
    display(obj)
