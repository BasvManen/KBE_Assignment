from math import radians, sin

from parapy.core import Input, Attribute, Part, child
from parapy.geom import *


spoiler_span = 1.5  # Specify main spoiler span


class Endplates(GeomBase):
    endplate_input = Input(True)                # True for spoiler with, False for spoiler without endplates
    endplate_position = Input(0.5)              # Point of attachment to spoiler, as fraction of endplate height
    chord = Input(0.1)                          # Should be the same as tip-chord of spoiler
    height = Input(0.1)
    thickness = Input(0.1)
    sweepback_angle = Input(0.)
    cant_angle = Input(0.)

    @Part
    def mid_curve(self):
        return Rectangle(width=self.chord, length=self.thickness,
                         position=translate(self.position, "y", spoiler_span/2 + self.thickness/2))

    @Part
    def upper_curve(self):
        return Rectangle(width=self.chord, length=self.thickness,
                         position=translate(self.mid_curve.position,
                                            "x", self.height*self.endplate_position*sin(radians(self.sweepback_angle)),
                                            "y", self.height*self.endplate_position*sin(radians(self.cant_angle)),
                                            "z", self.height*self.endplate_position))

    @Part
    def lower_curve(self):
        return Rectangle(width=self.chord, length=self.thickness,
                         position=translate(self.mid_curve.position,
                                            "x", self.height * (self.endplate_position-1) * sin(radians(self.sweepback_angle)),
                                            "y", self.height*(self.endplate_position-1) * sin(radians(self.cant_angle)),
                                            "z", self.height * (self.endplate_position-1)))

    @Part
    def surface(self):
        return RuledSolid(profile1=self.upper_curve, profile2=self.lower_curve)

    @Part
    def fillet(self):
        return FilletedSolid(built_from=self.surface, radius=0.002)

    @Part
    def mirrored(self):
        return MirroredShape(shape_in=self.fillet,
                             reference_point=Point(0, 0, 0),
                             vector1=self.position.Vx,
                             vector2=self.position.Vz)


if __name__ == '__main__':
    from parapy.gui import display
    obj = Endplates(label="endplates")
    display(obj)