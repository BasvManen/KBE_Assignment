from parapy.core import *
from parapy.geom import *
from kbeutils.geom.curve import Naca5AirfoilCurve, Naca4AirfoilCurve
import kbeutils.avl as avl

from math import radians

# SECTION CLASS
# In this file, the section profiles are defined


class Section(GeomBase):

    # INPUTS
    airfoil_name = Input()
    chord = Input()
    angle = Input()

    # Create a NACA 4 or NACA 5 profile from the airfoil name
    @Part(in_tree=False)
    def airfoil(self):
        return DynamicType(type=(Naca5AirfoilCurve
                                 if len(self.airfoil_name) == 5
                                 else Naca4AirfoilCurve),
                           designation=self.airfoil_name)

    # Scale the profile with the chord length of the real profile
    @Part(in_tree=False)
    def curve_flat(self):
        return ScaledCurve(curve_in=self.airfoil,
                           reference_point=self.position.point,
                           factor=self.chord)

    # Rotate the profile with the spoiler angle
    @Part(in_tree=False)
    def curve_up(self):
        return RotatedCurve(curve_in=self.curve_flat,
                            rotation_point=self.position,
                            vector=self.position.Vy,
                            angle=radians(self.angle))

    # Rotate the profile 180 degrees, so that it is upside down
    @Part
    def curve(self):
        return RotatedCurve(curve_in=self.curve_up,
                            rotation_point=self.position,
                            vector=self.position.Vx,
                            angle=radians(180))

    # Define the section in AVL (required to create the AVL surface)
    @Part(in_tree=False)
    def avl_section(self):
        return avl.SectionFromCurve(curve_in=self.curve_up, angle=self.angle)
