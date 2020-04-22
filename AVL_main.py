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
        return {case_name: result['Totals']['CLtot'] / result['Totals']['CLtot']
                for case_name, result in self.results.items()}

    @Part
    def case(self):
        return avl.Case(name=self.case_settings[0],
                        settings=self.case_settings[1])


if __name__ == '__main__':
    from parapy.gui import display
    spoiler = Spoiler(label="Spoiler",
                      mid_airfoil='9412',
                      tip_airfoil='9408',
                      spoiler_span=2500.,
                      spoiler_chord=800.,
                      spoiler_angle=20.,
                      strut_airfoil_shape=False,
                      strut_lat_location=0.8,
                      strut_height=250.,
                      strut_chord=400.,
                      strut_thickness=40.,
                      strut_sweep=15.,
                      strut_cant=0.,
                      endplate_present=True,
                      endplate_thickness=10.,
                      endplate_sweep=15.,
                      endplate_cant=0.)

    case = ['fixed aoa', {'alpha': 0}]

    analysis = AvlAnalysis(spoiler=spoiler,
                           case_settings=case)
    display(analysis)
