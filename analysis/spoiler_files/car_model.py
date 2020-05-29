from parapy.exchange.step import STEPReader
from parapy.core import Input, Attribute, Part, child
from parapy.geom import *
from math import radians

import numpy as np
import os
import sys

DIR = os.path.dirname(__file__)


class Car(GeomBase):
    # step_file = Input()

    length_car = Input()
    width_car = Input()

    # @Attribute
    # def car_file(self):
    #     return STEPReader(filename=sys.path[1] + '\\inputs\\'
    #                                + self.step_file + '.stp').children
    #
    # @Part
    # def solids(self):
    #     return TranslatedShape(
    #         quantify=len(self.car_file[0].children[1].children),
    #         shape_in=
    #         self.car_file[0].children[1].children[child.index].solids[0],
    #         displacement=Vector(0., 0., 0.))
    #
    # @Part
    # def shells(self):
    #     return SewnShell(
    #         quantify=len(self.car_file[0].children[0].children),
    #         built_from=
    #         self.car_file[0].children[0].children[child.index])

    @Attribute
    def positions(self):
        x_curves = np.array([0, 0.0563, 0.1958, 0.2925, 0.5000, 0.5625, 0.9375,
                             1.0000]) * self.length_car
        x_wheels = np.array([0.1958, 0.7833]) * self.length_car
        x_spoiler = 0.8688 * self.length_car
        return x_curves, x_wheels, x_spoiler

    @Attribute
    def heights(self):
        height_curves = np.array([0.08375, 0.11667, 0.13625, 0.15625, 0.225,
                                  0.23542, 0.17125, 0.16292]) * self.length_car
        return height_curves

    @Attribute
    def wheels_properties(self):
        height_wheels = 180.
        radius_wheels = 300.
        width_wheels = 80.
        return height_wheels, radius_wheels, width_wheels

    @Part(in_tree=False)
    def curves(self):
        return Rectangle(quantify=8,
                         width=self.heights[child.index],
                         length=self.width_car,
                         position=translate(self.position,
                                            "z",
                                            -self.positions[0][child.index]),
                         centered=False)

    @Attribute
    def chamfered_vertices(self):
        v11, v12, v13, v14 = self.curves[4].vertices
        v21, v22, v23, v24 = self.curves[5].vertices

        table1 = ((v12, v12.on_edges[0], self.heights[4] * 0.6,
                   0.05 * self.width_car),
                  (v13, v13.on_edges[0], 0.05 * self.width_car,
                   self.heights[4] * 0.6))
        table2 = ((v22, v22.on_edges[0], self.heights[5] * 0.6,
                   0.05 * self.width_car),
                  (v23, v23.on_edges[0], 0.05 * self.width_car,
                   self.heights[5] * 0.6))

        return table1, table2

    @Part(in_tree=False)
    def chamfered_curve(self):
        return ChamferedWire(quantify=8,
                             built_from=self.curves[child.index],
                             vertex_table=self.chamfered_vertices[
                                 child.index - 4] if child.index == 4 or child.index == 5 else (
                                 (self.curves[child.index].vertices[1],
                                  self.curves[child.index].vertices[
                                      1].on_edges[0],
                                  self.heights[child.index] * 0.6,
                                  0.01 * self.width_car), (
                                     self.curves[child.index].vertices[2],
                                     self.curves[child.index].vertices[
                                         2].on_edges[0],
                                     0.01 * self.width_car,
                                     self.heights[child.index] * 0.6)))

    @Part(in_tree=False)
    def lofted_car(self):
        return LoftedSolid(profiles=self.chamfered_curve,
                           mesh_deflection=1e-4)

    @Attribute
    def edges(self):
        table = []
        edge_index = self.lofted_car.edges
        edge_radius = np.array([0.04166667, 0., 0.01041667, 0., 0.04166667,
                                0.02083333, 0.01041667, 0.02083333, 0.02083333,
                                0.02083333,
                                0.04166667, 0., 0.01041667, 0.04166667, 0.,
                                0.01041667, 0., 0.]) * self.length_car
        for i in range(len(edge_radius)):
            if edge_radius[i] != 0.:
                table_instance = (edge_index[i], edge_radius[i])
                table.append(table_instance)

        return table

    @Part(in_tree=False)
    def filleted_car(self):
        return FilletedSolid(built_from=self.lofted_car,
                             edge_table=self.edges,
                             mesh_deflection=1e-4)

    @Part(in_tree=False)
    def wheel(self):
        return FilletedSolid(
            built_from=TranslatedShape(shape_in=RotatedShape(shape_in=
                                                             Cylinder(radius=
                                                                      self.wheels_properties[
                                                                          1],
                                                                      height=300.),
                                                             rotation_point=self.position,
                                                             vector=Vector(1,
                                                                           0,
                                                                           0),
                                                             angle=radians(
                                                                 90)),
                                       displacement=
                                       Vector(self.wheels_properties[0],
                                              300.,
                                              -self.positions[1][0])),
            radius=30.)

    @Attribute
    def wheel_attributes(self):
        wheel1 = self.wheel
        wheel2 = TranslatedShape(shape_in=wheel1,
                                 displacement=Vector(0.,
                                                     0.,
                                                     self.positions[1][0]
                                                     - self.positions[1][1]))
        wheel3 = MirroredShape(shape_in=wheel1,
                               reference_point=Point(0, self.width_car / 2, 0),
                               vector1=Vector(1, 0, 0),
                               vector2=Vector(0, 0, 1))
        wheel4 = MirroredShape(shape_in=wheel2,
                               reference_point=Point(0, self.width_car / 2, 0),
                               vector1=Vector(1, 0, 0),
                               vector2=Vector(0, 0, 1))
        return [wheel1, wheel2, wheel3, wheel4]

    @Part
    def wheels(self):
        return (Solid(quantify=4,
                      built_from=self.wheel_attributes[child.index]))

    @Attribute
    def tools(self):
        tool1 = TranslatedShape(shape_in=
                                RotatedShape(shape_in=
                                             Cylinder(radius=
                                                      self.wheels_properties[
                                                          1] + 10.,
                                                      height=400.),
                                             rotation_point=self.position,
                                             vector=Vector(1, 0, 0),
                                             angle=radians(90)),
                                displacement=
                                Vector(self.wheels_properties[0],
                                       299.,
                                       -self.positions[1][0]))
        tool2 = TranslatedShape(shape_in=tool1,
                                displacement=Vector(0.,
                                                    0.,
                                                    self.positions[1][0]
                                                    - self.positions[1][1]))
        tool3 = MirroredShape(shape_in=tool1,
                              reference_point=Point(0, self.width_car / 2, 0),
                              vector1=Vector(1, 0, 0),
                              vector2=Vector(0, 0, 1))
        tool4 = MirroredShape(shape_in=tool2,
                              reference_point=Point(0, self.width_car / 2, 0),
                              vector1=Vector(1, 0, 0),
                              vector2=Vector(0, 0, 1))
        return [tool1, tool2, tool3, tool4]

    @Part
    def subtracted_car(self):
        return SubtractedSolid(shape_in=self.filleted_car,
                               tool=self.tools,
                               mesh_deflection=1e-4)


if __name__ == '__main__':
    from parapy.gui import display

    obj = Car(length_car=4800.,
              width_car=2050.)
    display(obj)
