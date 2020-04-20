from math import radians, sin, tan, cos

from parapy.core import Input, Part, Attribute
from parapy.geom import *

import kbeutils.avl as avl


class Endplates(GeomBase):
    spoiler_span = Input()                   # Specify main spoiler span
    chord = Input()                          # Should be the same as tip-chord of spoiler
    height = Input()
    thickness = Input()
    sweepback_angle = Input()
    cant_angle = Input()

    @Attribute
    def endplate_chord(self):
        return self.chord - self.height*tan(radians(self.sweepback_angle))

    #@Part
    #def mid_curve(self):
    #    return Rectangle(width=self.chord, length=self.thickness,
    #                     position=translate(self.position, "y", self.spoiler_span/2 + self.thickness/2))

    @Part
    def upper_curve(self):
        return Rectangle(width=self.endplate_chord, length=self.thickness,
                         position=translate(XOY,
                                            "x", self.chord-self.endplate_chord/2,
                                            "y", self.spoiler_span/2,
                                            "z", self.height)
                         )

    @Part
    def lower_curve(self):
        return Rectangle(width=self.endplate_chord, length=self.thickness,
                         position=translate(self.upper_curve.position,
                                            "x", -self.height*tan(radians(self.sweepback_angle)),
                                            "y", -self.height*tan(radians(self.cant_angle)),
                                            "z", -self.height))

    @Part
    def avl_section_up(self):
        return avl.SectionFromCurve(curve_in=self.upper_curve)

    @Part
    def avl_section_lo(self):
        return avl.SectionFromCurve(curve_in=self.lower_curve)

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

    @Part
    def avl_surface(self):
        return avl.Surface(name="Endplates",
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.cosine,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.cosine,
                           y_duplicate=self.position.point[1],
                           sections=[self.avl_section_up, self.avl_section_lo])


if __name__ == '__main__':
    from parapy.gui import display
    obj = Endplates(label="endplates",
                    spoiler_span=3000,
                    chord=800,
                    height=400,
                    thickness=10,
                    sweepback_angle=15,
                    cant_angle=15)
    display(obj)
