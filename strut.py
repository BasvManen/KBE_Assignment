from math import radians, sin

from parapy.core import Input, Attribute, Part, child
from parapy.geom import *
from kbeutils.geom.curve import Naca4AirfoilCurve


spoiler_span = 1.5  # Specify main spoiler span


class Strut(GeomBase):
    strut_type = Input(1)               # 1 for sym_airfoil, 2 for simple plate
    strut_lat_location = Input(0.5)     # as fraction of spoiler half-span
    chord = Input(0.1)
    height = Input(0.6)
    thickness = Input(0.02)
    sweepback_angle = Input(15.)
    cant_angle = Input(25.)

    @Attribute
    def thickness_to_chord(self): # this attribute is used to define a symmetric airfoil
        if int(self.thickness/self.chord*100) < 2: # the airfoil cannot get too thin
            ratio = 2
        elif int(self.thickness/self.chord*100) > 50: # the airfoil cannot get too thick
            ratio = 40
        else:
            ratio = int(self.thickness / self.chord * 100)
        return ratio

    @Attribute
    def symmetric_airfoil_name(self): # create 4-digit naca airfoil name
        name = '00'+str(self.thickness_to_chord)
        return name

    @Part(in_tree=False)
    def airfoil(self):
        return RotatedCurve(curve_in=Naca4AirfoilCurve(self.symmetric_airfoil_name, n_points=200),
                            rotation_point=self.position,
                            vector=self.position.Vx, angle=radians(90))

    @Attribute
    def points2(self):
        return [Point(0, 0, 0),
                Point(self.chord, 0, 0),
                Point(self.chord, self.thickness, 0),
                Point(0, self.thickness, 0),
                Point(0, 0, 0)]

    @Part(in_tree=False)
    def curves2(self):
        return LineSegment(quantify=4, start=self.points2[child.index], end=self.points2[child.index + 1])

    @Part(in_tree=False)
    def curves_option_2(self):
        return ComposedCurve(built_from=self.curves2)

    @Attribute
    def strut_curve(self): # to either get the curves for the symmetric airfoil or thin plate below
        if self.strut_type == 1:
            crv = self.airfoil
        elif self.strut_type == 2:
            crv = self.curves_option_2
        return crv

    @Attribute
    def factor(self): # different strut type requires different scaling factor below
        if self.strut_type == 1:
            fct = self.chord
        elif self.strut_type == 2:
            fct = 1
        return fct

    @Part(in_tree=False)
    def upper_curve_scaled(self):
        return ScaledCurve(curve_in=self.strut_curve,
                           reference_point=self.position.point,
                           factor=self.factor)

    @Part
    def upper_curve(self):
        return TranslatedCurve(curve_in=self.upper_curve_scaled, displacement=Vector(0, self.strut_lat_location*spoiler_span, 0))

    @Part
    def lower_curve(self):
        return TranslatedCurve(curve_in=self.upper_curve,
                               displacement=Vector(self.height*sin(radians(self.sweepback_angle)),
                                                   self.height*sin(radians(self.cant_angle)),
                                                   self.height))

    @Part
    def surface(self):
        return LoftedShell(profiles=[self.upper_curve, self.lower_curve],
                           ruled=True)

    @Part
    def mirrored(self):
        return MirroredSurface(surface_in=self.surface.faces[0],
                               reference_point=Point(0,0,0),
                               vector1=self.position.Vx,
                               vector2=self.position.Vz)


if __name__ == '__main__':
    from parapy.gui import display
    obj = Strut(label="strut")
    display(obj)