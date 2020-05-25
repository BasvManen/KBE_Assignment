from parapy.core import *
from parapy.geom import *

from analysis.spoiler_files.section import Section
from math import radians

###############################################################################
# MAIN PLATE CLASS                                                            #
# In this file, the spoiler main plate is defined                             #
#                                                                             #
# Inputs:                                                                     #
# - airfoils, defined in a list of strings. See documentation of the Section  #
#   class for profile definition.                                             #
# - Span of the main plate                                                    #
# - Chord of the main plate                                                   #
# - Angle of the main plate, positive defined upwards                         #
# - Cant angle of the tip, positive defined inwards                           #
###############################################################################


class MainPlate(GeomBase):

    # List of strings, distributed equidistant along the span. First section is
    # the mid of the main plate and the last section is the tip of the main
    # plate. At least two sections are required.
    airfoils = Input()

    span = Input()
    chord = Input()
    angle = Input()
    tip_cant = Input()

    @Attribute
    def wetted_area(self):
        """ This attribute retrieves the area of the main plate solid. This is
        used as wetted area for the friction drag calculation. """
        return 2 * self.surface.solids[0].area

    @Part(in_tree=False)
    def sections(self):
        """ Create the sections based on the airfoils list input. They are
        translated such that the first section is at the mid and the last
        section is at the tip of the main plate. The other sections are placed
        equidistant from mid to tip. """
        return Section(quantify=len(self.airfoils),
                       airfoil_name=self.airfoils[child.index],
                       chord=self.chord,
                       position=self.position if child.index == 0
                       # Position the mid section at the mid of the main plate
                       else translate(child.previous.position,
                                      'y',
                                      0.5*self.span/(len(self.airfoils)-1))
                       if child.index != len(self.airfoils)-1
                       # Position the intermediate sections equidistant
                       else rotate(translate(child.previous.position,
                                             'y',
                                             0.5*self.span /
                                             (len(self.airfoils)-1)),
                                   self.position.Vx,
                                   radians(-self.tip_cant))
                       # For the last section, also account for the tip cant
                       )

    @Part
    def surface(self):
        """ Create the main plate based on the sections defined in the
        sections part. The main plate is then rotated based on the spoiler
        angle given as input. """
        return RotatedShape(shape_in=LoftedSolid(profiles=[section.curve
                                                 for section in self.sections],
                                                 ),
                            # Firstly, create a solid from the sections
                            rotation_point=self.position.point,
                            vector=self.position.Vy,
                            angle=radians(-self.angle),
                            mesh_deflection=1e-4,
                            # Rotate the solid to the desired spoiler angle
                            label="right_side"
                            )

    @Part(in_tree=False)
    def lofted_shell(self):
        """ Create a lofted shell of the main plate based on the sections
        defined in the sections part. This instance is later used in the
        structural analysis of the spoiler. """
        return RotatedShape(shape_in=LoftedShell(profiles=[section.curve
                                                 for section in self.sections],
                                                 ),
                            # Firstly, create a shell from the sections
                            rotation_point=self.position.point,
                            vector=self.position.Vy,
                            angle=radians(-self.angle),
                            mesh_deflection=1e-4,
                            # Rotate the shell to the desired spoiler angle
                            )

    @Part
    def mirrored_surface(self):
        """ Mirror the surface (which is defined from the mid position to the
        tip position) in order to obtain the entire main plate. """
        return MirroredShape(shape_in=self.surface,
                             reference_point=self.position.point,
                             vector1=self.position.Vx,
                             vector2=self.position.Vz,
                             # Mirror the shape in the XZ-plane
                             label="left_side"
                             )


if __name__ == '__main__':
    from parapy.gui import display
    obj = MainPlate(label="mainplate",
                    airfoils=["test", "naca6408", "naca6406"],
                    span=4,
                    chord=2,
                    angle=10,
                    tip_cant=15)
    display(obj)
