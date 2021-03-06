from analysis.structural_methods import mainplate_bending_xz, bending_stress, \
    normal_stress_due_to_strut, max_shear_stress, buckling_modes, failure_modes
from analysis.spoiler_files.assembly import Spoiler
from analysis.section_properties import SectionProperties
from analysis.weight_estimation import WeightEstimation
from analysis.AVL_main import AvlAnalysis
from parapy.geom import *
from parapy.core import *
from math import tan, radians
from matplotlib import pyplot as plt

import numpy as np


# Import and define the pop-up warnings
def generate_warning(warning_header, msg):
    from tkinter import Tk, mainloop, X, messagebox

    # initialization
    window = Tk()
    window.withdraw()

    # generates message box
    messagebox.showwarning(warning_header, msg)


###############################################################################
# STRUCTURAL ANALYSIS CLASS                                                   #
# In this file, the structural analysis for the spoiler is performed          #
#                                                                             #
# Inputs:                                                                     #
# - The same inputs as for the Spoiler class, these inputs are specified      #
#   under MainPlate, Strut and Endplate inputs. For more information,         #
#   check assembly.py                                                         #
# - The skin thickness of the spoiler                                         #
# - The number of ribs in the spoiler, excluding the 2 ribs at the            #
#   two sides of the main plate.                                              #
# - The maximum velocity of the car, to simulate the worst case scenario      #
#   that the spoiler has to withstand.                                        #
# - The air density at the moment of the aerodynamic analysis.                #
# - Young's modulus of the used material.                                     #
# - Yield strength of the used material.                                      #
# - Shear strength of the used material.                                      #
# - Density of the used material.                                             #
# - Poisson ratio of the used material.                                       #
###############################################################################


class StructuralAnalysis(GeomBase):
    # MainPlate Inputs
    spoiler_airfoils = Input()
    spoiler_span = Input()
    spoiler_chord = Input()
    spoiler_angle = Input()
    plate_amount = Input()
    plate_distance = Input()

    # Strut Inputs
    strut_amount = Input()
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

    # Car Inputs
    car_length = Input()
    car_width = Input()
    car_maximum_height = Input()
    car_middle_to_back_ratio = Input()

    # Additional inputs for calculations
    spoiler_skin_thickness = Input(0.001)
    n_ribs = Input(0)
    maximum_velocity = Input()
    air_density = Input()
    youngs_modulus = Input()
    yield_strength = Input()
    shear_strength = Input()
    material_density = Input()
    poisson_ratio = Input()

    @Part(in_tree=False)
    def spoiler_in_mm(self):
        """ Create the spoiler assembly part in millimeters. This instance
        is used for the weights estimation, the AVL analysis and the
        creation of the thick structural main plate. """
        return Spoiler(label="Spoiler in mm",
                       spoiler_airfoils=self.spoiler_airfoils,
                       spoiler_span=self.spoiler_span * 1000,
                       spoiler_chord=self.spoiler_chord * 1000,
                       spoiler_angle=self.spoiler_angle,
                       plate_amount=self.plate_amount,
                       plate_distance=self.plate_distance,
                       strut_amount=self.strut_amount,
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
                       endplate_cant=self.endplate_cant,
                       car_length=self.car_length * 1000,
                       car_width=self.car_width * 1000,
                       car_maximum_height=self.car_maximum_height * 1000,
                       car_middle_to_back_ratio=self.car_middle_to_back_ratio)

    @Part
    def weight_estimation(self):
        """ This part instance retrieves the WeightEstimation class. Note that
        the input of the spoiler geometry should be defined in mm in this
        class. """
        return WeightEstimation(material_density=self.material_density,
                                spoiler_skin_thickness=
                                self.spoiler_skin_thickness * 1000,
                                ribs_area=self.area_of_ribs,
                                spoiler_geometry=self.spoiler_in_mm,
                                strut_amount=self.strut_amount)

    @Attribute
    def weights(self):
        """ This attribute calculates the weights of each of the components,
        as well as the total weight of the spoiler. """
        weight = self.weight_estimation
        return weight.weight_mainplate, weight.weight_endplate, \
               weight.weight_strut, weight.weight_ribs, weight.total_weight

    @Attribute
    def get_distributed_forces(self):
        """ This attribute calculates the lift and drag distributions from
        AvlAnalysis, for the inputted maximum velocity that the spoiler has
        to withstand. It also outputs distribution of y locations at which
        these forces are applied. Note that it also uses a slight safety
        factor of 1.25 on this maximum velocity. """
        # Define the safety factor and the case for the AVL analysis
        safety_factor = 1.25
        case = [('AoA input',
                 {'alpha': self.spoiler_in_mm.car_model.avl_angle})]
        # Perform the aerodynamic analysis
        analysis = AvlAnalysis(spoiler_input=self.spoiler_in_mm,
                               case_settings=case,
                               velocity=self.maximum_velocity * safety_factor,
                               density=self.air_density)

        # The outputted data is defined in a slightly off format. This
        # section places the lift, drag and y-distribution in a format to
        # comply with the rest of the class.
        spacing = self.spoiler_span / len(
            analysis.lift_distribution[0])
        lift_distribution = []
        drag_distribution = []
        y_distribution = []
        i_crit = np.argmax(analysis.lift_distribution[1][0])
        for i in range(int(len(analysis.lift_distribution[0]) / 2)):
            lift_distribution.append(-analysis.lift_distribution[1][i][i_crit]
                                     * analysis.dyn_pressure
                                     * spacing)
            drag_distribution.append(analysis.drag_distribution[1][i][i_crit]
                                     * analysis.dyn_pressure
                                     * spacing)
        for i in range(len(analysis.lift_distribution[0])):
            y_distribution.append(analysis.lift_distribution[0][i][i_crit])
        lift_distribution = lift_distribution[::-1] + lift_distribution
        drag_distribution = drag_distribution[::-1] + drag_distribution
        y_distribution = sorted(y_distribution)
        return lift_distribution, drag_distribution, y_distribution

    @Attribute
    def force_y_location(self):
        """ This attribute renames the y_distribution from
        get_distributed_forces. """
        return self.get_distributed_forces[2]

    @Attribute
    def force_z(self):
        """ This attribute renames the lift_distribution from
            get_distributed_forces. """
        return self.get_distributed_forces[0]

    @Attribute
    def force_x(self):
        """ This attribute renames the drag_distribution from
                get_distributed_forces. """
        return self.get_distributed_forces[1]

    @Attribute
    def number_of_lateral_cuts(self):
        """ This attribute defines the discretisation along the half span of
        the spoiler, based on the lift distribution on the spoiler. """
        return int(len(self.force_z) / 2) + 1

    @Part
    def sectional_properties(self):
        """ This part instance retrieves SectionalProperties class. """
        return SectionProperties(airfoils=self.spoiler_airfoils,
                                 spoiler_span=self.spoiler_span,
                                 spoiler_chord=self.spoiler_chord,
                                 spoiler_angle=self.spoiler_angle,
                                 spoiler_skin_thickness=
                                 self.spoiler_skin_thickness,
                                 n_cuts=self.number_of_lateral_cuts,
                                 n_ribs=self.n_ribs)

    @Attribute
    def area_of_ribs(self):
        """ This attribute retrieves the area of each of the ribs of the
        spoiler, from SectionProperties. It is used for the weight estimation
        of the ribs. """
        ribs_area = self.sectional_properties.ribs_area
        return ribs_area

    @Attribute
    def moment_of_inertia(self):
        """ This attribute retrieves the moments of inertia (Ixx, Izz and
        Ixz) along the entire spoiler, from SectionProperties. """
        full_moment_of_inertia = \
            self.sectional_properties.full_moment_of_inertia

        moment_of_inertia_x = [row[0] for row in full_moment_of_inertia]
        moment_of_inertia_z = [row[1] for row in full_moment_of_inertia]
        moment_of_inertia_xz = [row[2] for row in full_moment_of_inertia]
        return moment_of_inertia_x, moment_of_inertia_z, moment_of_inertia_xz

    @Attribute
    def area_along_spoiler(self):
        """ This attribute retrieves the cross sectional area along the
        spoiler, from the discretisation defined in number_of_lateral_cuts. """
        areas = self.sectional_properties.area_along_spoiler
        return areas

    @Attribute
    def centroid_coordinates(self):
        """ This attribute retrieves the centroid's location along the
        spoiler, for the discretisation defined in number_of_lateral_cuts. """
        half_centroid_list = self.sectional_properties.centroid
        full_centroid_list = half_centroid_list[
                             ::-1] + half_centroid_list[1:]
        return full_centroid_list

    @Attribute
    def cutout_coordinates(self):
        """ This attribute retrieves the coordinates of the cutouts along the
        spoiler, for the discretisation defined in number_of_lateral_cuts. """
        half_spoiler_coordinates = \
            self.sectional_properties.coordinates_sections_points
        full_spoiler_coordinates = half_spoiler_coordinates[
                                   ::-1] + half_spoiler_coordinates[1:]
        return full_spoiler_coordinates

    @Attribute
    def bending_xz(self):
        """ This attribute uses the mainplate_bending_xz as described in
        structural_methods.py. It returns the bending deflection,
        the bending deflection angle and the bending moment along the
        spoiler (in x and z). It also returns the x and z forces on the
        struts. """
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
            self.strut_lat_location,
            self.strut_amount)
        return theta_x_i, theta_z_i, w_i, u_i, y_i, moment_x_i, moment_z_i, \
               f_strut_z, f_strut_x

    @Attribute
    def normal_stress(self):
        """ This attribute calculates the normal stress along the spoiler,
        due to the normal force the struts exert on the spoiler. """
        f_strut_y = self.bending_xz[7] * tan(radians(self.strut_cant))
        y_i = self.bending_xz[4]
        total_area_distribution = self.area_along_spoiler[::-1] \
                                  + self.area_along_spoiler[1:]
        sigma_y = normal_stress_due_to_strut(f_strut_y,
                                             y_i,
                                             total_area_distribution,
                                             self.strut_lat_location,
                                             self.spoiler_span,
                                             self.strut_amount)
        return sigma_y

    @Attribute
    def normal_bending_stress(self):
        """ This attribute calculates the normal stress along the spoiler,
        due to the bending moments along the spoiler. It returns the bending
        stress along each of the cutout, along the whole spoiler, as well as
        the maximum compressive and tensile stresses along the spoiler. """
        # Initialise inputs
        moment_x = self.bending_xz[5]
        moment_z = self.bending_xz[6]
        moi_xx = self.moment_of_inertia[0]
        moi_zz = self.moment_of_inertia[1]
        moi_xz = self.moment_of_inertia[2]
        cutout_coordinates = self.cutout_coordinates
        centroid_coordinates = self.centroid_coordinates

        # Use bending_stress() method
        sigma_y, sigma_y_max = bending_stress(moment_x, moment_z, moi_xx,
                                              moi_zz, moi_xz,
                                              cutout_coordinates,
                                              centroid_coordinates)
        return sigma_y, sigma_y_max

    @Attribute
    def maximum_normal_stress(self):
        """ This attribute calculates the total maximum tensile and
        compressive stress along the spoiler, and it returns these values in
        MPa. """
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

    @Attribute
    def maximum_shear_stress(self):
        """ This attribute calculates the maximum shear stress along the
        spoiler, and returns it in MPa. """
        # Initialise inputs
        force_x = self.get_distributed_forces[0]
        force_z = self.get_distributed_forces[1]
        moi_xx = self.moment_of_inertia[0]
        moi_zz = self.moment_of_inertia[1]
        moi_xz = self.moment_of_inertia[2]
        cutout_coordinates = self.cutout_coordinates
        centroid_coordinates = self.centroid_coordinates

        # Use max_shear_stress() method
        tau = max_shear_stress(force_x, force_z, self.spoiler_skin_thickness,
                               moi_xx, moi_zz, moi_xz, cutout_coordinates,
                               centroid_coordinates)
        # Convert to MPa
        for i in range(len(tau)):
            tau[i] = tau[i] / 10 ** 6
        return tau

    @Attribute
    def critical_buckling_values(self):
        """ This attribute calculates all different critical buckling values
        for the spoiler geometry. It returns the critical normal buckling
        stress, shear buckling stress and column buckling stress by using
        the buckling_modes() method. """
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
        """ This attribute determines whether the spoiler can withstand the
        forces and stresses, or it fails. It returns several lists of bools,
        determining due to which failure mode the spoiler will fail. """
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
        due_to_which_mode = occurred_failure[2]
        return due_to_other_modes, due_to_ribs, due_to_which_mode

    @Part
    def structural_mainplate(self):
        """ This part returns a thick main plate instance, representing the
        resulting main plate with its skin thickness. """
        return SewnSolid(quantify=2,
                         built_from=self.weight_estimation.thick_mainplate
                         if child.index == 0
                         else self.weight_estimation.thick_mainplate_mirror,
                         mesh_deflection=1e-5)

    @Part
    def structural_ribs(self):
        """ This part returns the various ribs instances, representing the
        resulting calculated ribs with the same thickness as the thick main
        plate. Note that this instance is created in mm. """
        return SewnSolid(quantify=self.n_ribs + 2,
                         built_from=SectionProperties(
                             airfoils=self.spoiler_airfoils,
                             spoiler_span=self.spoiler_span * 1000,
                             spoiler_chord=self.spoiler_chord * 1000,
                             spoiler_angle=self.spoiler_angle,
                             spoiler_skin_thickness=
                             self.spoiler_skin_thickness * 1000,
                             n_cuts=self.number_of_lateral_cuts,
                             n_ribs=self.n_ribs).ribs_total[child.index],
                         mesh_deflection=1e-5)

    @action(label="Plot the normal stress along the spoiler")
    def plot_normal_stress(self):
        """ This action plots the maximum tensile and compressive normal
        stresses along the spoiler span. It also includes several pop-up
        warnings if the maximum stresses exceed the critical failure mode
        values. """

        # Define the warnings
        if self.failure[2][0]:
            msg = "Stress is too high: spoiler will yield."
            header = "WARNING"
            generate_warning(header, msg)
        if self.failure[2][1]:
            msg = "Stress is too high: spoiler will buckle."
            header = "WARNING"
            generate_warning(header, msg)
        if self.failure[2][5]:
            msg = "Stress is too high: column buckling will occur."
            header = "WARNING"
            generate_warning(header, msg)

        # Plot the normal stress
        plt.plot(self.bending_xz[4], self.maximum_normal_stress[0])
        plt.plot(self.bending_xz[4], self.maximum_normal_stress[1])
        plt.xlabel('Spanwise location [m]')
        plt.ylabel('Normal stress [MPa]')
        plt.grid(b=True, which='both', color='0.65', linestyle='-')
        plt.legend(['Maximum tensile stress', 'Maximum compressive stress'])
        plt.title("Skin thickness = "
                  + str(self.spoiler_skin_thickness * 1000) + 'mm')
        plt.show()

    @action(label="Plot the shear stress along the spoiler")
    def plot_shear_stress(self):
        """ This action plots the maximum shear stresses along the spoiler
        span. It also includes several pop-up warnings if the maximum
        stresses exceed the critical failure mode values. """

        # Define the warnings
        if self.failure[2][2]:
            msg = "Stress is too high: shear yielding will occur."
            header = "WARNING"
            generate_warning(header, msg)
        if self.failure[2][3]:
            msg = "Stress is too high: shear buckling will occur."
            header = "WARNING"
            generate_warning(header, msg)

        # Plot the shear stress
        plt.plot(self.get_distributed_forces[2], self.maximum_shear_stress)
        plt.xlabel('Spanwise location [m]')
        plt.ylabel('Shear stress [MPa]')
        plt.grid(b=True, which='both', color='0.65', linestyle='-')
        plt.title("Skin thickness = "
                  + str(self.spoiler_skin_thickness * 1000) + 'mm')
        plt.show()

    @action(label="Plot the deflection of the spoiler")
    def plot_force_deflection(self):
        """ This action plots the maximum deflections (in x and z) along the
        spoiler span. It also includes a pop-up warnings if the
        maximum deflection exceeds 5% of the spoiler half-span. """

        # Define the warning
        if self.failure[2][4]:
            msg = "Deflection is too high: deflection is higher than criteria."
            header = "WARNING"
            generate_warning(header, msg)

        # Plot the deflection
        plt.plot(self.bending_xz[4], self.bending_xz[2])
        plt.plot(self.bending_xz[4], self.bending_xz[3])
        plt.xlabel('Spanwise location [m]')
        plt.ylabel('Deflection [m]')
        plt.grid(b=True, which='both', color='0.65', linestyle='-')
        plt.title("Skin thickness = "
                  + str(self.spoiler_skin_thickness * 1000) + 'mm')
        plt.legend(['Deflection in z', 'Deflection in x'])
        plt.show()

    @action(label="Plot the bending moment along the spoiler")
    def plot_bending_moment(self):
        """ This action plots the maximum bending moments (in x and z) along
        the spoiler span. """
        plt.plot(self.bending_xz[4], self.bending_xz[5])
        plt.plot(self.bending_xz[4], self.bending_xz[6])
        plt.xlabel('Spanwise location [m]')
        plt.ylabel('Bending moment [Nm]')
        plt.grid(b=True, which='both', color='0.65', linestyle='-')
        plt.title("Skin thickness = "
                  + str(self.spoiler_skin_thickness * 1000) + 'mm')
        plt.legend(['Moment about x', 'Moment about z'])
        plt.show()
