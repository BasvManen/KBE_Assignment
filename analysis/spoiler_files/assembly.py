from analysis.spoiler_files import MainPlate, Endplates, Struts, Car
from parapy.core import Input, Attribute, Part, child, DynamicType
from parapy.core.validate import *
from parapy.geom import *
from parapy.exchange import STEPWriter
import kbeutils.avl as avl
from math import sin, cos, radians, floor
import os

DIR = os.path.dirname(__file__)


# MAIN SPOILER CLASS
# In this file, the main spoiler geometry will be defined


class Spoiler(GeomBase):
    # Main Plate Inputs
    spoiler_airfoils = Input()
    spoiler_span = Input(validator=Positive)
    spoiler_chord = Input(validator=Positive)
    spoiler_angle = Input(validator=Range(-60., 60.))

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

    # Calculate reference area based on chord and span
    @Attribute
    def reference_area(self):
        return self.spoiler_chord * self.spoiler_span

    # Define the main plate (part)
    @Part
    def main_plate(self):
        return MainPlate(airfoils=self.spoiler_airfoils,
                         span=self.spoiler_span,
                         chord=self.spoiler_chord,
                         angle=self.spoiler_angle,
                         tip_cant=self.endplate_cant)

    # Define wetted area
    @Attribute
    def wetted_area(self):
        return self.main_plate.wetted_area + self.struts.wetted_area + \
               (self.endplates.wetted_area if self.endplate_present else 0)

    @Part
    def struts(self):
        return Struts(strut_amount=self.strut_amount,
                      strut_airfoil_shape=self.strut_airfoil_shape,
                      strut_lat_location=self.strut_lat_location,
                      strut_height=self.strut_height,
                      strut_chord_fraction=self.strut_chord_fraction,
                      strut_thickness=self.strut_thickness,
                      strut_sweep=self.strut_sweep,
                      strut_cant=self.strut_cant,
                      main=self.main_plate)

    # Calculate the endplate location
    @Attribute
    def endplate_position(self):
        return self.position.translate("z",
                                       self.spoiler_chord *
                                       sin(radians(self.spoiler_angle)))

    # Calculate the endplate height based on spoiler angle and chord
    @Attribute
    def endplate_height(self):
        camber = float(self.tip_airfoil[0]) \
            if len(self.tip_airfoil) == 4 else 9.
        pos = float(self.tip_airfoil[1]) / 10
        thickness = float(self.tip_airfoil[2:4]) \
            if len(self.tip_airfoil) == 4 else float(self.tip_airfoil[3:5])
        height_frac_1 = sin(radians(self.spoiler_angle))
        height_frac_2 = (camber / 100. + 0.5 * thickness / 100.) * \
                        cos(radians(self.spoiler_angle))

        return (height_frac_1 + height_frac_2) * self.spoiler_chord

    # Define the endplates (part)
    @Part
    def endplates(self):
        return DynamicType(type=Endplates,
                           spoiler_span=self.spoiler_span,
                           spoiler_height=self.spoiler_chord *
                                          sin(radians(self.spoiler_angle)),
                           chord=self.spoiler_chord *
                                 cos(radians(self.spoiler_angle)),
                           height=self.endplate_height,
                           thickness=self.endplate_thickness,
                           sweepback_angle=self.endplate_sweep,
                           cant_angle=self.endplate_cant,
                           position=self.endplate_position,
                           hidden=False if self.endplate_present else True)

    # Find the AVL surfaces in the part files
    @Attribute
    def avl_surfaces(self):
        return self.find_children(lambda o: isinstance(o, avl.Surface))

    # Define the AVL configuration
    @Part
    def avl_configuration(self):
        return avl.Configuration(name='Spoiler',
                                 reference_area=self.reference_area,
                                 reference_span=self.spoiler_span,
                                 reference_chord=self.spoiler_chord,
                                 reference_point=self.position.point,
                                 surfaces=self.avl_surfaces,
                                 mach=0.0)

    # Define the STEP file nodes
    @Attribute
    def nodes_for_stepfile(self):
        if self.endplate_present:
            nodes = [self.main_plate.surface,
                     self.main_plate.surface_mirrored,
                     self.struts.strut_right,
                     self.struts.strut_left,
                     self.endplates.endplate_right,
                     self.endplates.endplate_left]
        else:
            nodes = [self.main_plate.surface,
                     self.main_plate.surface_mirrored,
                     self.struts.strut_right,
                     self.struts.strut_left]
        return nodes

    # Write the STEP components from the nodes
    @Part
    def step_writer_components(self):
        return STEPWriter(default_directory=DIR,
                          nodes=self.nodes_for_stepfile)

    @Part
    def car(self):
        return Car(step_file='audi_step_file')


if __name__ == '__main__':
    from parapy.gui import display

    obj = Spoiler(spoiler_airfoils=["test", "naca6408", "naca6406"],
                  spoiler_span=1600.,
                  spoiler_chord=300.,
                  spoiler_angle=10.,
                  strut_lat_location=0.6,
                  strut_thickness=10.,
                  strut_height=250.,
                  strut_chord_fraction=0.4,
                  strut_sweep=10.,
                  strut_cant=0.,
                  endplate_present=False,
                  endplate_thickness=5.,
                  endplate_sweep=0.,
                  endplate_cant=0.,
                  strut_amount=3)
    display(obj)
