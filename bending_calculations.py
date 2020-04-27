from math import tan, radians
from section_properties import SectionProperties
from weight_estimation import WeightEstimation
from parapy.geom import *
from parapy.core import *
import numpy as np
from matplotlib import pyplot as plt

g = 9.80665


def sumz_moment(force_list, y_i, y_current):
    """
    This function is used in the calculation of the moment due to the
    distributed lift/weight/drag force of the spoiler as used in
    mainplate_bending_xz below. It uses a distributed
    force (force_list), the y-positions of that distributed force (y_i) and
    a current y location (y_current)
    """

    moment_list = []
    for i in range(len(force_list)):
        if y_i[i] < y_current:
            outcome = force_list[i] * (y_current - y_i[i])
        else:
            outcome = 0
        moment_list.append(outcome)
    return sum(moment_list)


def mainplate_bending_xz(lift, drag, E, Ixx, Izz, Ixz, spoiler_weight,
                         endplate_weight, spoiler_span, spoiler_chord,
                         spoiler_area, strut_lat_location):
    """
    This function calculates the bending moment along the spoiler in x and
    z, as well as the bending displacement in x and z. It uses as inputs the
    aerodynamic forces on the spoiler, the material and sectional properties
    of the spoiler and the geometric properties of the spoiler.
    """

    # retrieve y-location of the struts
    strut_location_1 = spoiler_span / 2 * (1 - strut_lat_location)
    strut_location_2 = spoiler_span / 2 * (1 + strut_lat_location)

    # calculating y-coordinate, area and weight at each increment i. the
    # weight distribution is approximated by separate weight forces along
    # the spoiler, which are appropriate to the area of the spoiler at each i.
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
        weight_i[i] = -spoiler_weight * g / spoiler_area * area_i[i]

    # adding the weight of the endplate to the first and last weight_i
    weight_i[0] += endplate_weight * g
    weight_i[-1] += endplate_weight * g

    # calculate the z-force on the strut by sum of forces in z
    f_strut_z = -(sum(lift) + sum(weight_i)) / 2
    # calculate the z-force on the strut by sum of forces in x
    f_strut_x = -sum(drag) / 2

    # calculate the influence of the lift and weight on the bending moment
    # for each increment i
    moment_lift_i = []
    moment_weight_i = []
    moment_drag_i = []
    for i in range(len(lift) + 1):
        yset = y_i[i]
        momentL = sumz_moment(lift, y_ii, yset)
        momentW = sumz_moment(weight_i, y_ii, yset)
        momentD = sumz_moment(drag, y_ii, yset)
        moment_lift_i.append(momentL)
        moment_weight_i.append(momentW)
        moment_drag_i.append(momentD)

    # calculating the moment in x along the spoiler
    moment_x_i = []
    for i in range(len(lift) + 1):
        yset = y_i[i]
        if yset >= strut_location_2 and yset >= strut_location_1:
            mom_i = f_strut_z * (yset - strut_location_2) + f_strut_z \
                    * (yset - strut_location_1) \
                    + moment_lift_i[i] + moment_weight_i[i]
            moment_x_i.append(mom_i)
        elif strut_location_2 > yset >= strut_location_1:
            mom_i = f_strut_z * (yset - strut_location_1) + moment_lift_i[i] \
                    + moment_weight_i[i]
            moment_x_i.append(mom_i)
        elif yset < strut_location_2 and yset < strut_location_1:
            mom_i = moment_lift_i[i] + moment_weight_i[i]
            moment_x_i.append(mom_i)

    # calculating the moment in z along the spoiler
    moment_z_i = []
    for i in range(len(drag) + 1):
        yset = y_i[i]
        if yset >= strut_location_2 and yset >= strut_location_1:
            mom_i = f_strut_x * (yset - strut_location_2) + f_strut_x \
                    * (yset - strut_location_1) + moment_drag_i[i]
            moment_z_i.append(mom_i)
        elif strut_location_2 > yset >= strut_location_1:
            mom_i = f_strut_x * (yset - strut_location_1) + moment_drag_i[i]
            moment_z_i.append(mom_i)
        elif yset < strut_location_2 and yset < strut_location_1:
            mom_i = moment_drag_i[i]
            moment_z_i.append(mom_i)

    # Calculate deflection angles and displacement using Euler-Bernoulli
    # beam theory in unsymmetrical bending. The deflection angle (theta) in the
    # centerline of the spoiler is 0. The deflections at the struts are
    # considered equal to 0. Deflections in z are described by w,
    # and deflections in x are described by u.
    w_double_prime = np.zeros(len(lift) + 1)
    u_double_prime = np.zeros(len(drag) + 1)
    theta_x_i = np.zeros(len(lift) + 1)
    theta_z_i = np.zeros(len(drag) + 1)
    for i in range(len(lift) + 1):
        w_double_prime[i] = (moment_z_i[i] * Ixz[i] / (E * Ixx[i] * Izz[i])
                             - moment_x_i[i] / (E * Ixx[i])) \
                            / (1 - Ixz[i] ** 2 / (Ixx[i] * Izz[i]))
        u_double_prime[i] = (moment_x_i[i] * Ixz[i] / (E * Ixx[i] * Izz[i])
                             - moment_z_i[i] / (E * Izz[i])) \
                            / (1 - Ixz[i] ** 2 / (Ixx[i] * Izz[i]))

    for i in range(int(len(lift) / 2) + 1, len(lift) + 1):
        theta_x_i[i] = theta_x_i[i - 1] + 0.5 * (
                -w_double_prime[i] - w_double_prime[i - 1]) * (
                               y_i[i] - y_i[i - 1])
        theta_z_i[i] = theta_z_i[i - 1] + 0.5 * (
                -u_double_prime[i] - u_double_prime[i - 1]) * (
                               y_i[i] - y_i[i - 1])

    index_strut = np.where(y_i == strut_location_2)[0][0]
    w_i = np.zeros(len(lift) + 1)
    u_i = np.zeros(len(lift) + 1)
    for i in range(index_strut, len(lift) + 1):
        w_i[i] = w_i[i - 1] + 0.5 * (theta_x_i[i] + theta_x_i[i - 1]) * (
                y_i[i] - y_i[i - 1])
        u_i[i] = u_i[i - 1] + 0.5 * (theta_z_i[i] + theta_z_i[i - 1]) * (
                y_i[i] - y_i[i - 1])

    for i in range(index_strut + 1, int(len(lift) / 2), -1):
        w_i[i - 1] = w_i[i] - 0.5 * (theta_x_i[i] + theta_x_i[i - 1]) * (
                y_i[i] - y_i[i - 1])
        u_i[i - 1] = u_i[i] - 0.5 * (theta_z_i[i] + theta_z_i[i - 1]) * (
                y_i[i] - y_i[i - 1])

    for i in range(int(len(lift) / 2)):
        theta_x_i[i] = theta_x_i[len(lift) - i]
        theta_z_i[i] = theta_z_i[len(lift) - i]
        w_i[i] = w_i[len(lift) - i]
        u_i[i] = u_i[len(lift) - i]

    return theta_x_i, theta_z_i, w_i, u_i, y_i, moment_x_i, moment_z_i, \
           f_strut_z, f_strut_x


def normal_stress_due_to_strut(force_in_y, y_i, area_distribution,
                               strut_lat_location, spoiler_span):
    """
    Function which calculates the normal stress along the spoiler, due to
    the normal force which is present due to the cant angle of the struts.
    """

    # retrieve y-location of the struts
    strut_location_1 = spoiler_span / 2 * (1 - strut_lat_location)
    strut_location_2 = spoiler_span / 2 * (1 + strut_lat_location)

    # make normal force distribution
    normal_force = np.zeros(len(y_i))
    for i in range(len(y_i)):
        if y_i[i] < strut_location_1 or y_i[i] > strut_location_2:
            normal_force[i] = 0
        elif strut_location_1 <= y_i[i] <= strut_location_2:
            normal_force[i] = force_in_y

    # make normal stress distribution
    sigma_y = []
    for i in range(len(y_i)):
        sigma_y.append(normal_force[i] / area_distribution[i])

    return sigma_y


def bending_stress(moment_x, moment_z, Ixx, Izz, Ixz, line_coordinates,
                   centroid_list):
    """
    Function which calculates the normal stress along the spoiler due to the
    bending moment along the spoiler. It returns an array of the normal
    bending stress along the spoiler, as well as the maximum stress along
    the spoiler.
    """

    # initialise the x and z coordinates along the span
    x = []
    z = []
    for i in range(len(line_coordinates)):
        x.append([])
        z.append([])
        for j in range(len(line_coordinates[0])):
            x[i].append(line_coordinates[i][j][0])
            z[i].append(line_coordinates[i][j][2])

    # x and z coordinates of the centroid
    x_centroid = []
    z_centroid = []
    for i in range(len(centroid_list)):
        x_centroid.append(centroid_list[i][0])
        z_centroid.append(centroid_list[i][2])

    # calculate the normal stress due to bending
    sigma_y = []
    sigma_y_max = []
    for i in range(len(line_coordinates)):
        sigma_y.append([])
        for j in range(len(line_coordinates[i])):
            calc_sigma = moment_x[i] \
                         * (Izz[i] * (z[i][j] - z_centroid[i])
                            - Ixz[i] * (x[i][j] - x_centroid[i])) \
                         / (Ixx[i] * Izz[i] - Ixz[i] ** 2) \
                         + moment_z[i] \
                         * (Ixx[i] * (x[i][j] - x_centroid[i])
                            - Ixz[i] * (z[i][j] - z_centroid[i])) \
                         / (Ixx[i] * Izz[i] - Ixz[i] ** 2)
            sigma_y[i].append(calc_sigma)
        sigma_y_max.append(max(sigma_y[i])
                           if abs(max(sigma_y[i])) > abs(min(sigma_y[i]))
                           else min(sigma_y[i]))

    return sigma_y, sigma_y_max


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
        # Here the weights of the parts are calculated as input for the
        # force distribution. Note that WeightEstimation asks for inputs of mm,
        # while Bending asks for inputs in meters.
        model = WeightEstimation(
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

    # Discretise the spoiler along the span
    @Attribute
    def number_of_lateral_cuts(self):
        return int(len(self.force_z) / 2) + 1

    # Retrieve the sectional properties for this discretisation
    @Attribute
    def moment_of_inertia(self):
        full_moment_of_inertia = SectionProperties(
            airfoil_mid=self.airfoil_mid,
            airfoil_tip=self.airfoil_tip,
            spoiler_span=self.spoiler_span,
            spoiler_chord=self.spoiler_chord,
            spoiler_angle=self.spoiler_angle,
            spoiler_skin_thickness=self.spoiler_skin_thickness,
            n_cuts=self.number_of_lateral_cuts).full_moment_of_inertia

        moment_of_inertia_x = [row[0] for row in full_moment_of_inertia]
        moment_of_inertia_z = [row[1] for row in full_moment_of_inertia]
        moment_of_inertia_xz = [row[2] for row in full_moment_of_inertia]
        return moment_of_inertia_x, moment_of_inertia_z, moment_of_inertia_xz

    @Attribute
    def area_along_spoiler(self):
        return SectionProperties(
            airfoil_mid=self.airfoil_mid,
            airfoil_tip=self.airfoil_tip,
            spoiler_span=self.spoiler_span,
            spoiler_chord=self.spoiler_chord,
            spoiler_angle=self.spoiler_angle,
            spoiler_skin_thickness=self.spoiler_skin_thickness,
            n_cuts=self.number_of_lateral_cuts).area_along_spoiler

    # Calculate the bending moments and deflections in x and z.
    @Attribute
    def bending_xz(self):
        theta_x_i, theta_z_i, w_i, u_i, y_i, moment_x_i, moment_z_i, \
        f_strut_z, f_strut_x = mainplate_bending_xz(
            self.force_z, self.force_x,
            self.youngs_modulus,
            self.moment_of_inertia[0],
            self.moment_of_inertia[1],
            self.moment_of_inertia[2], self.weights[0],
            self.weights[1],
            self.spoiler_span, self.spoiler_chord,
            self.spoiler_area, self.strut_lat_location)
        return theta_x_i, theta_z_i, w_i, u_i, y_i, moment_x_i, moment_z_i, \
               f_strut_z, f_strut_x

    # Calculate the normal stress in the spoiler, from the normal force and
    # the bending moment.
    @Attribute
    def normal_stress(self):
        f_strut_y = self.bending_xz[7] * tan(radians(self.strut_cant))
        y_i = self.bending_xz[4]
        total_area_distribution = self.area_along_spoiler[::-1] \
                                  + self.area_along_spoiler[1:]
        sigma_y = normal_stress_due_to_strut(f_strut_y,
                                             y_i,
                                             total_area_distribution,
                                             self.strut_lat_location,
                                             self.spoiler_span)
        return sigma_y

    @Attribute
    def normal_bending_stress(self):
        moment_x = self.bending_xz[5]
        moment_z = self.bending_xz[6]
        moi_xx = self.moment_of_inertia[0]
        moi_zz = self.moment_of_inertia[1]
        moi_xz = self.moment_of_inertia[2]
        half_spoiler_coordinates = SectionProperties(
            airfoil_mid=self.airfoil_mid,
            airfoil_tip=self.airfoil_tip,
            spoiler_span=self.spoiler_span,
            spoiler_chord=self.spoiler_chord,
            spoiler_angle=self.spoiler_angle,
            spoiler_skin_thickness=self.spoiler_skin_thickness,
            n_cuts=self.number_of_lateral_cuts).coordinates_sections_points
        full_spoiler_coordinates = half_spoiler_coordinates[
                                   ::-1] + half_spoiler_coordinates[1:]
        half_centroid_list = SectionProperties(
            airfoil_mid=self.airfoil_mid,
            airfoil_tip=self.airfoil_tip,
            spoiler_span=self.spoiler_span,
            spoiler_chord=self.spoiler_chord,
            spoiler_angle=self.spoiler_angle,
            spoiler_skin_thickness=self.spoiler_skin_thickness,
            n_cuts=self.number_of_lateral_cuts).centroid
        full_centroid_list = half_centroid_list[
                             ::-1] + half_centroid_list[1:]

        sigma_y, sigma_y_max = bending_stress(moment_x, moment_z, moi_xx,
                                              moi_zz, moi_xz,
                                              full_spoiler_coordinates,
                                              full_centroid_list)
        return sigma_y, sigma_y_max

    @Attribute
    def maximum_normal_stress(self):
        max_normal_stress = []
        for i in range(len(self.normal_bending_stress[1])):
            max_normal_stress.append(self.normal_stress[i]
                                     + self.normal_bending_stress[1][i])
        return max_normal_stress

    @Attribute
    def plot_stress(self):
        plt.plot(self.bending_xz[4], self.normal_stress)
        plt.plot(self.bending_xz[4], self.normal_bending_stress[1])
        plt.plot(self.bending_xz[4], self.maximum_normal_stress)
        plt.xlabel('Spanwise location [m]')
        plt.ylabel('Stress [N/m^2]')
        plt.grid(b=True, which='both', color='0.65', linestyle='-')
        plt.title("Close it to refresh the ParaPy GUI")
        plt.show()
        return "Plot generated and closed"

    @Attribute
    def plot_force_deflection(self):
        plt.plot(self.bending_xz[4], self.bending_xz[2])
        plt.plot(self.bending_xz[4], self.bending_xz[3])
        plt.xlabel('Spanwise location [m]')
        plt.ylabel('Deflection [m]')
        plt.grid(b=True, which='both', color='0.65', linestyle='-')
        plt.title("Close it to refresh the ParaPy GUI")
        plt.legend(['Deflection in z', 'Deflection in x'])
        plt.show()
        return "Plot generated and closed"

    @Attribute
    def plot_bending_moment(self):
        plt.plot(self.bending_xz[4], self.bending_xz[5])
        plt.plot(self.bending_xz[4], self.bending_xz[6])
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
                  spoiler_angle=15.,
                  strut_airfoil_shape=True,
                  strut_lat_location=0.2,
                  strut_height=.25,
                  strut_chord=.4,
                  strut_thickness=.04,
                  strut_sweep=15.,
                  strut_cant=20.,
                  endplate_present=True,
                  endplate_thickness=.005,
                  endplate_sweep=15.,
                  endplate_cant=10.,
                  spoiler_area=2000000.,
                  force_z=-100 * np.ones(40),
                  force_x=10 * np.ones(40),
                  youngs_modulus=6.89 * 10 ** 7)
    display(obj)
