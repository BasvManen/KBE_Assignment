from spoiler_files import Spoiler
from parapy.core import *

import kbeutils.avl as avl


class AvlAnalysis(avl.Interface):

    spoiler = Input(in_tree=True)
    case_settings = Input()

    @Attribute
    def configuration(self):
        return self.spoiler.avl_configuration

    @Attribute
    def ld_ratio(self):
        return -self.results['default']['Totals']['CLtot'] / self.results['default']['Totals']['CDtot']

    @Part
    def case(self):
        return avl.Case(name=self.case_settings[0],
                        settings=self.case_settings[1])


if __name__ == '__main__':
    from parapy.gui import display
    spoiler = Spoiler(label="Spoiler",
                      mid_airfoil='9412',
                      tip_airfoil='9408',
                      spoiler_span=2.5,
                      spoiler_chord=0.8,
                      spoiler_angle=20.,
                      strut_airfoil_shape=False,
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
