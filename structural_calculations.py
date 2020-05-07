from math import tan, radians
from structural_methods import mainplate_bending_xz, bending_stress, \
    normal_stress_due_to_strut, max_shear_stress, buckling_modes, failure_modes
from spoiler_files.assembly import Spoiler
from section_properties import SectionProperties
from weight_estimation import WeightEstimation
from AVL_main import AvlAnalysis
from parapy.geom import *
from parapy.core import *
import numpy as np
from matplotlib import pyplot as plt


# STRUCTURAL ANALYSIS CLASS
# In this file, the structural analysis for the spoiler is performed


class StructuralAnalysis(GeomBase):
    # MainPlate Inputs
    mid_airfoil = Input()
    tip_airfoil = Input()
    spoiler_span = Input()
    spoiler_chord = Input()
    spoiler_angle = Input()
    spoiler_skin_thickness = Input(0.001)  # this acts as an initial value
    n_ribs = Input(0)

    # Strut Inputs
    strut_airfoil_shape = Input(False)
    strut_lat_location = Input()
    strut_height = Input()
    strut_chord_fraction = Input()
    strut_thickness = Input()
    strut_sweep = Input()
    strut_cant = Input()

    # Endplate Inputs
    endplate_present = Input(True)
    endplate_thickness = Input()
    endplate_sweep = Input()
    endplate_cant = Input()

    # Additional inputs for calculations
    maximum_velocity = Input()
    youngs_modulus = Input()
    yield_strength = Input()
    shear_strength = Input()
    material_density = Input()
    poisson_ratio = Input()

    # Add the spoiler geometry for several calculations in millimeter
    @Part(in_tree=False)
    def spoiler_in_mm(self):
        return Spoiler(label="Spoiler",
                       mid_airfoil=self.mid_airfoil,
                       tip_airfoil=self.tip_airfoil,
                       spoiler_span=self.spoiler_span * 1000,
                       spoiler_chord=self.spoiler_chord * 1000,
                       spoiler_angle=self.spoiler_angle,
                       strut_airfoil_shape=self.strut_airfoil_shape,
                       strut_lat_location=self.strut_lat_location,
                       strut_height=self.strut_height * 1000,
                       strut_chord_fraction=self.strut_chord_fraction,
                       strut_thickness=self.strut_thickness * 1000,
                       strut_sweep=self.strut_sweep,
                       strut_cant=self.strut_cant,
                       endplate_present=self.endplate_present,
                       endplate_thickness=self.endplate_thickness * 1000,
                       endplate_sweep=self.endplate_sweep,
                       endplate_cant=self.endplate_cant)

    # Add the spoiler geometry for several calculations in meter
    @Part(in_tree=False)
    def spoiler_in_m(self):
        return Spoiler(label="Spoiler",
                       mid_airfoil=self.mid_airfoil,
                       tip_airfoil=self.tip_airfoil,
                       spoiler_span=self.spoiler_span,
                       spoiler_chord=self.spoiler_chord,
                       spoiler_angle=self.spoiler_angle,
                       strut_airfoil_shape=self.strut_airfoil_shape,
                       strut_lat_location=self.strut_lat_location,
                       strut_height=self.strut_height,
                       strut_chord_fraction=self.strut_chord_fraction,
                       strut_thickness=self.strut_thickness,
                       strut_sweep=self.strut_sweep,
                       strut_cant=self.strut_cant,
                       endplate_present=False,
                       endplate_thickness=self.endplate_thickness,
                       endplate_sweep=self.endplate_sweep,
                       endplate_cant=self.endplate_cant)

    @Attribute
    def weights(self):
        # Here the weights of the parts are calculated as input for the
        # force distribution. Note that WeightEstimation asks for inputs of mm,
        # while Bending asks for inputs in meters.
        model = WeightEstimation(
            material_density=self.material_density,
            spoiler_skin_thickness=self.spoiler_skin_thickness * 1000,
            ribs_area=self.area_of_ribs,
            spoiler_geometry=self.spoiler_in_mm)
        return model.weight_mainplate, model.weight_endplate, \
               model.weight_strut, model.weight_ribs, model.total_weight

    # Next the maximum lift and drag distributions are implemented. Note that
    # for this the cars maximum speed is used, together with a safety factor
    # of 1.5. For naming purposes, force_z and force_x are defined.
    @Attribute
    def get_distributed_forces(self):
        safety_factor = 1.5
        case = [('fixed aoa', {'alpha': 0})]
        analysis = AvlAnalysis(spoiler=self.spoiler_in_m,
                               case_settings=case,
                               velocity=self.maximum_velocity * safety_factor)
        lift_distribution = []
        drag_distribution = []
        spacing = self.spoiler_in_m.spoiler_span / len(analysis.
                                                       lift_distribution[0])
        for i in range(int(len(analysis.lift_distribution[0]) / 2)):
            lift_distribution.append(-analysis.lift_distribution[1][i]
                                     * analysis.dyn_pressure
                                     * spacing)
            drag_distribution.append(analysis.drag_distribution[1][i]
                                     * analysis.dyn_pressure
                                     * spacing)
        lift_distribution = lift_distribution[::-1] + lift_distribution
        drag_distribution = drag_distribution[::-1] + drag_distribution
        y_distribution = sorted(analysis.lift_distribution[0])
        return lift_distribution, drag_distribution, y_distribution

    @Attribute
    def force_y_location(self):
        return self.get_distributed_forces[2]

    @Attribute
    def force_z(self):
        return self.get_distributed_forces[0]

    @Attribute
    def force_x(self):
        return self.get_distributed_forces[1]

    # Discretise the spoiler along the span
    @Attribute
    def number_of_lateral_cuts(self):
        return int(len(self.force_z) / 2) + 1

    # Get the area of the ribs for the weight estimation
    @Attribute
    def area_of_ribs(self):
        ribs_area = SectionProperties(
            airfoil_mid=self.mid_airfoil,
            airfoil_tip=self.tip_airfoil,
            spoiler_span=self.spoiler_span,
            spoiler_chord=self.spoiler_chord,
            spoiler_angle=self.spoiler_angle,
            spoiler_skin_thickness=self.spoiler_skin_thickness,
            n_cuts=self.number_of_lateral_cuts,
            n_ribs=self.n_ribs).ribs_area
        return ribs_area

    # Retrieve the moment of inertia for this discretisation
    @Attribute
    def moment_of_inertia(self):
        full_moment_of_inertia = SectionProperties(
            airfoil_mid=self.mid_airfoil,
            airfoil_tip=self.tip_airfoil,
            spoiler_span=self.spoiler_span,
            spoiler_chord=self.spoiler_chord,
            spoiler_angle=self.spoiler_angle,
            spoiler_skin_thickness=self.spoiler_skin_thickness,
            n_cuts=self.number_of_lateral_cuts,
            n_ribs=self.n_ribs).full_moment_of_inertia

        moment_of_inertia_x = [row[0] for row in full_moment_of_inertia]
        moment_of_inertia_z = [row[1] for row in full_moment_of_inertia]
        moment_of_inertia_xz = [row[2] for row in full_moment_of_inertia]
        return moment_of_inertia_x, moment_of_inertia_z, moment_of_inertia_xz

    # Retrieve the area along the spoiler for this discretisation
    @Attribute
    def area_along_spoiler(self):
        return SectionProperties(
            airfoil_mid=self.mid_airfoil,
            airfoil_tip=self.tip_airfoil,
            spoiler_span=self.spoiler_span,
            spoiler_chord=self.spoiler_chord,
            spoiler_angle=self.spoiler_angle,
            spoiler_skin_thickness=self.spoiler_skin_thickness,
            n_cuts=self.number_of_lateral_cuts,
            n_ribs=self.n_ribs).area_along_spoiler

    # Retrieve the coordinates of the centroid for this discretisation
    @Attribute
    def centroid_coordinates(self):
        half_centroid_list = SectionProperties(
            airfoil_mid=self.mid_airfoil,
            airfoil_tip=self.tip_airfoil,
            spoiler_span=self.spoiler_span,
            spoiler_chord=self.spoiler_chord,
            spoiler_angle=self.spoiler_angle,
            spoiler_skin_thickness=self.spoiler_skin_thickness,
            n_cuts=self.number_of_lateral_cuts,
            n_ribs=self.n_ribs).centroid
        full_centroid_list = half_centroid_list[
                             ::-1] + half_centroid_list[1:]
        return full_centroid_list

    # Retrieve the coordinates along each of the discretised cutouts along
    # the spoiler span
    @Attribute
    def cutout_coordinates(self):
        half_spoiler_coordinates = SectionProperties(
            airfoil_mid=self.mid_airfoil,
            airfoil_tip=self.tip_airfoil,
            spoiler_span=self.spoiler_span,
            spoiler_chord=self.spoiler_chord,
            spoiler_angle=self.spoiler_angle,
            spoiler_skin_thickness=self.spoiler_skin_thickness,
            n_cuts=self.number_of_lateral_cuts,
            n_ribs=self.n_ribs).coordinates_sections_points
        full_spoiler_coordinates = half_spoiler_coordinates[
                                   ::-1] + half_spoiler_coordinates[1:]
        return full_spoiler_coordinates

    # Calculate the bending moments and deflections in x and z.
    @Attribute
    def bending_xz(self):
        theta_x_i, theta_z_i, w_i, u_i, y_i, moment_x_i, moment_z_i, \
        f_strut_z, f_strut_x = mainplate_bending_xz(
            self.force_z, self.force_x,
            self.youngs_modulus,
            self.moment_of_inertia[0],
            self.moment_of_inertia[1],
            self.moment_of_inertia[2],
            self.weights[0],
            self.weights[1],
            self.spoiler_span, self.spoiler_chord,
            self.strut_lat_location)
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
        cutout_coordinates = self.cutout_coordinates
        centroid_coordinates = self.centroid_coordinates

        sigma_y, sigma_y_max = bending_stress(moment_x, moment_z, moi_xx,
                                              moi_zz, moi_xz,
                                              cutout_coordinates,
                                              centroid_coordinates)
        return sigma_y, sigma_y_max

    # Calculate the maximum tensile and compressive stress along the spoiler
    # and convert it to MPa
    @Attribute
    def maximum_normal_stress(self):
        max_normal_stress_tensile = []
        max_normal_stress_compressive = []
        for i in range(len(self.normal_bending_stress[0])):
            max_normal_stress_tensile.append((self.normal_stress[i]
                                              + max(
                        self.normal_bending_stress[0][i])) / 10 ** 6)
            max_normal_stress_compressive.append((self.normal_stress[i]
                                                  + min(
                        self.normal_bending_stress[0][i])) / 10 ** 6)
        return max_normal_stress_tensile, max_normal_stress_compressive

    # Calculate the shear stress along the spoiler and convert to MPa
    @Attribute
    def maximum_shear_stress(self):
        force_x = self.get_distributed_forces[0]
        force_z = self.get_distributed_forces[1]
        moi_xx = self.moment_of_inertia[0]
        moi_zz = self.moment_of_inertia[1]
        moi_xz = self.moment_of_inertia[2]
        cutout_coordinates = self.cutout_coordinates
        centroid_coordinates = self.centroid_coordinates

        tau = max_shear_stress(force_x, force_z, self.spoiler_skin_thickness,
                               moi_xx, moi_zz, moi_xz, cutout_coordinates,
                               centroid_coordinates)

        # convert to MPa
        for i in range(len(tau)):
            tau[i] = tau[i] / 10 ** 6

        return tau

    # Calculate the critical values for buckling failure modes
    @Attribute
    def critical_buckling_values(self):
        buckling_values = buckling_modes(self.n_ribs, self.spoiler_span,
                                         self.spoiler_chord,
                                         self.spoiler_skin_thickness,
                                         self.moment_of_inertia[0],
                                         self.moment_of_inertia[1],
                                         self.area_along_spoiler,
                                         self.youngs_modulus,
                                         self.poisson_ratio)
        sigma_crit = buckling_values[0]
        tau_crit = buckling_values[1]
        sigma_column_crit = buckling_values[2]
        return sigma_crit, tau_crit, sigma_column_crit

    # Determine whether the spoiler fails or not
    @Attribute
    def failure(self):
        occurred_failure = failure_modes(max(self.maximum_normal_stress[0]),
                                         abs(min(
                                             self.maximum_normal_stress[1])),
                                         max([max(self.maximum_shear_stress),
                                              abs(min(
                                                  self.maximum_shear_stress))]),
                                         max([max(self.bending_xz[2]),
                                              abs(min(self.bending_xz[2]))]),
                                         self.critical_buckling_values[0],
                                         self.critical_buckling_values[1],
                                         self.critical_buckling_values[2],
                                         self.spoiler_span,
                                         self.yield_strength,
                                         self.shear_strength)
        due_to_other_modes = occurred_failure[0]
        due_to_ribs = occurred_failure[1]
        return due_to_other_modes, due_to_ribs

    # Creating several actions to plot parameters along the spoiler
    @action(label="Plot the normal stress along the spoiler")
    def plot_normal_stress(self):
        # plt.plot(self.bending_xz[4], self.normal_stress)
        plt.plot(self.bending_xz[4], self.maximum_normal_stress[0])
        plt.plot(self.bending_xz[4], self.maximum_normal_stress[1])
        plt.xlabel('Spanwise location [m]')
        plt.ylabel('Normal stress [MPa]')
        plt.grid(b=True, which='both', color='0.65', linestyle='-')
        plt.legend(['Maximum tensile stress', 'Maximum compressive stress'])
        plt.title("Close it to refresh the ParaPy GUI")
        plt.show()

    @action(label="Plot the shear stress along the spoiler")
    def plot_shear_stress(self):
        plt.plot(self.get_distributed_forces[2], self.maximum_shear_stress)
        plt.xlabel('Spanwise location [m]')
        plt.ylabel('Shear stress [MPa]')
        plt.grid(b=True, which='both', color='0.65', linestyle='-')
        plt.title("Close it to refresh the ParaPy GUI")
        plt.show()

    @action(label="Plot the deflection of the spoiler")
    def plot_force_deflection(self):
        plt.plot(self.bending_xz[4], self.bending_xz[2])
        plt.plot(self.bending_xz[4], self.bending_xz[3])
        plt.xlabel('Spanwise location [m]')
        plt.ylabel('Deflection [m]')
        plt.grid(b=True, which='both', color='0.65', linestyle='-')
        plt.title("Close it to refresh the ParaPy GUI")
        plt.legend(['Deflection in z', 'Deflection in x'])
        plt.show()

    @action(label="Plot the bending moment along the spoiler")
    def plot_bending_moment(self):
        plt.plot(self.bending_xz[4], self.bending_xz[5])
        plt.plot(self.bending_xz[4], self.bending_xz[6])
        plt.xlabel('Spanwise location [m]')
        plt.ylabel('Bending moment [Nm]')
        plt.grid(b=True, which='both', color='0.65', linestyle='-')
        plt.title("Close it to refresh the ParaPy GUI")
        plt.legend(['Moment about x', 'Moment about z'])
        plt.show()


if __name__ == '__main__':
    from parapy.gui import display

    thickness = 0.001
    n_ribs = 1
    calc_normal_stress = 300.
    calc_shear_stress = 0.
    deflection = 0.
    yield_strength = 3000.
    shear_strength = 34.
    span = 2.5
    density = 1440.
    youngs_modulus = 70 * 10 ** 9
    poisson_ratio = 0.36
    failure = True

    while failure:
        print(thickness)
        obj = StructuralAnalysis(label="Aerodynamic Bending",
                                 material_density=density,
                                 mid_airfoil='9404',
                                 tip_airfoil='9402',
                                 spoiler_span=span,
                                 spoiler_chord=0.3,
                                 spoiler_angle=10.,
                                 strut_airfoil_shape=False,
                                 strut_lat_location=0.65,
                                 strut_height=0.25,
                                 strut_chord_fraction=0.6,
                                 strut_thickness=0.01,
                                 strut_sweep=10.1,
                                 strut_cant=0.,
                                 endplate_present=True,
                                 endplate_thickness=0.01,
                                 endplate_sweep=15.,
                                 endplate_cant=10.,
                                 maximum_velocity=60.,
                                 youngs_modulus=youngs_modulus,
                                 yield_strength=yield_strength,
                                 shear_strength=shear_strength,
                                 spoiler_skin_thickness=thickness,
                                 n_ribs=n_ribs,
                                 poisson_ratio=poisson_ratio)
        failure = obj.failure[0]
        failure_due_to_ribs = obj.failure[1]
        if failure_due_to_ribs:
            n_ribs += 1
        elif failure:
            thickness += 0.001

    print(n_ribs)
    print(obj.weights)

    # obj = StructuralAnalysis(label="Aerodynamic Bending",
    #                          material_density=1600.,
    #                          mid_airfoil='9404',
    #                          tip_airfoil='9402',
    #                          spoiler_span=2.5,
    #                          spoiler_chord=0.3,
    #                          spoiler_angle=10.,
    #                          strut_airfoil_shape=False,
    #                          strut_lat_location=0.4,
    #                          strut_height=0.2,
    #                          strut_chord_fraction=0.6,
    #                          strut_thickness=0.01,
    #                          strut_sweep=10.,
    #                          strut_cant=10.,
    #                          endplate_present=False,
    #                          endplate_thickness=0.01,
    #                          endplate_sweep=15.,
    #                          endplate_cant=10.,
    #                          maximum_velocity=60.,
    #                          youngs_modulus=1.19 * 10 ** 9,
    #                          spoiler_skin_thickness=0.01)
    display(obj)
