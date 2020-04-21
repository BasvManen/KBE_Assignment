from math import radians, sin

from parapy.core import Input, Attribute, Part
from parapy.geom import *


class StrutPlate(GeomBase):
    spoiler_span = Input()                  # Specify main spoiler span
    strut_lat_location = Input()     # as fraction of spoiler half-span
    chord = Input()
    height = Input()                # as defined from spoiler leading edge to strut base
    thickness = Input()
    sweepback_angle = Input()
    cant_angle = Input()
    main = Input()

    @Part(in_tree=False)
    def upper_curve_rectangle(self):
        return Rectangle(width=self.chord, length=self.thickness,
                         position=translate(self.position, "y", self.strut_lat_location*self.spoiler_span/2),
                         centered=False)

    @Part(in_tree=False)
    def lower_curve_rectangle(self):
        return Rectangle(width=self.chord, length=self.thickness,
                         position=translate(self.upper_curve_rectangle.position,
                                            "x", -self.height * sin(radians(self.sweepback_angle)),
                                            "y", -self.height * sin(radians(self.cant_angle)),
                                            "z", -self.height),
                         centered=False)

    @Part(in_tree=False)
    def extended_curve_rectangle(self):
        return Rectangle(width=self.chord, length=self.thickness,
                         position=translate(self.upper_curve_rectangle.position,
                                            "x", self.height * sin(radians(self.sweepback_angle)),
                                            "y", self.height * sin(radians(self.cant_angle)),
                                            "z", self.height),
                         centered=False)

    @Part(in_tree=False)
    def solid(self):
        return RuledSolid(profile1=self.extended_curve_rectangle, profile2=self.lower_curve_rectangle)

    @Part(in_tree=False)
    def fillet(self):
        return FilletedSolid(built_from=self.solid, radius=self.thickness/3)

    @Part(in_tree=False)
    def partitioned_solid(self):
        return PartitionedSolid(solid_in=self.main.surface, tool=self.fillet, keep_tool=True)

    @Part
    def strut(self):
        return SubtractedSolid(shape_in=SubtractedSolid(shape_in=self.fillet, tool=self.partitioned_solid.solids[2] if self.partitioned_solid.solids[2].area < self.partitioned_solid.solids[3].area else self.partitioned_solid.solids[3]),
                               tool=self.partitioned_solid.solids[1])

    @Part
    def mirrored(self):
        return MirroredShape(shape_in=self.strut,
                             reference_point=Point(0, 0, 0),
                             vector1=self.position.Vx,
                             vector2=self.position.Vz)


if __name__ == '__main__':
    from parapy.gui import display
    obj = StrutPlate(label="strut",
                     spoiler_span = 3000,
                     strut_lat_location=0.8,
                     chord=800,
                     height=400,
                     thickness=20,
                     sweepback_angle=15,
                     cant_angle=0)
    display(obj)