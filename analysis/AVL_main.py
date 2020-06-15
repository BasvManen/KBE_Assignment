from analysis.spoiler_files import Spoiler
from parapy.core import *
from math import sin, radians

import kbeutils.avl as avl
import matplotlib.pyplot as plt
import numpy as np

###############################################################################
# AVL ANALYSIS CLASS                                                          #
# In this file, the AVL analysis is defined                                   #
#                                                                             #
# Inputs:                                                                     #
# - The spoiler geometry, as defined in the Spoiler class                     #
# - Case settings, list of cases that are investigated                        #
# - Velocity, car velocity at the moment of the aerodynamic analysis          #
# - Density, the air density at the moment of the aerodynamic analysis        #
# - (OPTIONAL) Viscosity, the viscosity of the fluid at the moment of the     #
#   aerodynamic analysis. Default is set to air.                              #
###############################################################################


def number_to_letter(integer):
    """ This function converts the quantify number of the main plate to a
    letter in the alphabet. This is done, because the name of an AVL
    surface cannot contain any digits. 0 converts to A, 1 to B etc. """

    alphabet = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K",
                "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
                "W", "X", "Y", "Z"]
    return alphabet[integer]


from analysis.avl_sections import AVLSections
from analysis.avl_surfaces import AVLSurfaces


class AvlAnalysis(avl.Interface):

    # INPUTS
    spoiler_input = Input()
    case_settings = Input()
    velocity = Input()
    density = Input()
    viscosity = Input(1.47e-5)

    @Part(in_tree=False)
    def spoiler(self):
        """ This part retrieves the input of the main file spoiler and creates
        an identical spoiler, but this time with dimensions in meters instead
        of dimensions in millimeters. """
        return Spoiler(spoiler_airfoils=self.spoiler_input.spoiler_airfoils,
                       spoiler_span=self.spoiler_input.spoiler_span/1000,
                       spoiler_chord=self.spoiler_input.spoiler_chord/1000,
                       spoiler_angle=self.spoiler_input.spoiler_angle,
                       plate_amount=self.spoiler_input.plate_amount,
                       plate_distance=self.spoiler_input.plate_distance,
                       strut_amount=self.spoiler_input.strut_amount,
                       strut_airfoil_shape=
                       self.spoiler_input.strut_airfoil_shape,
                       strut_lat_location=
                       self.spoiler_input.strut_lat_location,
                       strut_height=self.spoiler_input.strut_height/1000,
                       strut_chord_fraction=
                       self.spoiler_input.strut_chord_fraction,
                       strut_thickness=self.spoiler_input.strut_thickness/1000,
                       strut_sweep=self.spoiler_input.strut_sweep,
                       strut_cant=self.spoiler_input.strut_cant,
                       endplate_present=False,
                       endplate_thickness=
                       self.spoiler_input.endplate_thickness/1000,
                       endplate_sweep=self.spoiler_input.endplate_sweep,
                       endplate_cant=self.spoiler_input.endplate_cant,
                       car_length=self.spoiler_input.car_length/1000,
                       car_width=self.spoiler_input.car_width/1000,
                       car_maximum_height=
                       self.spoiler_input.car_maximum_height/1000,
                       car_middle_to_back_ratio=
                       self.spoiler_input.car_middle_to_back_ratio)

    @Attribute
    def reference_area(self):
        """ This attribute calculates the reference area of the spoiler. This
        is simply the area of the spoiler main plate. """
        return self.spoiler.spoiler_chord * self.spoiler.spoiler_span

    @Attribute
    def reynolds_number(self):
        """ This attribute calculates the Reynolds number based on the spoiler
        chord. Density, velocity and viscosity are defined as inputs. """
        return (self.density * self.velocity * self.spoiler.spoiler_chord /
                self.viscosity)

    @Attribute
    def dyn_pressure(self):
        """ This attribute calculated the dynamic pressure of the incoming
        flow. It is calculated using the input velocity and density. """
        return 0.5*self.density*self.velocity**2

    @Part
    def avl_sections(self):
        return AVLSections(quantify=self.spoiler.plate_amount,
                           sections=self.spoiler.main_plate
                           [child.index].sections)

    @Part
    def avl_surfaces(self):
        """ This part creates the AVL surface of the main plate. The surface
        is created from the AVL sections for the main plate. """
        return AVLSurfaces(quantify=self.spoiler.plate_amount,
                           number=child.index,
                           duplicate=self.spoiler.position.point[1],
                           sections=self.avl_sections
                           [child.index].plate_sections,
                           angle=self.spoiler.spoiler_angle)

    @Attribute
    def configuration(self):
        """ This attribute creates the configuration for the AVL analysis.
        The reference inputs are based on the main plate. """
        return avl.Configuration(name='Spoiler',
                                 reference_area=self.reference_area,
                                 reference_span=self.spoiler.spoiler_span,
                                 reference_chord=self.spoiler.spoiler_chord,
                                 reference_point=self.spoiler.position.point,
                                 surfaces=[plate.surface for plate
                                           in self.avl_surfaces],
                                 mach=0.0
                                 # Because of the low velocities, the flow is
                                 # assumed incompressible.
                                 )

    @Part
    def cases(self):
        """ This part retrieves the case input and converts it into an input
        that is given to AVL. The case is defined in a list, where the first
        entry is the name and the second entry is the case setting. Multiple
        cases can be appended in a list. """
        return avl.Case(quantify=len(self.case_settings),
                        name=self.case_settings[child.index][0],
                        settings=self.case_settings[child.index][1]
                        )

    @Attribute
    def total_force(self):
        """ This attribute calculates the total downforce produced by the
        spoiler, based on the resulting lift coefficient, the dynamic pressure
        and the reference area. """
        cl = self.results[self.case_settings[0][0]]['Totals']['CLtot']
        force = cl*self.dyn_pressure*self.reference_area
        return force

    @Attribute
    def c_l(self):
        """ This attribute returns the resulting lift coefficient. """
        return self.results[self.case_settings[0][0]]['Totals']['CLtot']

    @Attribute
    def parasite_drag_coefficient(self):
        """ This attribute calculates the parasite drag coefficient, based on
        a semi-empirical method introduced by Torenbeek in his book: Advanced
        Aircraft Design. The parasite drag is based on the wetted area, frontal
        area and the Reynolds number. """
        s_wet = self.spoiler.wetted_area
        s_front = (self.spoiler.spoiler_chord * self.spoiler.spoiler_span *
                   sin(radians(self.spoiler.spoiler_angle)) *
                   self.spoiler.plate_amount)
        phi = 1 + 5 * (s_front / s_wet)
        # Empirical method for the form factor
        cf = 0.455 / ((np.log10(self.reynolds_number))**2.58)
        # Empirical method for the friction coefficient
        cd = phi * cf * s_wet/self.spoiler.reference_area
        return cd

    @Attribute
    def c_d(self):
        """ This attribute returns the resulting drag coefficient. """
        return (self.results[self.case_settings[0][0]]['Totals']['CDind'] +
                self.parasite_drag_coefficient)

    @Attribute
    def ld_ratio(self):
        """ This attribute returns the downforce-over-drag ratio (or
        aerodynamic efficiency). """
        return self.c_l / self.c_d

    @Attribute
    def lift_distribution(self):
        """ This attribute returns the lift distribution along the span. The
        first list contains the span-wise location, the second list contains
        the local lift coefficient multiplied with the local chord. """
        y_pos = np.zeros((40, self.spoiler.plate_amount))
        lift = np.zeros((40, self.spoiler.plate_amount))
        for i in range(self.spoiler.plate_amount):
            y_pos[:, i] = np.array([self.results[self.case_settings[0][0]]
                                   ['StripForces'][number_to_letter(i)]
                                   ['Yle']])
            lift[:, i] = np.array([self.results[self.case_settings[0][0]]
                                  ['StripForces'][number_to_letter(i)]
                                  ['c cl']])
        return y_pos, lift

    @Attribute
    def drag_distribution(self):
        """ This attribute returns the (total) drag distribution along the
        span. The first list contains the span-wise location, the second list
        contains the local (total) drag coefficient multiplied with the local
        chord. """
        y_pos = np.zeros((40, self.spoiler.plate_amount))
        drag = np.zeros((40, self.spoiler.plate_amount))
        for i in range(self.spoiler.plate_amount):
            y_pos[:, i] = np.array([self.results[self.case_settings[0][0]]
                                    ['StripForces'][number_to_letter(i)]
                                    ['Yle']])
            drag[:, i] = (np.multiply(
                          np.array([self.results[self.case_settings[0][0]]
                                   ['StripForces'][number_to_letter(i)]
                                   ['cd']]),
                          np.array([self.results[self.case_settings[0][0]]
                                   ['StripForces'][number_to_letter(i)]
                                   ['Chord']])) +
                          self.parasite_drag_coefficient)
        return y_pos, drag

    @action(label="Plot lift distribution")
    def lift_plot(self):
        """ This action retrieves the lift distribution from the attribute and
        returns a plot of the lift distribution along the span. The left side
        and the right side of the main plate are plotted separately. """
        x1 = np.zeros((20, self.spoiler.plate_amount))
        x2 = np.zeros((20, self.spoiler.plate_amount))
        y1 = np.zeros((20, self.spoiler.plate_amount))
        y2 = np.zeros((20, self.spoiler.plate_amount))

        plt.figure()
        for i in range(self.spoiler.plate_amount):
            # Original surface data
            x1[:, i] = self.lift_distribution[0][:len(self.lift_distribution[0]
                                                      [:, i])//2, i]
            y1[:, i] = self.lift_distribution[1][:len(self.lift_distribution[1]
                                                      [:, i])//2, i]

            # Mirrored surface data
            x2[:, i] = self.lift_distribution[0][len(self.lift_distribution[0]
                                                     [:, i])//2:, i]
            y2[:, i] = self.lift_distribution[1][len(self.lift_distribution[1]
                                                     [:, i])//2:, i]

            plt.plot(x1[:, i], y1[:, i], c="black")
            plt.plot(x2[:, i], y2[:, i], c="black")

        # Total force coefficient visible in plot title
        plt.title("Total Downforce Coefficient: " + str(self.c_l))
        # Axis labels
        plt.xlabel("Span-wise location [m]")
        plt.ylabel("Local downforce coefficient")
        plt.show()

    @action(label="Plot drag distribution")
    def drag_plot(self):
        """ This action retrieves the (total) drag distribution from the
        attribute and returns a plot of the drag distribution along the span.
        THe left side and the right side of the main plate are plotted
        separately. """
        x1 = np.zeros((20, self.spoiler.plate_amount))
        x2 = np.zeros((20, self.spoiler.plate_amount))
        y1 = np.zeros((20, self.spoiler.plate_amount))
        y2 = np.zeros((20, self.spoiler.plate_amount))

        plt.figure()
        for i in range(self.spoiler.plate_amount):
            # Original surface data
            x1[:, i] = self.drag_distribution[0][:len(self.drag_distribution[0]
                                                      [:, i])//2, i]
            y1[:, i] = self.drag_distribution[1][:len(self.drag_distribution[1]
                                                      [:, i])//2, i]

            # Mirrored surface data
            x2[:, i] = self.drag_distribution[0][len(self.drag_distribution[0]
                                                     [:, i])//2:, i]
            y2[:, i] = self.drag_distribution[1][len(self.drag_distribution[1]
                                                     [:, i])//2:, i]

            plt.plot(x1[:, i], y1[:, i], c="black")
            plt.plot(x2[:, i], y2[:, i], c="black")

        # Total force coefficient visible in plot title
        plt.title("Total Drag Coefficient: " + str(self.c_d))
        # Axis labels
        plt.xlabel("Span-wise location [m]")
        plt.ylabel("Local drag coefficient")
        plt.show()
