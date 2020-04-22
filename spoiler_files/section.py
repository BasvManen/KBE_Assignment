from parapy.core import *
from parapy.geom import *
from kbeutils.geom.curve import Naca5AirfoilCurve, Naca4AirfoilCurve
import kbeutils.avl as avl

from math import radians


class Section(GeomBase):
    airfoil_name = Input()
    chord = Input()
    angle = Input()

    @Part(in_tree=False)
    def airfoil(self):
        return DynamicType(type=(Naca5AirfoilCurve
                                 if len(self.airfoil_name) == 5
                                 else Naca4AirfoilCurve),
                           designation=self.airfoil_name)

    @Part(in_tree=False)
    def curve_flat(self):
        return ScaledCurve(curve_in=self.airfoil,
                           reference_point=self.position.point,
                           factor=self.chord)

    @Part(in_tree=False)
    def curve_up(self):
        return RotatedCurve(curve_in=self.curve_flat,
                            rotation_point=self.position,
                            vector=self.position.Vy,
                            angle=radians(self.angle))

    @Part
    def curve(self):
        return RotatedCurve(curve_in=self.curve_up,
                            rotation_point=self.position,
                            vector=self.position.Vx,
                            angle=radians(180))

    @Part(in_tree=False)
    def avl_section(self):
        return avl.SectionFromCurve(curve_in=self.curve_up, angle=-self.angle)


if __name__ == '__main__':
    from parapy.gui import display
    obj = Section(airfoil_name='9412',
                  chord=800,
                  angle=20)
    display(obj)
