from math import radians, sin

from parapy.core import Input, Attribute, Part
from parapy.geom import *


class StrutPlate(GeomBase):
    spoiler_span = Input(3000)                  # Specify main spoiler span
    strut_lat_location = Input(0.5)     # as fraction of spoiler half-span
    chord = Input(200)
    height = Input(600)
    thickness = Input(20)
    sweepback_angle = Input(15.)
    cant_angle = Input(25.)

    @Part(in_tree=False)
    def upper_curve_rectangle(self):
        return Rectangle(width=self.chord, length=self.thickness,
                         position=translate(self.position, "y", self.strut_lat_location*self.spoiler_span/2))

    @Part(in_tree=False)
    def lower_curve_rectangle(self):
        return Rectangle(width=self.chord, length=self.thickness,
                         position=translate(self.position, "x", self.height * sin(radians(self.sweepback_angle)),
                                            "y", self.strut_lat_location*self.spoiler_span/2+self.height * sin(radians(self.cant_angle)),
                                            "z", self.height))

    @Part(in_tree=False)
    def solid(self):
        return RuledSolid(profile1=self.upper_curve_rectangle, profile2=self.lower_curve_rectangle)

    @Part
    def fillet(self):
        return FilletedSolid(built_from=self.solid, radius=self.thickness/3)

    @Part
    def mirrored(self):
        return MirroredShape(shape_in=self.fillet,
                             reference_point=Point(0, 0, 0),
                             vector1=self.position.Vx,
                             vector2=self.position.Vz)


if __name__ == '__main__':
    from parapy.gui import display
    obj = StrutPlate(label="strut")
    display(obj)