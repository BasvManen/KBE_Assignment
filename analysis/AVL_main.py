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


class AvlAnalysis(avl.Interface):

    # INPUTS
    spoiler = Input()
    case_settings = Input()
    velocity = Input()
    density = Input()
    viscosity = Input(1.47e-5)

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
    def avl_main_plate_sections(self):
        """ This part retrieves the sections from the spoiler main plate and
        converts them into AVL sections, which are build from the section
        curvature. """
        return avl.SectionFromCurve(quantify=
                                    len(self.spoiler.main_plate.sections),
                                    curve_in=self.spoiler.main_plate.
                                    sections[child.index].curve
                                    )

    @Part
    def avl_main_plate(self):
        """ This part creates the AVL surface of the main plate. The surface
        is created from the AVL sections for the main plate. """
        return avl.Surface(name='Main Plate',
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.equal,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.equal,
                           y_duplicate=self.spoiler.position.point[1],
                           sections=self.avl_main_plate_sections,
                           angle=self.spoiler.spoiler_angle
                           )

    @Attribute
    def configuration(self):
        """ This attribute creates the configuration for the AVL analysis.
        The reference inputs are based on the main plate. """
        return avl.Configuration(name='Spoiler',
                                 reference_area=self.reference_area,
                                 reference_span=self.spoiler.spoiler_span,
                                 reference_chord=self.spoiler.spoiler_chord,
                                 reference_point=self.spoiler.position.point,
                                 surfaces=[self.avl_main_plate],
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
                   sin(radians(self.spoiler.spoiler_angle)))
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
        return [self.results[self.case_settings[0][0]]['StripForces']
                ['Main Plate']['Yle'],
                self.results[self.case_settings[0][0]]['StripForces']
                ['Main Plate']['c cl']]

    @Attribute
    def drag_distribution(self):
        """ This attribute returns the (total) drag distribution along the
        span. The first list contains the span-wise location, the second list
        contains the local (total) drag coefficient multiplied with the local
        chord. """
        return [self.results[self.case_settings[0][0]]['StripForces']
                ['Main Plate']['Yle'],
                np.multiply((self.results[self.case_settings[0][0]]
                            ['StripForces']['Main Plate']['cd'] +
                             self.parasite_drag_coefficient),
                self.results[self.case_settings[0][0]]['StripForces']
                ['Main Plate']['Chord'])]

    @action(label="Plot lift distribution")
    def lift_plot(self):
        """ This action retrieves the lift distribution from the attribute and
        returns a plot of the lift distribution along the span. The left side
        and the right side of the main plate are plotted separately. """
        # Original surface data
        x_1 = self.lift_distribution[0][:len(self.lift_distribution[0])//2]
        y_1 = self.lift_distribution[1][:len(self.lift_distribution[0])//2]

        # Mirrored surface data
        x_2 = self.lift_distribution[0][len(self.lift_distribution[0])//2:]
        y_2 = self.lift_distribution[1][len(self.lift_distribution[0])//2:]

        plt.figure()
        plt.plot(x_1, y_1, c="black")
        plt.plot(x_2, y_2, c="black")
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
        # Original surface data
        x_1 = self.drag_distribution[0][:len(self.drag_distribution[0])//2]
        y_1 = self.drag_distribution[1][:len(self.drag_distribution[0])//2]

        # Mirrored surface data
        x_2 = self.drag_distribution[0][len(self.drag_distribution[0])//2:]
        y_2 = self.drag_distribution[1][len(self.drag_distribution[0])//2:]

        plt.plot(x_1, y_1, c="black")
        plt.plot(x_2, y_2, c="black")
        # Total force coefficient visible in plot title
        plt.title("Total Drag Coefficient: " + str(self.c_d))
        # Axis labels
        plt.xlabel("Span-wise location [m]")
        plt.ylabel("Local drag coefficient")
        plt.show()


if __name__ == '__main__':
    from parapy.gui import display

    obj = Spoiler(spoiler_airfoils=["test", "naca6408", "naca6406"],
                  spoiler_span=1.6,
                  spoiler_chord=0.3,
                  spoiler_angle=10.,
                  strut_lat_location=0.6,
                  strut_thickness=0.01,
                  strut_height=0.25,
                  strut_chord_fraction=0.4,
                  strut_sweep=10.,
                  strut_cant=0.,
                  endplate_present=False,
                  endplate_thickness=0.05,
                  endplate_sweep=0.,
                  endplate_cant=0.,
                  strut_amount=3)

    cases = [('Incoming flow angle', {'alpha': 2})]

    analysis = AvlAnalysis(spoiler=obj,
                           velocity=10,
                           density=1.225,
                           case_settings=cases)
    display(analysis)