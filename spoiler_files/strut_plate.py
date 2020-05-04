from math import radians, sin

from parapy.core import Input, Attribute, Part
from parapy.geom import *

import kbeutils.avl as avl


class StrutPlate(GeomBase):
    main_plate_span = Input()  # Specify main spoiler span
    strut_lat_location = Input()  # as fraction of spoiler half-span
    chord_fraction = Input()
    strut_height = Input() # as defined from spoiler leading edge to strut base
    strut_thickness = Input()
    strut_sweepback_angle = Input()
    strut_cant_angle = Input()
    main = Input()

    @Attribute
    def strut_chord(self):
        return self.main.chord * self.chord_fraction

    @Part(in_tree=False)
    def upper_curve_rectangle(self):
        return Rectangle(width=self.strut_chord, length=self.strut_thickness,
                         position=translate(self.position, "y",
                                            self.strut_lat_location
                                            * self.main_plate_span / 2),
                         centered=False)

    @Part(in_tree=False)
    def lower_curve_rectangle(self):
        return Rectangle(width=self.strut_chord, length=self.strut_thickness,
                         position=translate(
                             self.upper_curve_rectangle.position,
                             "x",
                             -self.strut_height * sin(radians(self.strut_sweepback_angle)),
                             "y", -self.strut_height * sin(radians(self.strut_cant_angle)),
                             "z", -self.strut_height),
                         centered=False)

    @Part(in_tree=False)
    def avl_section_up(self):
        return avl.SectionFromCurve(curve_in=self.upper_curve_rectangle)

    @Part(in_tree=False)
    def avl_section_lo(self):
        return avl.SectionFromCurve(curve_in=self.lower_curve_rectangle)

    @Part(in_tree=False)
    def extended_curve_rectangle(self):
        return Rectangle(width=self.strut_chord, length=self.strut_thickness,
                         position=translate(
                             self.upper_curve_rectangle.position,
                             "x",
                             self.strut_height * sin(radians(self.strut_sweepback_angle)),
                             "y", self.strut_height * sin(radians(self.strut_cant_angle)),
                             "z", self.strut_height),
                         centered=False)

    @Part(in_tree=False)
    def solid(self):
        return RuledSolid(profile1=self.extended_curve_rectangle,
                          profile2=self.lower_curve_rectangle)

    @Part(in_tree=False)
    def fillet(self):
        return FilletedSolid(built_from=self.solid, radius=self.strut_thickness / 3)

    @Part(in_tree=False)
    def partitioned_solid(self):
        return PartitionedSolid(solid_in=self.main.surface, tool=self.fillet,
                                keep_tool=True)

    @Part
    def strut_right(self):
        return SubtractedSolid(shape_in=
                               SubtractedSolid(shape_in=self.fillet,
                                               tool=
                                               self.partitioned_solid.solids[
                                                   2]),
                               tool=self.partitioned_solid.solids[1])

    @Part
    def strut_left(self):
        return MirroredShape(shape_in=self.strut_right,
                             reference_point=Point(0, 0, 0),
                             vector1=self.position.Vx,
                             vector2=self.position.Vz)

    @Part
    def avl_surface(self):
        return avl.Surface(name="Struts",
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.cosine,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.cosine,
                           y_duplicate=self.position.point[1],
                           sections=[self.avl_section_up, self.avl_section_lo])


if __name__ == '__main__':
    from parapy.gui import display

    obj = StrutPlate(label="strut",
                     spoiler_span=3000,
                     strut_lat_location=0.8,
                     chord=800,
                     height=400,
                     thickness=20,
                     sweepback_angle=15,
                     cant_angle=0)
    display(obj)
