from math import radians, sin

from parapy.core import Input, Part
from parapy.geom import *


class Endplates(GeomBase):
    spoiler_span = Input()                   # Specify main spoiler span
    endplate_position = Input()              # Point of attachment to spoiler, as fraction of endplate height
    chord = Input()                          # Should be the same as tip-chord of spoiler
    height = Input()
    thickness = Input()
    sweepback_angle = Input()
    cant_angle = Input()

    @Part
    def mid_curve(self):
        return Rectangle(width=self.chord, length=self.thickness,
                         position=translate(self.position, "y", self.spoiler_span/2 + self.thickness/2))

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

    @Part(in_tree=False)
    def solid(self):
        return RuledSolid(profile1=self.upper_curve, profile2=self.lower_curve)

    @Part
    def fillet(self):
        return FilletedSolid(built_from=self.solid, radius=self.thickness/3)

    @Part
    def mirrored(self):
        return MirroredShape(shape_in=self.fillet,
                             reference_point=self.position,
                             vector1=self.position.Vx,
                             vector2=self.position.Vz)


if __name__ == '__main__':
    from parapy.gui import display
    obj = Endplates(label="endplates")
    display(obj)
