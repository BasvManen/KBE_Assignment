from parapy.core import *
import kbeutils.avl as avl

###############################################################################
# AVL SECTION CLASS                                                           #
# In this file, the AVL sections used to create an AVL surface are defined    #
#                                                                             #
# Inputs:                                                                     #
# - The section curves of the aerodynamic surface.                            #
###############################################################################


class AVLSections(Base):
    sections = Input()

    @Part
    def plate_sections(self):
        """This part returns the AVL section. It is a list with the same length
        as the input list of curves. """
        return avl.SectionFromCurve(quantify=len(self.sections),
                                    curve_in=self.sections[child.index].curve)
