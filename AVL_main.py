from spoiler_files import Spoiler
from parapy.core import *

import kbeutils.avl as avl


class AvlAnalysis(avl.Interface):

    spoiler = Input(in_tree=True)

    @Attribute
    def configuration(self):
        return self.spoiler.avl_configuration


if __name__ == '__main__':
    from parapy.gui import display
    spoiler = Spoiler(label="Spoiler",
                      mid_airfoil='9412',
                      tip_airfoil='9408',
                      spoiler_span=3000.,
                      spoiler_chord=800.,
                      spoiler_angle=20.,
                      strut_airfoil_shape=True,
                      strut_lat_location=0.5,
                      strut_height=400.,
                      strut_chord=400.,
                      strut_thickness=20.,
                      strut_sweep=15.,
                      strut_cant=0.,
                      endplate_present=True,
                      endplate_height=400.,
                      endplate_thickness=10.,
                      endplate_sweep=15.,
                      endplate_cant=0.)

    analysis = AvlAnalysis(spoiler=spoiler)
    display(analysis)
