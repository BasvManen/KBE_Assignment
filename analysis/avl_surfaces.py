from parapy.core import *
import kbeutils.avl as avl
from analysis.AVL_main import number_to_letter


class AVLSurfaces(Base):

    number = Input()
    duplicate = Input()
    sections = Input()
    angle = Input()

    @Part
    def surface(self):
        return avl.Surface(name=number_to_letter(self.number),
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.equal,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.equal,
                           y_duplicate=self.duplicate,
                           sections=[section for section in self.sections],
                           angle=self.angle)

