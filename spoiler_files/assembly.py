from spoiler_files import MainPlate, StrutAirfoil, StrutPlate, Endplates
from parapy.core import Input, Attribute, Part, child, DynamicType
from parapy.core.validate import *
from parapy.geom import *
from parapy.exchange import STEPWriter
import kbeutils.avl as avl
from math import sin, cos, radians
import os


DIR = os.path.dirname(__file__)


class Spoiler(GeomBase):

    # Main Plate Inputs
    mid_airfoil = Input(validator=is_string)
    tip_airfoil = Input(validator=is_string)
    spoiler_span = Input(validator=Positive)
    spoiler_chord = Input(validator=Positive)
    spoiler_angle = Input(validator=And(Positive, LessThanOrEqualTo(60.)))

    # Strut Inputs
    strut_airfoil_shape = Input(False, validator=OneOf([True, False]))
    strut_lat_location = Input(validator=And(Positive, Range(limit1=0.1,
                                                             limit2=1.0)))
    strut_height = Input(validator=Positive)
    strut_chord = Input(validator=Positive)
    strut_thickness = Input(validator=Positive)
    strut_sweep = Input(validator=And(Positive, LessThanOrEqualTo(60.)))
    strut_cant = Input(validator=And(Positive, LessThanOrEqualTo(60.)))

    # Endplate Inputs
    endplate_present = Input(True, validator=OneOf([True, False]))
    endplate_thickness = Input(validator=And(Positive,
                                             GreaterThanOrEqualTo(1.)))
    endplate_sweep = Input(validator=And(Positive, LessThanOrEqualTo(60.)))
    endplate_cant = Input(validator=And(Positive, LessThanOrEqualTo(60.)))

    @Attribute
    def reference_area(self):
        return self.spoiler_chord*self.spoiler_span

    @Part
    def main_plate(self):
        return MainPlate(airfoil_mid=self.mid_airfoil,
                         airfoil_tip=self.tip_airfoil,
                         span=self.spoiler_span,
                         chord=self.spoiler_chord,
                         angle=self.spoiler_angle,
                         tip_cant=self.endplate_cant)

    @Attribute
    def strut_position(self):
        return self.position.translate("x", (self.spoiler_chord*cos(radians(self.spoiler_angle))-self.strut_chord)/2)

    @Part
    def struts(self):
        return DynamicType(type=StrutAirfoil if self.strut_airfoil_shape else StrutPlate,
                           spoiler_span=self.spoiler_span,
                           chord=self.strut_chord,
                           strut_lat_location=self.strut_lat_location,
                           height=self.strut_height,
                           thickness=self.strut_thickness,
                           sweepback_angle=self.strut_sweep,
                           cant_angle=self.strut_cant,
                           main=self.main_plate,
                           position=self.strut_position)  # due to earlier used transformations and scaling this is used.

    @Attribute
    def endplate_position(self):
        return self.position.translate("z", self.spoiler_chord*sin(radians(self.spoiler_angle)))

    @Part
    def endplates(self):
        return DynamicType(type=Endplates,
                           spoiler_span=self.spoiler_span,
                           chord=self.spoiler_chord*cos(radians(self.spoiler_angle)),
                           height=max(100, 1.1*self.spoiler_chord*sin(radians(self.spoiler_angle))),
                           thickness=self.endplate_thickness,
                           sweepback_angle=self.endplate_sweep,
                           cant_angle=self.endplate_cant,
                           position=self.endplate_position,
                           hidden=False if self.endplate_present else True)

    @Attribute
    def avl_surfaces(self):
        return self.find_children(lambda o: isinstance(o, avl.Surface))

    @Part
    def avl_configuration(self):
        return avl.Configuration(name='Spoiler',
                                 reference_area=self.reference_area,
                                 reference_span=self.spoiler_span,
                                 reference_chord=self.spoiler_chord,
                                 reference_point=self.position.point,
                                 surfaces=self.avl_surfaces,
                                 mach=0.0)

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
                  strut_chord=400.,
                  strut_thickness=40.,
                  strut_sweep=15.,
                  strut_cant=15.,
                  endplate_present=True,
                  endplate_thickness=10.,
                  endplate_sweep=15.,
                  endplate_cant=10.)
    display(obj)