from spoiler_files import Spoiler
from parapy.core import *

import kbeutils.avl as avl
import matplotlib.pyplot as plt


class AvlAnalysis(avl.Interface):

    spoiler = Input(in_tree=True)
    case_settings = Input()

    @Attribute
    def configuration(self):
        return self.spoiler.avl_configuration

    @Attribute
    def ld_ratio(self):
        return -self.results['default']['Totals']['CLtot'] / self.results['default']['Totals']['CDtot']

    @Attribute
    def force_distribution(self):
        return [self.results['default']['StripForces']['Main Plate']['Yle'],
                self.results['default']['StripForces']['Main Plate']['c cl']]

    @Part
    def case(self):
        return avl.Case(name=self.case_settings[0],
                        settings=self.case_settings[1])


if __name__ == '__main__':
    from parapy.gui import display
    spoiler = Spoiler(label="Spoiler",
                      mid_airfoil='0012',
                      tip_airfoil='0008',
                      spoiler_span=2.5,
                      spoiler_chord=0.8,
                      spoiler_angle=5.,
                      strut_airfoil_shape=True,
                      strut_lat_location=0.8,
                      strut_height=0.25,
                      strut_chord=0.4,
                      strut_thickness=0.04,
                      strut_sweep=15.,
                      strut_cant=0.,
                      endplate_present=False,
                      endplate_thickness=0.01,
                      endplate_sweep=15.,
                      endplate_cant=0.)

    case = ['fixed aoa', {'alpha': 0}]

    analysis = AvlAnalysis(spoiler=spoiler,
                           case_settings=case)

    print("Current Geometry Efficiency: L/D =", analysis.ld_ratio)
    display(analysis)
