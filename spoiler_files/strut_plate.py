from math import radians, sin, cos

from parapy.core import Input, Attribute, Part
from parapy.geom import *

import kbeutils.avl as avl

# PLATE-SHAPED STRUT CLASS
# In this file, the plate-shaped strut is defined


class StrutPlate(GeomBase):

    # INPUTS
    strut_lat_location = Input()
    chord_fraction = Input()
    strut_height = Input()
    strut_thickness = Input()
    strut_sweepback_angle = Input()
    strut_cant_angle = Input()
    main = Input()

    do_avl = Input(False)

    # Calculate the strut chord from the spoiler chord and angle
    @Attribute
    def strut_chord(self):
        return self.main.chord * self.chord_fraction \
               * cos(radians(self.main.angle))

    # Define the upper curve of the strut
    @Part(in_tree=False)
    def upper_curve_rectangle(self):
        return Rectangle(width=self.strut_chord, length=self.strut_thickness,
                         position=translate(self.position, "y",
                                            self.strut_lat_location
                                            * self.main.span / 2),
                         centered=False)

    # Define the lower curve of the strut
    @Part(in_tree=False)
    def lower_curve_rectangle(self):
        return Rectangle(width=self.strut_chord, length=self.strut_thickness,
                         position=translate(
                             self.upper_curve_rectangle.position,
                             "x", -self.strut_height *
                                  sin(radians(self.strut_sweepback_angle)),
                             "y", -self.strut_height *
                                  sin(radians(self.strut_cant_angle)),
                             "z", -self.strut_height),
                         centered=False)

    # Define upper section for AVL surface
    @Part(in_tree=False)
    def avl_section_up(self):
        return avl.SectionFromCurve(curve_in=self.upper_curve_rectangle)

    # Define lower section for AVL surface
    @Part(in_tree=False)
    def avl_section_lo(self):
        return avl.SectionFromCurve(curve_in=self.lower_curve_rectangle)

    # Define the extended curve, in case the spoiler is under an angle.
    # This will make sure that the strut is always attached to the spoiler
    @Part(in_tree=False)
    def extended_curve_rectangle(self):
        return Rectangle(width=self.strut_chord, length=self.strut_thickness,
                         position=translate(
                             self.upper_curve_rectangle.position,
                             "x", self.strut_height *
                                  sin(radians(self.strut_sweepback_angle)),
                             "y", self.strut_height *
                                  sin(radians(self.strut_cant_angle)),
                             "z", self.strut_height + self.main.chord),
                         centered=False)

    # Define the solid strut from the curves
    @Part(in_tree=False)
    def solid(self):
        return RuledSolid(profile1=self.extended_curve_rectangle,
                          profile2=self.lower_curve_rectangle)

    # Smooth the edges to obtain a filleted strut
    @Part(in_tree=False)
    def fillet(self):
        return FilletedSolid(built_from=self.solid,
                             radius=self.strut_thickness / 3)

    # Define the intersection of the strut and the main plate.
    # This is needed to define the cutting plane for the strut
    @Part(in_tree=False)
    def partitioned_solid(self):
        return PartitionedSolid(solid_in=self.main.surface, tool=self.fillet,
                                keep_tool=True)

    # Create the strut by cutting the filleted solid at the main plate
    @Part
    def strut_right(self):
        return SubtractedSolid(shape_in=
                               SubtractedSolid(shape_in=self.fillet,
                                               tool=
                                               self.partitioned_solid.solids[
                                                   2]),
                               tool=self.partitioned_solid.solids[1])

    # Mirror of the first strut
    @Part
    def strut_left(self):
        return MirroredShape(shape_in=self.strut_right,
                             reference_point=Point(0, 0, 0),
                             vector1=self.position.Vx,
                             vector2=self.position.Vz)

    # Define the surface for the AVL analysis
    @Part
    def avl_surface(self):
        return avl.Surface(name="Struts",
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.cosine,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.cosine,
                           y_duplicate=self.position.point[1],
                           sections=[self.avl_section_up, self.avl_section_lo],
                           hidden=not self.do_avl)


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
