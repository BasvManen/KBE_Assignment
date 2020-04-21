from math import radians, sin, cos

from parapy.core import Input, Attribute, Part
from parapy.geom import *

from kbeutils.geom.curve import Naca4AirfoilCurve


class StrutAirfoil(GeomBase):
    spoiler_span = Input()                  # Specify main spoiler span
    strut_lat_location = Input()     # as fraction of spoiler half-span
    chord = Input()
    height = Input()
    thickness = Input()
    sweepback_angle = Input()
    cant_angle = Input()

    @Attribute
    def thickness_to_chord(self):  # this attribute is used to define a symmetric airfoil
        if int(self.thickness/self.chord*100) < 2:  # the airfoil cannot get too thin
            ratio = 2
        elif int(self.thickness/self.chord*100) > 50:  # the airfoil cannot get too thick
            ratio = 40
        else:
            ratio = int(self.thickness / self.chord * 100)
        return ratio

    @Attribute
    def symmetric_airfoil_name(self):  # create 4-digit naca airfoil name
        name = '00'+str(self.thickness_to_chord)
        return name

    @Part(in_tree=False)
    def airfoil(self):
        return RotatedCurve(curve_in=Naca4AirfoilCurve(self.symmetric_airfoil_name, n_points=200),
                            rotation_point=XOY,
                            vector=self.position.Vx, angle=radians(90))

    @Part(in_tree=False)
    def airfoil_scaled(self):
        return ScaledCurve(curve_in=self.airfoil,
                           reference_point=XOY,
                           factor=self.chord)

    @Part(in_tree=False)
    def upper_curve_airfoil(self):
        return TranslatedCurve(curve_in=self.airfoil_scaled,
                               displacement=Vector(self.position.point[0], self.strut_lat_location*self.spoiler_span/2, self.position.point[2]))

    @Part(in_tree=False)
    def lower_curve_airfoil(self):
        return TranslatedCurve(curve_in=self.upper_curve_airfoil,
                               displacement=Vector(-self.height*sin(radians(self.sweepback_angle)),
                                                   -self.height*sin(radians(self.cant_angle)),
                                                   -self.height))

    @Part
    def solid(self):
        return RuledSolid(profile1=self.upper_curve_airfoil, profile2=self.lower_curve_airfoil)

    @Part
    def mirrored(self):
        return MirroredShape(shape_in=self.solid,
                             reference_point=Point(0, 0, 0),
                             vector1=self.position.Vx,
                             vector2=self.position.Vz)


if __name__ == '__main__':
    from parapy.gui import display
    obj = StrutAirfoil(label="strut",
                       spoiler_span=3000,
                       strut_lat_location=0.1,
                       chord=400,
                       height=500,
                       thickness=20,
                       sweepback_angle=15,
                       cant_angle=0)
    display(obj)