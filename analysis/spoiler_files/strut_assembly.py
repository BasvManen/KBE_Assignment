from analysis.spoiler_files import StrutAirfoil, StrutPlate
from parapy.core import Input, Attribute, Part, child, DynamicType
from parapy.core.validate import *
from parapy.geom import *
from math import sin, cos, radians, floor


class Struts(GeomBase):

    # Strut Inputs
    strut_amount = Input(2, validator=GreaterThanOrEqualTo(2))
    strut_airfoil_shape = Input(True, validator=OneOf([True, False]))
    strut_lat_location = Input(validator=Range(limit1=0.1, limit2=1.0))
    strut_height = Input(validator=Positive)
    strut_chord_fraction = Input(validator=Range(0.3, 1.0))
    strut_thickness = Input(validator=Positive)
    strut_sweep = Input(validator=Range(-60., 60.))
    strut_cant = Input(validator=Range(-30., 30.))
    main = Input()

    # Calculate the strut location
    @Attribute
    def strut_y_position(self):
        amount = self.strut_amount - floor(self.strut_amount / 2)
        y_translation = []
        for i in range(amount):
            if self.strut_amount % 2 == 0:
                y_translation.append(self.strut_lat_location
                                     * self.main.span
                                     / (self.strut_amount - 1) / 2 * (
                                             2 * i + 1))
            else:
                if i == 0:
                    y_translation.append(self.strut_thickness)
                else:
                    y_translation.append(self.strut_lat_location
                                         * self.main.span
                                         / (self.strut_amount - 1) * i)
        return y_translation

    # Define the struts (part)
    @Part(in_tree=False)
    def struts(self):
        return DynamicType(type=StrutAirfoil if self.strut_airfoil_shape
        else StrutPlate,
                           chord_fraction=self.strut_chord_fraction,
                           strut_lat_location=self.strut_lat_location,
                           strut_height=self.strut_height,
                           strut_thickness=self.strut_thickness,
                           strut_sweepback_angle=self.strut_sweep,
                           strut_cant_angle=self.strut_cant,
                           main=self.main)

    # Define the struts for the mid_strut
    @Part(in_tree=False)
    def struts_no_cant(self):
        return DynamicType(type=StrutAirfoil if self.strut_airfoil_shape
        else StrutPlate,
                           chord_fraction=self.strut_chord_fraction,
                           strut_lat_location=self.strut_lat_location,
                           strut_height=self.strut_height,
                           strut_thickness=self.strut_thickness,
                           strut_sweepback_angle=self.strut_sweep,
                           strut_cant_angle=0.,
                           main=self.main)

    # Translate strut to correct location, this is done with TranslatedShape
    # to make it work with both airfoil and filleted strut shapes.
    @Part(in_tree=False)
    def translated_strut(self):
        return TranslatedShape(quantify=self.strut_amount
                                        - floor(self.strut_amount / 2),
                               shape_in=self.struts_no_cant.strut if self.strut_amount % 2 != 0 and child.index == 0 else self.struts.strut,
                               displacement=Vector(x=(self.main.chord
                                                      * cos(
                                           radians(self.main.angle))
                                                      - self.strut_chord_fraction
                                                      * self.main.chord *
                                                      cos(radians(
                                                          self.main.angle)))
                                                     / 2,
                                                   y=self.strut_y_position[
                                                       child.index]))

    # Initialise subtraction of the solid at the main plate lower surface by
    # cutting the solid into several pieces.
    @Part(in_tree=False)
    def partitioned_solid(self):
        return PartitionedSolid(quantify=self.strut_amount
                                         - floor(self.strut_amount / 2),
                                solid_in=self.main.surface,
                                tool=self.translated_strut[child.index],
                                keep_tool=True,
                                mesh_deflection=1e-4)

    # Create part of the strut from the subtracted solid
    @Part
    def struts_right(self):
        return TranslatedShape(quantify=self.strut_amount
                                        - floor(self.strut_amount / 2) - self.strut_amount % 2,
                               shape_in=
                               self.partitioned_solid[child.index + self.strut_amount % 2].solids[3],
                               displacement=Vector(0., 0., 0.))

    @Part
    def struts_left(self):
        return MirroredShape(quantify=self.strut_amount
                                      - floor(self.strut_amount / 2) - self.strut_amount % 2,
                             shape_in=self.struts_right[child.index],
                             reference_point=Point(0., 0., 0.),
                             vector1=Vector(1., 0., 0.),
                             vector2=Vector(0., 0., 1.))

    @Part
    def strut_mid(self):
        return TranslatedShape(shape_in=
                               self.partitioned_solid[0].solids[3],
                               displacement=Vector(0., -self.strut_thickness,
                                                   0.),
                               hidden=True if self.strut_amount % 2 == 0 else False)