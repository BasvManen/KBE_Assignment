from parapy.core import *
from parapy.geom import *

from section import Section
from math import radians


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


if __name__ == '__main__':
    from parapy.gui import display
    obj = MainPlate(airfoil_mid='0012',
                    airfoil_tip='0008',
                    span=3,
                    chord=0.8,
                    angle=-20)
    display(obj)