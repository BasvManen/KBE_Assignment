from parapy.core import *
from parapy.geom import *

from kbeutils.geom.curve import Naca4AirfoilCurve, Naca5AirfoilCurve
from math import radians

import sys
import os

###############################################################################
# SECTION CLASS                                                               #
# In this file, a section profile is defined.                                 #
#                                                                             #
# Inputs:                                                                     #
# - airfoil name (Can be NACA 4 or 5 digit airfoil, or an airfoil from the    #
#   library)                                                                  #
# - Section chord                                                             #
###############################################################################


class Section(GeomBase):

    # NACA airfoil is selected if the name starts with 'naca', followed by a
    # four or five digit number. Else, the library is searched.
    airfoil_name = Input()

    chord = Input()

    @Attribute
    def airfoil_points(self):
        """ This attribute retrieves the coordinates from the data file in the
        library if an airfoil from the library is chosen. It returns a list
        with points, from which the airfoil curve is created. If a NACA
        airfoil is chosen, then this attribute will return nothing. """

        # Create the path for the airfoil file in the library.
        filename = sys.path[1] + '\\airfoils\\' + self.airfoil_name + '.dat'

        # Return nothing if the chosen file is not in the library.
        if not os.path.isfile(filename):
            return "A NACA airfoil is selected"

        # Open the file, read the coordinates and return them in a list.
        with open(filename, 'r') as f:
            points = []
            for line in f:
                x, y = line.split(' ', 1)
                points.append(Point(float(x), 0, float(y)))
        return points

    @Part(in_tree=False)
    def airfoil(self):
        """ Create the airfoil curve from the coordinates in the airfoil data
        file. If a NACA airfoil is chosen, create the curve directly using the
        functions from kbeutils. """
        return DynamicType(type=Naca4AirfoilCurve
                           # Check if NACA 4 airfoil is chosen
                           if self.airfoil_name[:4] == 'naca'
                           and len(self.airfoil_name[4:]) == 4
                           else Naca5AirfoilCurve
                           # Check if NACA 5 airfoil is chosen
                           if self.airfoil_name[:4] == 'naca'
                           and len(self.airfoil_name[4:]) == 5
                           # Make a curve from coordinates otherwise
                           else FittedCurve,
                           points=self.airfoil_points,
                           designation=self.airfoil_name[4:],
                           mesh_deflection=1e-5,
                           tolerance=1e-5,
                           position=XOY
                           )

    @Part(in_tree=False)
    def curve_origin(self):
        """ Create the curve from which the main plate can be build. This
        curve is scaled with the chord and rotated upside-down, such that
        the resulting force will point downwards. Please note that this curve
        is placed at the origin of the axis system. """
        return RotatedCurve(curve_in=ScaledCurve(curve_in=self.airfoil,
                                                 reference_point=XOY,
                                                 factor=self.chord
                                                 ),
                            rotation_point=XOY,
                            vector=self.position.Vx,
                            angle=radians(180))

    @Part
    def curve(self):
        """ Transform the scaled and rotated curve to the desired position and
        orientation. This is the final output curve of the Section class. """
        return TransformedCurve(curve_in=self.curve_origin,
                                from_position=XOY,
                                to_position=self.position
                                )
