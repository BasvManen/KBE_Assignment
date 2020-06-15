from analysis.spoiler_files import MainPlate, Endplates, Struts, Car
from parapy.core import Input, Attribute, Part, child, DynamicType
from parapy.core.validate import *
from parapy.geom import *
from math import sin, radians, tan
import os

DIR = os.path.dirname(__file__)

###############################################################################
# SPOILER ASSEMBLY CLASS                                                      #
# In this file, the spoiler geometry is assembled.                            #
#                                                                             #
# Inputs:                                                                     #
# - All geometry parameters as defined in the .dat input file.                #
###############################################################################


class Spoiler(GeomBase):
    # Main Plate Inputs
    spoiler_airfoils = Input()
    spoiler_span = Input(validator=Positive)
    spoiler_chord = Input(validator=Positive)
    spoiler_angle = Input(validator=Range(-60., 60.))
    plate_amount = Input(validator=GreaterThanOrEqualTo(1))
    plate_distance = Input(validator=Range(limit1=0.1, limit2=1.0))

    # Strut Inputs
    strut_amount = Input(2, validator=GreaterThanOrEqualTo(2))
    strut_airfoil_shape = Input(True, validator=OneOf([True, False]))
    strut_lat_location = Input(validator=Range(limit1=0.1, limit2=1.0))
    strut_height = Input(validator=Positive)
    strut_chord_fraction = Input(validator=Range(0.3, 1.0))
    strut_thickness = Input(validator=Positive)
    strut_sweep = Input(validator=Range(-60., 60.))
    strut_cant = Input(validator=Range(-30., 30.))

    # Endplate Inputs
    endplate_present = Input(True, validator=OneOf([True, False]))
    endplate_thickness = Input(validator=And(Positive))
    endplate_sweep = Input(validator=Range(-60., 60.))
    endplate_cant = Input(validator=Range(-60., 60.))

    # Car Inputs
    car_length = Input()
    car_width = Input()
    car_maximum_height = Input()
    car_middle_to_back_ratio = Input()

    @Attribute
    def reference_area(self):
        """ This attribute calculates the reference area of the spoiler,
        which is used as reference for the aerodynamic analysis. """
        return self.spoiler_chord * self.spoiler_span

    @Part
    def main_plate(self):
        """ This part returns the main plate(s) of the spoiler. """
        return MainPlate(quantify=self.plate_amount,
                         airfoils=self.spoiler_airfoils,
                         # The span needs to account for the endplate cant.
                         span=(self.spoiler_span -
                               sin(radians(self.endplate_cant)) * 1.8 *
                               (self.spoiler_chord*self.plate_distance) *
                               (self.plate_amount - 1 - child.index)),
                         chord=self.spoiler_chord,
                         angle=self.spoiler_angle,
                         tip_cant=self.endplate_cant,
                         # The position of the plates is determined by the
                         # input distance between the plates and the strut
                         # sweep angle.
                         position=translate(self.position,
                                            'z',
                                            self.spoiler_chord *
                                            self.plate_distance*child.index,
                                            'x',
                                            self.spoiler_chord *
                                            self.plate_distance*child.index *
                                            tan(radians(self.strut_sweep))))

    @Attribute
    def wetted_area(self):
        """ This attribute calculates the wetted area of the spoiler,
        which is used to calculate the friction drag. """
        return self.main_plate[0].wetted_area * self.plate_amount \
               + self.struts.struts.wetted_area * self.strut_amount + \
               (self.endplates.wetted_area if self.endplate_present else 0)

    @Part
    def struts(self):
        """ This part returns the struts of the spoiler. """
        return Struts(strut_amount=self.strut_amount,
                      strut_airfoil_shape=self.strut_airfoil_shape,
                      strut_lat_location=self.strut_lat_location,
                      strut_height=self.strut_height,
                      strut_chord_fraction=self.strut_chord_fraction,
                      strut_thickness=self.strut_thickness,
                      strut_sweep=self.strut_sweep,
                      strut_cant=self.strut_cant,
                      main=self.main_plate)

    @Attribute
    def endplate_height(self):
        """ This attribute calculates the vertical distance between the top
        and bottom of the plate(s). This is then defined as the endplate
        height. """
        z1 = self.main_plate[0].surface.edges[-1].bbox.bounds[2]
        z2 = self.main_plate[-1].surface.edges[-1].bbox.bounds[5]
        return z2, (z2 - z1)

    @Attribute
    def endplate_chord(self):
        """"  This attribute calculates the horizontal distance between the top
        and bottom of the plate(s). This is then defined as the endplate
        chord. """
        x1 = self.main_plate[0].surface.edges[-1].bbox.bounds[0]
        x2 = self.main_plate[-1].surface.edges[-1].bbox.bounds[3]
        return x2, (x2 - x1)

    @Part
    def endplates(self):
        """This part returns the endplates. """
        return DynamicType(type=Endplates,
                           chord=self.endplate_chord[1],
                           height=self.endplate_height[1],
                           thickness=self.endplate_thickness,
                           sweep=self.endplate_sweep,
                           cant=self.endplate_cant,
                           main=self.main_plate,
                           position=translate(self.position,
                                              'x', self.endplate_chord[0],
                                              'y', self.spoiler_span/2,
                                              'z', self.endplate_height[0]),
                           hide=False if self.endplate_present else True,
                           hidden=False if self.endplate_present else True)

    @Part
    def car_model(self):
        """ This part returns the car model. """
        return Car(length_car=self.car_length,
                   width_car=self.car_width,
                   max_height_car=self.car_maximum_height,
                   middle_to_back_height_ratio=self.car_middle_to_back_ratio,
                   position=translate(self.position,
                                      "x", -self.car_model.positions[0][6]
                                      + self.spoiler_chord
                                      * self.strut_chord_fraction
                                      - self.strut_height
                                      * tan(radians(self.strut_sweep)),
                                      "y", -self.car_width/2,
                                      "z", -self.car_model.heights[6]
                                      - self.strut_height + 35.))

