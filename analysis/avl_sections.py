from parapy.core import *
import kbeutils.avl as avl


class AVLSections(Base):
    sections = Input()

    @Part
    def plate_sections(self):
        return avl.SectionFromCurve(quantify=len(self.sections),
                                    curve_in=self.sections[child.index].curve)
