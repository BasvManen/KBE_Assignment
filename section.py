from parapy.core import *
from parapy.geom import *
from kbeutils.geom.curve import Naca5AirfoilCurve, Naca4AirfoilCurve


class Section(GeomBase):
    airfoil_name = Input()
    chord = Input()

    @Part(in_tree=False)
    def airfoil(self):
        return DynamicType(type=(Naca5AirfoilCurve
                                 if len(self.airfoil_name) == 5
                                 else Naca4AirfoilCurve),
                           designation=self.airfoil_name)

    @Part
    def curve(self):
        return ScaledCurve(curve_in=self.airfoil,
                           reference_point=self.position.point,
                           factor=self.chord)


if __name__ == '__main__':
    from parapy.gui import display
    obj = Section(airfoil_name='00112',
                  chord=2)
    display(obj)
