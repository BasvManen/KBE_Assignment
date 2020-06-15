from math import radians, sin, cos, tan

from parapy.core import Input, Attribute, Part
from parapy.geom import *

import kbeutils.avl as avl


###############################################################################
# PLATE-SHAPED STRUT CLASS                                                    #
# In this file, the base of the plate-shaped strut is defined. It can         #
# return a single strut part, which will be partioned and correctly           #
# translated in the SpoilerAssembly class.                                    #
#                                                                             #
# Inputs:                                                                     #
# - Chord of the struts, as fraction of the chord of the main plate           #
# - Height of the struts, as defined from car base to spoiler base            #
# - Thickness of the struts                                                   #
# - Sweepback angle of the struts                                             #
# - Cant angle of the struts                                                  #
# - main, defined as a Part entry of the main plate geometry                  #
###############################################################################


class StrutPlate(GeomBase):

    chord_fraction = Input()
    strut_height = Input()
    strut_thickness = Input()
    strut_sweepback_angle = Input()
    strut_cant_angle = Input()
    main = Input()

    @Attribute
    def strut_chord(self):
        """" This attribute calculates the actual chord of the struts,
        which is defined in the x-direction. It makes sure that the chord of
        the strut will never exceed the chord (projected in x-direction) of
        the main plate. """
        return self.main[-1].chord * self.chord_fraction \
               * cos(radians(self.main[-1].angle))

    @Attribute
    def wetted_area(self):
        """ This attribute calculates the total wetted area of the struts.
        It calculates the area of each of the sides of the struts, and adds
        these separate contributions. """
        return 2 * (2 * self.strut_height * self.strut_chord +
                    2 * self.strut_height * self.strut_thickness +
                    2 * self.strut_chord * self.strut_thickness)

    @Part(in_tree=False)
    def upper_curve_rectangle(self):
        """ Create the upper rectangular curve, based on the strut chord and
        thickness. This curve is later used for creating a ruled solid. """
        return Rectangle(width=self.strut_chord, length=self.strut_thickness,
                         centered=False)

    @Part(in_tree=False)
    def lower_curve_rectangle(self):
        """ Create the lower rectangular curve for the ruled solid,
        by translating the upper curve in the right direction by means of
        strut height, sweepback angle and cant angle. """
        return Rectangle(width=self.strut_chord, length=self.strut_thickness,
                         position=translate(
                             self.upper_curve_rectangle.position,
                             "x", -self.strut_height *
                                  tan(radians(self.strut_sweepback_angle)),
                             "y", -self.strut_height *
                                  tan(radians(self.strut_cant_angle)),
                             "z", -self.strut_height),
                         centered=False)

    @Part(in_tree=False)
    def extended_curve_rectangle(self):
        """ In order to cut off the strut at the lower side of the main
        plate (at any main plate angle), the strut upper curve is extended
        to a higher z-location from where it can be easily partioned. The
        upper curve is extended in the correct direction by means of the
        strut height, sweepback angle and the cant angle. This instance will
        make sure that the strut is always attached to the lower side of the
        main plate. """
        return Rectangle(width=self.strut_chord, length=self.strut_thickness,
                         position=translate(
                             self.upper_curve_rectangle.position,
                             "x", (self.strut_height + self.main[-1].chord) *
                                  tan(radians(self.strut_sweepback_angle)),
                             "y", (self.strut_height + self.main[-1].chord) *
                                  tan(radians(self.strut_cant_angle)),
                             "z", self.strut_height + self.main[-1].chord),
                         centered=False)

    @Part(in_tree=False)
    def solid(self):
        """ Create the initial ruled solid for the extended strut from the
        rectangular curves. """
        return RuledSolid(profile1=self.extended_curve_rectangle,
                          profile2=self.lower_curve_rectangle)

    # Smooth the edges to obtain a filleted strut
    @Part(in_tree=True)
    def strut(self):
        """ Fillet the edges of the extended ruled solid to obtain a more
        refined plate-shaped strut. This instance will later be cut-off at
        the lower side of the main plate, and subtracted in the
        SpoilerAssembly class. """
        return FilletedSolid(built_from=self.solid,
                             radius=self.strut_thickness / 3)
