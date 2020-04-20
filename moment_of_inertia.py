from spoiler_files import MainPlate
from spoiler_files.section import Section
from parapy.core import *
from parapy.geom import *

mid_airfoil_test='9412'
tip_airfoil_test='9408'
spoiler_span_test=3000.
spoiler_chord_test=800.
spoiler_angle_test=20.
tip_cant_test = 15.


class MomentOfInertia(GeomBase):

    airfoil_mid = Input('9412')
    airfoil_tip = Input('9412')
    span = Input(3000)
    chord = Input(800)
    angle = Input(0)
    tip_cant = Input(0)
    thickness = Input(2)

    @Attribute
    def airfoil_names(self):
        return self.airfoil_mid, self.airfoil_tip

    @Attribute
    def section_positions(self):
        mid_position = self.position
        tip_position = self.position.translate('y', self.span / 2)
        return mid_position, tip_position

    @Part(in_tree=True)
    def sections(self):
        return Section(quantify=2,
                       airfoil_name=self.airfoil_names[child.index],
                       chord=self.chord,
                       angle=self.angle,
                       position=self.section_positions[child.index])

    @Attribute
    def coordinates_sections_points(self):
        crv = self.sections[0].curve
        return crv.equispaced_points(200)

    @Part
    def lines_on_airfoil(self):
        return LineSegment(quantify=len(self.coordinates_sections_points),
                           start=self.coordinates_sections_points[child.index],
                           end=self.coordinates_sections_points[child.index-1])




if __name__ == '__main__':
    from parapy.gui import display
    obj = MomentOfInertia(label='points')
    display(obj)