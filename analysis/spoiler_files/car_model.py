from parapy.core import Input, Attribute, Part, child
from parapy.geom import *
from math import radians, atan, pi

import numpy as np

###############################################################################
# CAR MODEL CLASS                                                             #
# In this file, a simple car model is defined                                 #
#                                                                             #
# Inputs:                                                                     #
# - Length of the car                                                         #
# - Width of the car                                                          #
# - Maximum height of the car (located at the cockpit)                        #
# - The ratio from the maximum height of the car, to the back of the car      #
###############################################################################


class Car(GeomBase):

    length_car = Input()
    width_car = Input()
    max_height_car = Input()
    middle_to_back_height_ratio = Input()

    @Attribute
    def positions(self):
        """ This attribute returns the x_positions of the curves for the
        lofted car solid, as well as the x location of the wheels and
        spoiler position. All positions are based on a generic
        high-performance LM GTE Pro car, and are scaled with the inputted
        car length. """
        x_curves = np.array([0, 0.0563, 0.1958, 0.2925, 0.5000, 0.5625, 0.9375,
                             1.0000]) * self.length_car
        x_wheels = np.array([0.1958, 0.8133]) * self.length_car
        x_spoiler = 0.8688 * self.length_car
        return x_curves, x_wheels, x_spoiler

    @Attribute
    def heights(self):
        """ This attribute returns the height of the curves for the lofted
        car solid. All values are based on a generic high-performance LM GTE
        Pro car, and are scaled with the inputted maximum car height and
        middle to back height ratio. """
        height_curves = np.array(
            [0.35574718, 0.49558236, 0.57875287, 0.66370742, 0.95573868,
             1., 0.72742333, 0.69203976]) * self.max_height_car
        height_curves[6] = height_curves[5] / self.middle_to_back_height_ratio
        height_curves[7] = height_curves[6] / 1.05
        return height_curves

    @Attribute
    def avl_angle(self):
        """ This attribute calculates the angle of deflection for the AVL
        analysis, due to the car body. It is assumed that the deflection
        angle is dependent on the aft height change of the body. """
        dif_height = (self.heights[5] - self.heights[7])
        dif_position = (self.positions[0][7] - self.positions[0][5])
        angle = atan(dif_height / dif_position) / 1.5 * 180 / pi
        return angle

    @Attribute
    def wheels_properties(self):
        """ This attribute determines the wheel height, radius and width. """
        height_wheels = 180.
        radius_wheels = 300.
        width_wheels = 80.
        return height_wheels, radius_wheels, width_wheels

    @Part(in_tree=False)
    def curves(self):
        """ This part returns several rectangular curves, which are
        later chamfered and used for the lofted car solid. The curves are
        based on positions, heights and width_car. """
        return Rectangle(quantify=8,
                         width=self.heights[child.index],
                         length=self.width_car,
                         position=translate(self.position,
                                            "z",
                                            -self.positions[0][child.index]),
                         centered=False)

    @Attribute
    def chamfered_vertices(self):
        """ This attribute creates vertex_tables for the ChamferedCurve
        class, for the 4th and 5th index of curves. This is done to create
        some width change, where the cockpit of the car would be located. """
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
        """ This part creates the chamfered curves for the lofted car solid.
        Note that not only the 4th and 5th index of curves are chamfered,
        as this would lead to uneven edges and vertices of the curves,
        and thus problems with LoftedSolid. """
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
        """ This part created the lofted car solid from the chamfered
        curves. """
        return LoftedSolid(profiles=self.chamfered_curve,
                           mesh_deflection=1e-4)

    @Attribute
    def edges(self):
        """ This attribute creates an edge_table for the filleting of the
        lofted car solid. """
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
        """ This part fillets the lofted car solid, to create a finer car
        solid. """
        return FilletedSolid(built_from=self.lofted_car,
                             edge_table=self.edges,
                             mesh_deflection=1e-5)

    @Part(in_tree=False)
    def wheel(self):
        """ This attribute creates a single wheel instance, by rotating and
        translating a Cylinder solid, and later filleting it. """
        return FilletedSolid(
            built_from=
            TranslatedShape(shape_in=
                            RotatedShape(shape_in=
                                         Cylinder(radius=
                                                  self.wheels_properties[1],
                                                  height=300.,
                                                  position=self.position),
                                         rotation_point=self.position,
                                         vector=Vector(1, 0, 0),
                                         angle=radians(90)),
                            displacement=Vector(self.wheels_properties[0],
                                                300.,
                                                -self.positions[1][0])),
            radius=30.)

    @Attribute
    def wheel_attributes(self):
        """ This attribute directly defines a set of 4 wheels from the
        single wheel instance, all located at their right locations. """
        wheel1 = self.wheel
        wheel2 = TranslatedShape(shape_in=wheel1,
                                 displacement=Vector(0.,
                                                     0.,
                                                     self.positions[1][0]
                                                     - self.positions[1][1]))
        wheel3 = MirroredShape(shape_in=wheel1,
                               reference_point=translate(self.position,
                                                         "y",
                                                         self.width_car / 2),
                               vector1=Vector(1, 0, 0),
                               vector2=Vector(0, 0, 1))
        wheel4 = MirroredShape(shape_in=wheel2,
                               reference_point=translate(self.position,
                                                         "y",
                                                         self.width_car/2),
                               vector1=Vector(1, 0, 0),
                               vector2=Vector(0, 0, 1))
        return [wheel1, wheel2, wheel3, wheel4]

    @Part(in_tree=True)
    def wheels(self):
        """ This part creates the 4 wheels and rotates them into the right
        orientation for the Main assembly. """
        return RotatedShape(quantify=4,
                            shape_in=self.wheel_attributes[child.index],
                            rotation_point=self.position,
                            vector=Vector(0, 1, 0),
                            angle=radians(-90))

    @Attribute
    def tools(self):
        """ This attribute defines 4 cutout tools, to be used to create
        wheel bays from the filleted car solid. It uses cylinders with a
        slightly higher radius than the wheels. """
        tool1 = TranslatedShape(shape_in=
                                RotatedShape(shape_in=
                                             Cylinder(radius=
                                                      self.wheels_properties[
                                                          1] + 10.,
                                                      height=400.,
                                                      position=self.position),
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
                              reference_point=translate(self.position,
                                                        "y",
                                                        self.width_car / 2),
                              vector1=Vector(1, 0, 0),
                              vector2=Vector(0, 0, 1))
        tool4 = MirroredShape(shape_in=tool2,
                              reference_point=translate(self.position,
                                                        "y",
                                                        self.width_car / 2),
                              vector1=Vector(1, 0, 0),
                              vector2=Vector(0, 0, 1))
        return [tool1, tool2, tool3, tool4]

    @Part(in_tree=False)
    def subtracted_car(self):
        """ This part creates a subtracted solid from the filleted car and
        the tools, to create a car with wheel bays. """
        return SubtractedSolid(shape_in=self.filleted_car,
                               tool=self.tools,
                               mesh_deflection=1e-4)

    @Part
    def car_model(self):
        """ This part rotates the subtracted car, in order to have the right
        orientation for the Main assembly. """
        return RotatedShape(shape_in=self.subtracted_car,
                            rotation_point=self.position,
                            vector=Vector(0, 1, 0),
                            angle=radians(-90),
                            mesh_deflection=1e-5)
