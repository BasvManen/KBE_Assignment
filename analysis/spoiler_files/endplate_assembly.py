from parapy.core import *
from parapy.geom import *
from math import radians

from analysis.spoiler_files.endplate import Endplate

###############################################################################
# ENDPLATE ASSEMBLY CLASS                                                     #
# In this file, the endplate assembly is defined,                             #
# based on the endplate class.                                                #
#                                                                             #
# Inputs:                                                                     #
# - Chord of the endplate                                                     #
# - Height of the endplate                                                    #
# - Thickness of the endplate                                                 #
# - Sweep angle of the endplate                                               #
# - Cant angle of the endplate                                                #
# - Main plate part, as defined in the main plate class                       #
###############################################################################


class Endplates(GeomBase):

    chord = Input()
    height = Input()
    thickness = Input()
    sweep = Input()
    cant = Input()
    main = Input(in_tree=False)

    @Attribute
    def wetted_area(self):
        """ This attribute returns the wetted area of both endplates together.
        This is used for the calculation of the total wetted area of the
        spoiler. """
        return 2 * self.endplate.solid.area

    @Part(in_tree=False)
    def endplate(self):
        """ This part creates an endplate from the endplate class. It is based
        on the inputs of this class. """
        return Endplate(chord=self.chord,
                        height=self.height,
                        thickness=self.thickness,
                        sweep=self.sweep,
                        position=self.position)

    @Part
    def solid(self):
        """ This part applies the cant angle to the endplate part. This is the
        end product of this class for the right endplate. """
        return RotatedShape(shape_in=self.endplate.solid,
                            rotation_point=self.position.point,
                            vector=self.main.surface.position.orientation.Vx,
                            angle=radians(-self.cant),
                            label="right_side")

    @Part
    def mirrored_solid(self):
        """ This part creates a mirrored solid of the right endplate. It is
        mirrored in the mid plane of the spoiler. This is the end product of
         this class for the left endplate. """
        return MirroredShape(shape_in=self.solid.solid,
                             reference_point=XOY,
                             vector1=self.position.Vx,
                             vector2=self.position.Vz,
                             label="left_side")