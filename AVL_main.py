from spoiler_files import Spoiler
from parapy.core import *

import kbeutils.avl as avl
import matplotlib.pyplot as plt
import numpy as np


class AvlAnalysis(avl.Interface):

    spoiler = Input(in_tree=True)
    case_settings = Input()
    velocity = Input()

    @Attribute
    def configuration(self):
        return self.spoiler.avl_configuration

    @Part
    def cases(self):
        return avl.Case(quantify=len(self.case_settings),
                        name=self.case_settings[child.index][0],
                        settings=self.case_settings[child.index][1])

    @Attribute
    def dyn_pressure(self):
        return 0.5*1.225*self.velocity**2

    @Attribute
    def total_force(self):
        cl = self.results[self.case_settings[0][0]]['Totals']['CLtot']
        force = cl*self.dyn_pressure*self.spoiler.reference_area
        return force

    @Attribute
    def ld_ratio(self):
        return self.results[self.case_settings[0][0]]['Totals']['CLtot'] \
               / self.results[self.case_settings[0][0]]['Totals']['CDtot']

    @Attribute
    def lift_distribution(self):
        return [self.results[self.case_settings[0][0]]['StripForces']['Main Plate']['Yle'],
                self.results[self.case_settings[0][0]]['StripForces']['Main Plate']['c cl']]

    @Attribute
    def lift_plot(self):
        x_axis_1 = self.lift_distribution[0][:len(self.lift_distribution[0])//2]
        y_axis_1 = self.lift_distribution[1][:len(self.lift_distribution[0])//2]
        x_axis_2 = self.lift_distribution[0][len(self.lift_distribution[0])//2:]
        y_axis_2 = self.lift_distribution[1][len(self.lift_distribution[0])//2:]

        plt.plot(x_axis_1, y_axis_1, c="black")
        plt.plot(x_axis_2, y_axis_2, c="black")
        plt.title("Total Downforce Coefficient: " + str(self.results[self.case_settings[0][0]]['Totals']['CLtot']))
        plt.xlabel("Spanwise location [m]")
        plt.ylabel("Local downforce coefficient")
        plt.show()
        return "Plot is generated in a separate window"

    @Attribute
    def drag_plot(self):
        x_axis_1 = self.drag_distribution[0][:len(self.drag_distribution[0])//2]
        y_axis_1 = self.drag_distribution[1][:len(self.drag_distribution[0])//2]
        x_axis_2 = self.drag_distribution[0][len(self.drag_distribution[0])//2:]
        y_axis_2 = self.drag_distribution[1][len(self.drag_distribution[0])//2:]

        plt.plot(x_axis_1, y_axis_1, c="black")
        plt.plot(x_axis_2, y_axis_2, c="black")
        plt.title("Total Drag Coefficient: " + str(self.results[self.case_settings[0][0]]['Totals']['CDtot']))
        plt.xlabel("Spanwise location [m]")
        plt.ylabel("Local drag coefficient")
        plt.show()
        return "Plot is generated in a separate window"

    @Attribute
    def drag_distribution(self):
        return [self.results[self.case_settings[0][0]]['StripForces']['Main Plate']['Yle'],
                np.multiply(self.results[self.case_settings[0][0]]['StripForces']['Main Plate']['cd'],
                self.results[self.case_settings[0][0]]['StripForces']['Main Plate']['Chord'])]


if __name__ == '__main__':
    from parapy.gui import display

    spoiler = Spoiler(label="Spoiler",
                      mid_airfoil='0012',
                      tip_airfoil='0012',
                      spoiler_span=2.5,
                      spoiler_chord=0.8,
                      spoiler_angle=0,
                      strut_airfoil_shape=True,
                      strut_lat_location=0.8,
                      strut_height=0.25,
                      strut_chord_fraction=0.7,
                      strut_thickness=0.04,
                      strut_sweep=15.,
                      strut_cant=0.,
                      endplate_present=False,
                      endplate_thickness=0.01,
                      endplate_sweep=15.,
                      endplate_cant=0.)

    case = [('AoA input', {'alpha': 3})]

    analysis = AvlAnalysis(spoiler=spoiler,
                           case_settings=case,
                           velocity=30)

    display(analysis)
