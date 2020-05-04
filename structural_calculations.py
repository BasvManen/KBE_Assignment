from math import tan, radians
from structural_methods import mainplate_bending_xz, bending_stress, \
    normal_stress_due_to_strut
from spoiler_files.assembly import Spoiler
from section_properties import SectionProperties
from weight_estimation import WeightEstimation
from AVL_main import AvlAnalysis
from parapy.geom import *
from parapy.core import *
import numpy as np
from matplotlib import pyplot as plt


class StructuralAnalysis(GeomBase):
    # MainPlate Inputs
    mid_airfoil = Input()
    tip_airfoil = Input()
    spoiler_span = Input()
    spoiler_chord = Input()
    spoiler_angle = Input()
    spoiler_skin_thickness = Input(0.001)  # this acts as an initial value

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
    maximum_velocity = Input()
    youngs_modulus = Input()
    material_density = Input()

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
                       strut_chord=self.strut_chord * 1000,
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
                       strut_chord=self.strut_chord,
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
            spoiler_geometry=self.spoiler_in_mm)
        return model.weight_mainplate, model.weight_endplate

    # Next the maximum lift and drag distributions are implemented. Note that
    # for this the cars maximum speed is used, together with a safety factor
    # of 1.5. For naming purposes, force_z and force_x are defined.
    @Attribute
    def get_distributed_forces(self):
        case = ['fixed aoa', {'alpha': 0}]
        analysis = AvlAnalysis(spoiler=self.spoiler_in_m,
                               case_settings=case,
                               velocity=self.maximum_velocity * 1.5)
        lift_distribution = []
        drag_distribution = []
        for i in range(int(len(analysis.lift_distribution[0]) / 2)):
            lift_distribution.append(-analysis.lift_distribution[1][i]
                                     * analysis.dyn_pressure
                                     * self.spoiler_in_m.reference_area)
            drag_distribution.append(analysis.drag_distribution[1][i]
                                     * analysis.dyn_pressure
                                     * self.spoiler_in_m.reference_area)
        lift_distribution = lift_distribution[::-1] + lift_distribution
        drag_distribution = drag_distribution[::-1] + drag_distribution
        return lift_distribution, drag_distribution

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

    # Retrieve the sectional properties for this discretisation
    @Attribute
    def moment_of_inertia(self):
        full_moment_of_inertia = SectionProperties(
            airfoil_mid=self.mid_airfoil,
            airfoil_tip=self.tip_airfoil,
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
            airfoil_mid=self.mid_airfoil,
            airfoil_tip=self.tip_airfoil,
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
        half_spoiler_coordinates = SectionProperties(
            airfoil_mid=self.mid_airfoil,
            airfoil_tip=self.tip_airfoil,
            spoiler_span=self.spoiler_span,
            spoiler_chord=self.spoiler_chord,
            spoiler_angle=self.spoiler_angle,
            spoiler_skin_thickness=self.spoiler_skin_thickness,
            n_cuts=self.number_of_lateral_cuts).coordinates_sections_points
        full_spoiler_coordinates = half_spoiler_coordinates[
                                   ::-1] + half_spoiler_coordinates[1:]
        half_centroid_list = SectionProperties(
            airfoil_mid=self.mid_airfoil,
            airfoil_tip=self.tip_airfoil,
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
        max_normal_stress_tensile = []
        max_normal_stress_compressive = []
        for i in range(len(self.normal_bending_stress[1])):
            max_normal_stress_tensile.append(self.normal_stress[i]
                                             + max(
                self.normal_bending_stress[0][i]))
            max_normal_stress_compressive.append(
                min(self.normal_bending_stress[0][i]))
        return max_normal_stress_tensile, max_normal_stress_compressive

    # @Attribute
    # def column_buckling(self):
    #     r_list = []
    #     for i in range(self.number_of_lateral_cuts - 1):
    #         r_list.append(self.moment_of_inertia[0][i + self.number_of_lateral_cuts]
    #                       / self.area_along_spoiler[i])
    #     r = min(r_list)
    #     le = self.spoiler_span
    #     sigma_cr = (np.pi ** 2 * self.youngs_modulus) / (le / r) ** 2
    #     return sigma_cr

    @Attribute
    def plot_stress(self):
        plt.plot(self.bending_xz[4], self.normal_stress)
        plt.plot(self.bending_xz[4], self.maximum_normal_stress[0])
        plt.plot(self.bending_xz[4], self.maximum_normal_stress[1])
        plt.xlabel('Spanwise location [m]')
        plt.ylabel('Stress [N/m^2]')
        plt.grid(b=True, which='both', color='0.65', linestyle='-')
        plt.legend(['Normal stress', 'Maximum tensile stress',
                    'Maximum compressive stress'])
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
    from inputs.read_inputs import *

    obj = StructuralAnalysis(label="Aerodynamic Bending",
                             material_density=material_density,
                             mid_airfoil='9404',
                             tip_airfoil='9402',
                             spoiler_span=spoiler_span / 1000,
                             spoiler_chord=spoiler_chord / 1000,
                             spoiler_angle=20,
                             strut_airfoil_shape=strut_airfoil_shape,
                             strut_lat_location=strut_lat_location,
                             strut_height=strut_height / 1000,
                             strut_chord=strut_chord / 1000,
                             strut_thickness=strut_thickness / 1000,
                             strut_sweep=strut_sweep,
                             strut_cant=strut_cant,
                             endplate_present=endplate_present,
                             endplate_thickness=endplate_thickness / 1000,
                             endplate_sweep=endplate_sweep,
                             endplate_cant=endplate_cant,
                             maximum_velocity=100.,
                             youngs_modulus=1.19 * 10 ** 9,
                             spoiler_skin_thickness=0.002)
    display(obj)
