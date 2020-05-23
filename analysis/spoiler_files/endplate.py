from math import radians, sin, tan, cos

from parapy.core import *
from parapy.geom import *


# ENDPLATE CLASS
# In this file, the spoiler endplates are defined


class Endplate(GeomBase):

    # INPUTS
    chord = Input()
    height = Input()
    thickness = Input()
    sweepback_angle = Input()

    pos = Input(XOY)

    @Attribute
    def colors(self):
        return ["red", "green", "blue"]

    @Attribute
    def vectors(self):
        return [self.pos.Vx, self.pos.Vy, self.pos.Vz]

    @Part
    def vector(self):
        return LineSegment(quantify=3,
                           start=self.pos.location,
                           end=(translate(self.pos.location, self.vectors[child.index], 0.3)),
                           color=self.colors[child.index],
                           line_thickness=2
                           )

    @Attribute
    def endplate_chord(self):
        return self.chord

    # Define wetted area
    @Attribute
    def wetted_area(self):
        return self.solid.area

    # Define the upper (rectangular) curve of the endplate
    @Part(in_tree=False)
    def upper_curve(self):
        return Rectangle(width=self.chord,
                         length=self.thickness,
                         centered=False,
                         position=translate(self.position,
                                            'x', -self.chord)
                         )

    # Define the lower (rectangular) curve of the endplate
    @Part(in_tree=False)
    def lower_curve(self):
        return Rectangle(width=self.chord,
                         length=self.thickness,
                         centered=False,
                         position=translate(self.upper_curve.position,
                                            'z', -self.height)
                         )

    # Define the solid endplate based on the two curves
    @Part
    def solid(self):
        return FilletedSolid(built_from=RuledSolid(profile1=self.upper_curve,
                                                   profile2=self.lower_curve),
                             radius=self.thickness/3
                             )


if __name__ == '__main__':
    from parapy.gui import display
    obj = Endplate(chord=0.8,
                   height=0.2,
                   thickness=0.02,
                   sweepback_angle=0)
    display(obj)

