from analysis.spoiler_files import StrutAirfoil, StrutPlate
from parapy.core import Input, Attribute, Part, child, DynamicType
from parapy.core.validate import *
from parapy.geom import *
from math import sin, cos, radians, floor


###############################################################################
# STRUT ASSEMBLY CLASS                                                        #
# In this file, the bases of the struts created in StrutPlate and             #
# StrutAirfoil will be used to create the struts for the assembly.            #
#                                                                             #
# Inputs:                                                                     #
# - Amount of struts in the assembly, with a minimum of 2                     #
# - strut_airfoil_shape, defined as True if the struts are supposed to be     #
#   airfoil-shaped, and False if the struts are plate-shaped.                 #
# - The spanwise location of the most outboard strut, defined as fraction     #
#   of the half-span of the main plate.                                       #
# - Chord of the struts, as fraction of the chord of the main plate           #
# - Height of the struts, as defined from car base to spoiler base            #
# - Thickness of the struts                                                   #
# - Sweepback angle of the struts                                             #
# - Cant angle of the struts                                                  #
# - main, defined as a Part entry of the main plate geometry                  #
###############################################################################


class Struts(GeomBase):
    strut_amount = Input()
    strut_airfoil_shape = Input()
    strut_lat_location = Input()
    strut_height = Input()
    strut_chord_fraction = Input()
    strut_thickness = Input()
    strut_sweep = Input()
    strut_cant = Input()
    main = Input()

    @Attribute
    def strut_y_position(self):
        """ This attribute calculates the lateral y-location at which points
        along the main plate each strut will be attached. It first checks
        wheter the inputted strut amount is even or uneven. Depending on
        this, the spacing of the struts is determined. The input of
        strut_lat_location determines the most outboard strut loaction,
        and the other struts are equidistantly distributed over the main
        plate span. It return a list of y-locations of the struts, for only
        one half of the total spoiler span. """
        amount = self.strut_amount - floor(self.strut_amount / 2)
        y_translation = []
        for i in range(amount):
            if self.strut_amount % 2 == 0:
                y_translation.append(self.strut_lat_location
                                     * self.main.span
                                     / (self.strut_amount - 1) / 2 * (
                                             2 * i + 1))
            else:
                if i == 0:
                    y_translation.append(self.strut_thickness)
                else:
                    y_translation.append(self.strut_lat_location
                                         * self.main.span
                                         / (self.strut_amount - 1) * i)
        return y_translation

    @Part(in_tree=False)
    def struts(self):
        """ Create the struts. Depending on the input of
        strut_airfoil_shape, a StrutAirfoil or StrutPlate instance is
        returned. """
        return DynamicType(type=StrutAirfoil if self.strut_airfoil_shape
                           else StrutPlate,
                           chord_fraction=self.strut_chord_fraction,
                           strut_lat_location=self.strut_lat_location,
                           strut_height=self.strut_height,
                           strut_thickness=self.strut_thickness,
                           strut_sweepback_angle=self.strut_sweep,
                           strut_cant_angle=self.strut_cant,
                           main=self.main)

    @Part(in_tree=False)
    def struts_no_cant(self):
        """ If the inputted amount of struts in an uneven number, there will
        be also a strut placed at the midsection of the spoiler. This
        mid-strut has to have zero cant angle, as the spoiler is symmetric
        about its midpoint. Therefor it is defined separately in this part
        instance. """
        return DynamicType(type=StrutAirfoil if self.strut_airfoil_shape
                           else StrutPlate,
                           chord_fraction=self.strut_chord_fraction,
                           strut_lat_location=self.strut_lat_location,
                           strut_height=self.strut_height,
                           strut_thickness=self.strut_thickness,
                           strut_sweepback_angle=self.strut_sweep,
                           strut_cant_angle=0.,
                           main=self.main)

    @Part(in_tree=False)
    def translated_strut(self):
        """ Translate struts to their correct locations, this is done with
        TranslatedShape to make it work with both airfoil and plate strut
        shapes. It returns the struts at their correct x and y location for
        half the span of the spoiler. This can later be (partially) mirrored
        to get the struts for the full span. """
        return TranslatedShape(quantify=self.strut_amount
                                        - floor(self.strut_amount / 2),
                               shape_in=self.struts_no_cant.strut
                               if self.strut_amount % 2 != 0
                               and child.index == 0
                               else self.struts.strut,
                               displacement=
                               Vector(x=(self.main.chord
                                         * cos(radians(self.main.angle))
                                         - self.strut_chord_fraction
                                         * self.main.chord
                                         * cos(radians(self.main.angle))) / 2,
                                      y=self.strut_y_position[child.index]))

    @Part(in_tree=False)
    def partitioned_solid(self):
        """ In order to cut-off each spoiler at the lower side of the main
        plate, PartitionedSolid is used. This returns several cut pieces of
        which one is the wanted cut-off strut. """
        return PartitionedSolid(quantify=self.strut_amount
                                         - floor(self.strut_amount / 2),
                                solid_in=self.main.surface,
                                tool=self.translated_strut[child.index],
                                keep_tool=True,
                                mesh_deflection=1e-4)

    @Part
    def struts_right(self):
        """ Create the cut-off strut parts from the partitioned solid. These
        are the final struts over the right side of the spoiler. """
        return Solid(quantify=self.strut_amount - floor(self.strut_amount / 2)
                              - self.strut_amount % 2,
                     built_from=
                     self.partitioned_solid[child.index
                                            + self.strut_amount % 2].solids[3])

    @Part
    def struts_left(self):
        """ Mirror the struts defined in struts_right
        about the xz-plane of the spoiler. This will return the final strut
        parts along the left side of the spoiler. """
        return MirroredShape(quantify=self.strut_amount
                                      - floor(self.strut_amount / 2)
                                      - self.strut_amount % 2,
                             shape_in=self.struts_right[child.index],
                             reference_point=Point(0., 0., 0.),
                             vector1=Vector(1., 0., 0.),
                             vector2=Vector(0., 0., 1.))

    @Part
    def strut_mid(self):
        """ In case of an uneven amount of inputted struts, the strut on the
        mid-section of the spoiler is defined here. It returns a single
        strut part which is located at the mid-section and has no cant
        angle. """
        return TranslatedShape(shape_in=self.partitioned_solid[0].solids[3],
                               displacement=
                               Vector(0., -self.strut_thickness, 0.),
                               hidden=True if self.strut_amount % 2 == 0
                               else False)
