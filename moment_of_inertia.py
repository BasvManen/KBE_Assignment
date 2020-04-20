from spoiler_files import MainPlate
from spoiler_files.section import Section
from parapy.core import *
from parapy.geom import *
from math import atan, cos, sin, tan, radians, pi

mid_airfoil_test = '9412'
tip_airfoil_test = '9408'
spoiler_span_test = 3000.
spoiler_chord_test = 800.
spoiler_angle_test = 20.
tip_cant_test = 15.


class MomentOfInertia(GeomBase):
    airfoil_mid = Input('9412')
    airfoil_tip = Input('9412')
    span = Input(3000)
    chord = Input(800)
    angle = Input(0)
    tip_cant = Input(0)
    thickness = Input(20)
    n_discretise = Input(200)

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
        return crv.equispaced_points(self.n_discretise)

    @Attribute
    def amount_of_lines(self):
        return self.n_discretise - 1

    @Part
    def lines_on_airfoil(self):
        return LineSegment(quantify=self.amount_of_lines,
                           start=self.coordinates_sections_points[child.index],
                           end=self.coordinates_sections_points[child.index + 1])

    # @Part
    # def lines_on_airfoil(self):
    #     return LineSegment(quantify=self.amount_of_lines,
    #                        start=Point(0, 0, 0),
    #                        end=Point(103.92, 0, 60))

    @Attribute
    def centroid_calculation(self):
        x = 0
        y = self.lines_on_airfoil[0].position.y
        z = 0
        for i in range(self.amount_of_lines):
            x = x + (self.lines_on_airfoil[i].midpoint.x * self.lines_on_airfoil[i].length * self.thickness) \
                / ((self.amount_of_lines) * self.lines_on_airfoil[i].length * self.thickness)
            z = z + (self.lines_on_airfoil[i].midpoint.z * self.lines_on_airfoil[i].length * self.thickness) \
                / ((self.amount_of_lines) * self.lines_on_airfoil[i].length * self.thickness)
        return x, y, z

    @Part
    def centroid(self):
        return Point(self.centroid_calculation[0], self.centroid_calculation[1], self.centroid_calculation[2])

    @Attribute
    def moment_inertia_displaced_area(self):
        ix_area = 0
        iz_area = 0
        ixz_area = 0
        for i in range(self.amount_of_lines):
            ix_area = ix_area + (self.lines_on_airfoil[i].length * self.thickness) \
                      * (self.lines_on_airfoil[i].midpoint.z - self.centroid_calculation[2]) ** 2
            iz_area = iz_area + (self.lines_on_airfoil[i].length * self.thickness) \
                      * (self.lines_on_airfoil[i].midpoint.x - self.centroid_calculation[0]) ** 2
            ixz_area = ixz_area + (self.lines_on_airfoil[i].length * self.thickness) \
                      * (self.lines_on_airfoil[i].midpoint.z - self.centroid_calculation[2]) \
                      * (self.lines_on_airfoil[i].midpoint.x - self.centroid_calculation[0])
        return ix_area, iz_area, ixz_area

    @Attribute
    def moment_inertia_area_rectangle(self):
        ix = 0
        iz = 0
        ixz = 0
        for i in range(self.amount_of_lines):
            iu = 1 / 12 * self.lines_on_airfoil[i].length * self.thickness ** 3
            iw = 1 / 12 * self.thickness * self.lines_on_airfoil[i].length ** 3
            theta = radians(90) if abs(self.lines_on_airfoil[i].point1.x - self.lines_on_airfoil[i].point2.x) < (10 ** -10) \
                else atan((self.lines_on_airfoil[i].point1.z - self.lines_on_airfoil[i].point2.z)
                          / (self.lines_on_airfoil[i].point1.x - self.lines_on_airfoil[i].point2.x))
            ix = ix + ((iu + iw) / 2 + (iu - iw) / 2 * cos(2 * theta))
            iz = iz + ((iu + iw) / 2 - (iu - iw) / 2 * cos(2 * theta))
            ixz = ixz + ((iu - iw) / 2 * sin(2 * theta))
        return ix, iz, ixz
    
    @Attribute
    def moment_inertia_total(self):
        ix_total = self.moment_inertia_displaced_area[0] + self.moment_inertia_area_rectangle[0]
        iz_total = self.moment_inertia_displaced_area[1] + self.moment_inertia_area_rectangle[1]
        ixz_total = self.moment_inertia_displaced_area[2] + self.moment_inertia_area_rectangle[2]
        return ix_total, iz_total, ixz_total


if __name__ == '__main__':
    from parapy.gui import display

    obj = MomentOfInertia(label='points')
    display(obj)
