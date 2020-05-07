from spoiler_files import MainPlate, StrutAirfoil, StrutPlate, Endplates
from parapy.core import Input, Attribute, Part, child, DynamicType
from parapy.core.validate import *
from parapy.geom import *
from parapy.exchange import STEPWriter
import kbeutils.avl as avl
from math import sin, cos, radians
import os

DIR = os.path.dirname(__file__)

# MAIN SPOILER CLASS
# In this file, the main spoiler geometry will be defined


class Spoiler(GeomBase):

    # Main Plate Inputs
    mid_airfoil = Input(validator=is_string)
    tip_airfoil = Input(validator=is_string)
    spoiler_span = Input(validator=Positive)
    spoiler_chord = Input(validator=Positive)
    spoiler_angle = Input(validator=Range(-60., 60.))

    # Strut Inputs
    strut_airfoil_shape = Input(False, validator=OneOf([True, False]))
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

    do_avl = Input(False)

    # Calculate reference area based on chord and span
    @Attribute
    def reference_area(self):
        return self.spoiler_chord*self.spoiler_span

    # Define the main plate (part)
    @Part
    def main_plate(self):
        return MainPlate(airfoil_mid=self.mid_airfoil,
                         airfoil_tip=self.tip_airfoil,
                         span=self.spoiler_span,
                         chord=self.spoiler_chord,
                         angle=self.spoiler_angle,
                         tip_cant=self.endplate_cant,
                         do_avl=self.do_avl)

    # Calculate the strut location
    @Attribute
    def strut_position(self):
        return self.position.translate("x", (self.spoiler_chord
                                             * cos(radians(self.spoiler_angle))
                                             - self.strut_chord_fraction
                                             * self.spoiler_chord *
                                             cos(radians(self.spoiler_angle)))
                                       / 2)

    # Define the struts (part)
    @Part
    def struts(self):
        return DynamicType(type=StrutAirfoil if self.strut_airfoil_shape
                           else StrutPlate,
                           chord_fraction=self.strut_chord_fraction,
                           strut_lat_location=self.strut_lat_location,
                           strut_height=self.strut_height,
                           strut_thickness=self.strut_thickness,
                           strut_sweepback_angle=self.strut_sweep,
                           strut_cant_angle=self.strut_cant,
                           main=self.main_plate,
                           position=self.strut_position)

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
        pos = float(self.tip_airfoil[1])/10
        thickness = float(self.tip_airfoil[2:4]) \
            if len(self.tip_airfoil) == 4 else float(self.tip_airfoil[3:5])
        height_frac_1 = sin(radians(self.spoiler_angle))
        height_frac_2 = (camber/100. + 0.5*thickness/100.) * \
            cos(radians(self.spoiler_angle)) - \
            0.9 * (pos*sin(radians(self.spoiler_angle)))

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


if __name__ == '__main__':
    from parapy.gui import display
    obj = Spoiler(label="SpoilerAssembly",
                  mid_airfoil='9412',
                  tip_airfoil='9408',
                  spoiler_span=2500.,
                  spoiler_chord=800.,
                  spoiler_angle=5.,
                  strut_airfoil_shape=True,
                  strut_lat_location=0.8,
                  strut_height=250.,
                  strut_chord_fraction=.7,
                  strut_thickness=40.,
                  strut_sweep=15.,
                  strut_cant=15.,
                  endplate_present=True,
                  endplate_thickness=10.,
                  endplate_sweep=0.,
                  endplate_cant=0.)
    display(obj)