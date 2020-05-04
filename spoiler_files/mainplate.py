from parapy.core import *
from parapy.geom import *
from math import sin, cos, radians

import kbeutils.avl as avl
from spoiler_files.section import Section


class MainPlate(GeomBase):

    airfoil_mid = Input()
    airfoil_tip = Input()
    span = Input()
    chord = Input()
    angle = Input()
    tip_cant = Input()
    
    @Attribute
    def airfoil_names(self):
        return self.airfoil_mid, self.airfoil_tip

    @Attribute
    def section_positions(self):
        mid_position = self.position
        tip_position = self.position.translate('y', self.span/2)
        return tip_position, mid_position

    @Part(in_tree=False)
    def sections(self):
        return Section(quantify=2,
                       airfoil_name=self.airfoil_names[child.index],
                       chord=self.chord,
                       angle=self.angle,
                       position=self.section_positions[child.index])

    @Part(in_tree=False)
    def surface_whole(self):
        return LoftedSolid(profiles=[section.curve
                                     for section in self.sections],
                           ruled=True)

    @Part(in_tree=False)
    def cutting_plane(self):
        return Plane(translate(XOY, 'x', self.chord*cos(radians(self.angle)),
                               'y', self.span/2,
                               'z', self.chord*sin(radians(self.angle))),
                     normal=rotate(VY, VX, -self.tip_cant, deg=True))

    @Part(in_tree=False)
    def half_space_solid(self):
        return HalfSpaceSolid(self.cutting_plane, Point(0, self.span, 0))

    @Part
    def surface(self):
        return SubtractedSolid(shape_in=self.surface_whole, tool=self.half_space_solid)

    @Part
    def surface_mirrored(self):
        return MirroredShape(shape_in=self.surface,
                             reference_point=self.position.point,
                             vector1=self.position.Vx,
                             vector2=self.position.Vz)

    @Part
    def avl_surface(self):
        return avl.Surface(name="Main Plate",
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.cosine,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.equal,
                           y_duplicate=self.position.point[1],
                           sections=[section.avl_section
                                     for section in self.sections])


if __name__ == '__main__':
    from parapy.gui import display
    obj = MainPlate(airfoil_mid='9412',
                    airfoil_tip='7408',
                    span=3000,
                    chord=800,
                    angle=0,
                    tip_cant=0)
    display(obj)