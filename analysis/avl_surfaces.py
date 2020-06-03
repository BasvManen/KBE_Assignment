from parapy.core import *
import kbeutils.avl as avl


class AVLSurfaces(Base):

    number = Input()
    duplicate = Input()
    sections = Input()
    angle = Input()

    @Part
    def surface(self):
        return avl.Surface(name="Main Plate",
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.equal,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.equal,
                           y_duplicate=self.duplicate,
                           sections=[section for section in self.sections],
                           angle=self.angle)