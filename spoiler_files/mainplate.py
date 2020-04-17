from parapy.core import *
from parapy.geom import *

from spoiler_files.section import Section
import kbeutils.avl as avl


class MainPlate(GeomBase):

    airfoil_mid = Input()
    airfoil_tip = Input()
    span = Input()
    chord = Input()
    angle = Input()
    
    @Attribute
    def airfoil_names(self):
        return self.airfoil_mid, self.airfoil_tip

    @Attribute
    def section_positions(self):
        mid_position = self.position
        tip_position = self.position.translate('y', self.span/2)
        return mid_position, tip_position

    @Part
    def sections(self):
        return Section(quantify=2,
                       airfoil_name=self.airfoil_names[child.index],
                       chord=self.chord,
                       angle=self.angle,
                       position=self.section_positions[child.index])

    @Part
    def surface(self):
        return LoftedShell(profiles=[section.curve
                                     for section in self.sections],
                           ruled=True)

    @Part
    def surface_mirrored(self):
        return MirroredSurface(surface_in=self.surface.faces[0],
                               reference_point=self.position.point,
                               vector1=self.position.Vx,
                               vector2=self.position.Vz)

    @Part
    def avl_surface(self):
        return avl.Surface(name="Main Plate",
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.cosine,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.cosine,
                           y_duplicate=self.position.point[1],
                           sections=[section.avl_section
                                     for section in self.sections])


if __name__ == '__main__':
    from parapy.gui import display
    obj = MainPlate(airfoil_mid='9412',
                    airfoil_tip='7408',
                    span=3000,
                    chord=800,
                    angle=0)
    display(obj)