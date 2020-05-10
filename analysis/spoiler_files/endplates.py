from math import radians, sin, tan, cos

from parapy.core import Input, Part, Attribute
from parapy.geom import *

import kbeutils.avl as avl

# ENDPLATE CLASS
# In this file, the spoiler endplates are defined


class Endplates(GeomBase):

    # INPUTS
    spoiler_span = Input()
    spoiler_height = Input()
    chord = Input()
    height = Input()
    thickness = Input()
    sweepback_angle = Input()
    cant_angle = Input()

    # Calculate endplate chord based on sweep angle and spoiler chord
    @Attribute
    def endplate_chord(self):
        return self.chord

    # Define wetted area
    @Attribute
    def wetted_area(self):
        return 2 * (2 * self.chord * self.height +
                    2 * self.chord * self.thickness +
                    2 * self.height * self.thickness)

    # Define the upper (rectangular) curve of the endplate
    @Part
    def upper_curve(self):
        return Rectangle(width=self.endplate_chord, length=self.thickness,
                         position=translate(XOY,
                                            "x", self.chord-self.endplate_chord
                                            / 2,
                                            "y", self.spoiler_span/2,
                                            "z", self.spoiler_height)
                         )

    # Define the lower (rectangular) curve of the endplate
    @Part
    def lower_curve(self):
        return Rectangle(width=self.endplate_chord, length=self.thickness,
                         position=translate(self.upper_curve.position,
                                            "x", -self.height*tan(
                                                radians(self.sweepback_angle)),
                                            "y", -self.height*tan(
                                                radians(self.cant_angle)),
                                            "z", -self.height))

    # Define the upper curve for the AVL surface
    @Part(in_tree=False)
    def avl_section_up(self):
        return avl.SectionFromCurve(curve_in=self.upper_curve)

    # Define the lower curve for the AVL surface
    @Part(in_tree=False)
    def avl_section_lo(self):
        return avl.SectionFromCurve(curve_in=self.lower_curve)

    # Define the solid endplate based on the two curves
    @Part(in_tree=False)
    def solid(self):
        return RuledSolid(profile1=self.upper_curve, profile2=self.lower_curve)

    # Smooth the edges of the solid to get a filleted endplate
    @Part
    def endplate_right(self):
        return FilletedSolid(built_from=self.solid, radius=self.thickness/3)

    # Mirror of the endplate
    @Part
    def endplate_left(self):
        return MirroredShape(shape_in=self.endplate_right,
                             reference_point=self.position,
                             vector1=self.position.Vx,
                             vector2=self.position.Vz)

    # Create surface for the AVL analysis
    @Part(in_tree=False)
    def avl_surface(self):
        return avl.Surface(name="Endplates",
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.cosine,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.cosine,
                           y_duplicate=self.position.point[1],
                           sections=[self.avl_section_up, self.avl_section_lo])
