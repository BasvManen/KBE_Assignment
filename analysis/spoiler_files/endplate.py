from parapy.core import *
from parapy.geom import *

from math import sin, radians

###############################################################################
# ENDPLATE CLASS                                                              #
# In this file, the spoiler endplate is defined                               #
#                                                                             #
# Inputs:                                                                     #
# - Chord of the endplate                                                     #
# - Height of the endplate                                                    #
# - Thickness of the endplate                                                 #
# - Sweep angle of the endplate                                               #
###############################################################################


class Endplate(GeomBase):

    chord = Input()
    height = Input()
    thickness = Input()
    sweep = Input()

    @Attribute
    def wetted_area(self):
        """ This attribute retrieves the wetted area of the endplate, based on
        the solid property. """
        return self.solid.area

    @Part(in_tree=False)
    def upper_curve(self):
        """ This part defines the upper curve of the endplate. It is positioned
        at the origin of the local axis system in negative x-direction. """
        return Rectangle(width=self.chord,
                         length=self.thickness,
                         centered=False,
                         position=translate(self.position,
                                            'x', -self.chord)
                         )

    @Part(in_tree=False)
    def lower_curve(self):
        """ This part defines the lower curve of the endplate. It is positioned
         relative to the upper curve, based on height and sweep. """
        return Rectangle(width=self.chord,
                         length=self.thickness,
                         centered=False,
                         position=translate(self.upper_curve.position,
                                            'z', -self.height,
                                            'x', (-sin(radians(self.sweep))
                                                  * self.height))
                         )

    @Part
    def solid(self):
        """ This part is the resulting solid based on the upper and the lower
        curve. This is the end product of the endplate class. """
        return FilletedSolid(built_from=RuledSolid(profile1=self.upper_curve,
                                                   profile2=self.lower_curve),
                             radius=self.thickness/3)
