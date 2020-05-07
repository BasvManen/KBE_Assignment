from spoiler_files import Spoiler
from parapy.core import *

import kbeutils.avl as avl
import matplotlib.pyplot as plt
import numpy as np

# AVL ANALYSIS CLASS
# In this file, the AVL analysis is defined


class AvlAnalysis(avl.Interface):

    # INPUTS
    spoiler = Input(in_tree=True)
    case_settings = Input()
    velocity = Input()
    density = Input()

    # Extract the AVL configuration from the assembly class
    @Attribute
    def configuration(self):
        return self.spoiler.avl_configuration

    # Define the cases given as input
    @Part
    def cases(self):
        return avl.Case(quantify=len(self.case_settings),
                        name=self.case_settings[child.index][0],
                        settings=self.case_settings[child.index][1])

    # Calculate the dynamic pressure from the velocity
    @Attribute
    def dyn_pressure(self):
        return 0.5*self.density*self.velocity**2

    # Calculate the total force based on the AVL results and dynamic pressure
    @Attribute
    def total_force(self):
        cl = self.results[self.case_settings[0][0]]['Totals']['CLtot']
        force = cl*self.dyn_pressure*self.spoiler.reference_area
        return force

    # Calculate the aerodynamic efficiency from the AVL results
    @Attribute
    def ld_ratio(self):
        return self.results[self.case_settings[0][0]]['Totals']['CLtot'] \
               / self.results[self.case_settings[0][0]]['Totals']['CDtot']

    # Save the lift distribution from the AVL results
    @Attribute
    def lift_distribution(self):
        return [self.results[self.case_settings[0][0]]['StripForces']
                ['Main Plate']['Yle'],
                self.results[self.case_settings[0][0]]['StripForces']
                ['Main Plate']['c cl']]

    # Save the drag distribution from the AVL results
    @Attribute
    def drag_distribution(self):
        return [self.results[self.case_settings[0][0]]['StripForces']
                ['Main Plate']['Yle'],
                np.multiply(self.results[self.case_settings[0][0]]
                            ['StripForces']['Main Plate']['cd'],
                self.results[self.case_settings[0][0]]['StripForces']
                ['Main Plate']['Chord'])]

    # Generate a lift distribution plot from the AVL results
    @Attribute
    def lift_plot(self):
        # Original surface data
        x_1 = self.lift_distribution[0][:len(self.lift_distribution[0])//2]
        y_1 = self.lift_distribution[1][:len(self.lift_distribution[0])//2]

        # Mirrored surface data
        x_2 = self.lift_distribution[0][len(self.lift_distribution[0])//2:]
        y_2 = self.lift_distribution[1][len(self.lift_distribution[0])//2:]

        plt.plot(x_1, y_1, c="black")
        plt.plot(x_2, y_2, c="black")
        # Total force coefficient visible in plot title
        plt.title("Total Downforce Coefficient: " +
                  str(self.results[self.case_settings[0][0]]
                      ['Totals']['CLtot']))
        # Axis labels
        plt.xlabel("Spanwise location [m]")
        plt.ylabel("Local downforce coefficient")

        plt.show()
        return "Plot is generated in a separate window"

    # Generate a drag distribution plot from the AVL results
    @Attribute
    def drag_plot(self):
        # Original surface data
        x_1 = self.drag_distribution[0][:len(self.drag_distribution[0])//2]
        y_1 = self.drag_distribution[1][:len(self.drag_distribution[0])//2]

        # Mirrored surface data
        x_2 = self.drag_distribution[0][len(self.drag_distribution[0])//2:]
        y_2 = self.drag_distribution[1][len(self.drag_distribution[0])//2:]

        plt.plot(x_1, y_1, c="black")
        plt.plot(x_2, y_2, c="black")
        # Total force coefficient visible in plot title
        plt.title("Total Drag Coefficient: " +
                  str(self.results[self.case_settings[0][0]]
                      ['Totals']['CDtot']))
        # Axis labels
        plt.xlabel("Spanwise location [m]")
        plt.ylabel("Local drag coefficient")

        plt.show()
        return "Plot is generated in a separate window"


def avl_main(geom, cond):
    from parapy.gui import display

    spoiler = Spoiler(label="Spoiler",
                      mid_airfoil=geom[0],
                      tip_airfoil=geom[1],
                      spoiler_span=geom[2]/1000.,
                      spoiler_chord=geom[3]/1000.,
                      spoiler_angle=geom[4],
                      strut_airfoil_shape=geom[5],
                      strut_lat_location=geom[6],
                      strut_height=geom[7]/1000.,
                      strut_chord_fraction=geom[8],
                      strut_thickness=geom[9]/1000.,
                      strut_sweep=geom[10],
                      strut_cant=geom[11],
                      endplate_present=False,
                      endplate_thickness=geom[13]/1000.,
                      endplate_sweep=geom[14],
                      endplate_cant=geom[15],
                      do_avl=True)

    case = [('AoA input', {'alpha': 0})]

    analysis = AvlAnalysis(spoiler=spoiler,
                           case_settings=case,
                           velocity=cond[0],
                           density=cond[2])

    display(analysis)
