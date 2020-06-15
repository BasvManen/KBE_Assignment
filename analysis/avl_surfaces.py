from parapy.core import *
import kbeutils.avl as avl
from analysis.AVL_main import number_to_letter

###############################################################################
# AVL SURFACE CLASS                                                           #
# In this file, the AVL surface used in the aerodynamic analysis is created.  #
#                                                                             #
# Inputs:                                                                     #
# - The plate number, starting from the bottom plate with number 0.           #
# - Y-position of the surface mirror point.                                   #
# - AVL sections that define the aerodynamic surface.                         #
# - Angle of the surface, positive defined upwards.                           #
###############################################################################


class AVLSurfaces(Base):

    number = Input()
    duplicate = Input()
    sections = Input()
    angle = Input()

    @Part
    def surface(self):
        """This part returns an AVL surface with an unique name. This way,
        multiple plates can be distinguished when multiple main plates are
        present. """
        return avl.Surface(name=number_to_letter(self.number),
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.equal,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.equal,
                           y_duplicate=self.duplicate,
                           sections=[section for section in self.sections],
                           angle=self.angle)

