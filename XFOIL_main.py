from spoiler_files import Spoiler
from parapy.core import *
from parapy.geom import *

from kbeutils.geom.curve import airfoil_points_in_xy_plane


class XFoilAnalysis(GeomBase):

    spoiler = Input(in_tree=True)
    fraction = Input(0.3)

    @Part
    def cutting_plane(self):
        return Plane(Point(0, self.fraction*spoiler.spoiler_span/2, 0), normal=VY)

    @Part
    def analysis_section(self):
        return IntersectedShapes(shape_in=self.spoiler.main_plate.surface,
                                 tool=self.cutting_plane)

    @Part
    def section_points(self):
        return airfoil_points_in_xy_plane(curve_in=self.analysis_section)


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

    analysis = XFoilAnalysis(spoiler=spoiler)
    display(analysis)
