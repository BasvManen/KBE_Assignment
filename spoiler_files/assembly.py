from parapy.core import Input, Attribute, Part, child, DynamicType
from parapy.geom import *
from math import sin, cos, radians

from spoiler_files import MainPlate, StrutAirfoil, StrutPlate, Endplates
import kbeutils.avl as avl


class Spoiler(GeomBase):

    # Main Plate Inputs
    mid_airfoil = Input()
    tip_airfoil = Input()
    spoiler_span = Input()
    spoiler_chord = Input()
    spoiler_angle = Input()

    # Strut Inputs
    strut_airfoil_shape = Input(False)
    strut_lat_location = Input()
    strut_height = Input()
    strut_chord = Input()
    strut_thickness = Input()
    strut_sweep = Input()
    strut_cant = Input()

    # Endplate Inputs
    endplate_present = Input(True)
    endplate_thickness = Input()
    endplate_sweep = Input()
    endplate_cant = Input()

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
        return self.position.translate("x", 0)

    @Part
    def struts(self):
        return DynamicType(type=StrutAirfoil if self.strut_airfoil_shape else StrutPlate,
                           spoiler_span=self.spoiler_span,
                           chord=self.strut_chord,
                           strut_lat_location=self.strut_lat_location,
                           height=self.strut_height+100,
                           thickness=self.strut_thickness,
                           sweepback_angle=self.strut_sweep,
                           cant_angle=self.strut_cant
                           #position=XOY.translate("y", self.struts.height/self.struts.chord)
                           #if self.strut_airfoil_shape else self.position.translate("z", -self.struts.height)
                           ) # due to earlier used transformations and scaling this is used.



    @Part
    def strut_new(self):
        return SubtractedSolid(shape_in=self.struts.solid, tool=self.main_plate.surface)

    @Attribute
    def endplate_position(self):
        return self.position.translate("z", self.spoiler_chord*sin(radians(self.spoiler_angle)))

    @Part
    def endplates(self):
        return DynamicType(type=Endplates,
                           spoiler_span=self.spoiler_span,
                           chord=self.spoiler_chord*cos(radians(self.spoiler_angle)),
                           height=self.spoiler_chord*sin(radians(self.spoiler_angle)),
                           thickness=self.endplate_thickness,
                           sweepback_angle=self.endplate_sweep,
                           cant_angle=self.endplate_cant,
                           position=self.endplate_position,
                           hidden=False if self.endplate_present else True)

    @Attribute
    def avl_surfaces(self):
        return self.find_children(lambda o: isinstance(o, avl.Surface))

    @Part(in_tree=False)
    def avl_configuration(self):
        return avl.Configuration(name='Spoiler',
                                 reference_area=self.reference_area,
                                 reference_span=self.spoiler_span,
                                 reference_chord=self.spoiler_chord,
                                 reference_point=self.position.point,
                                 surfaces=self.avl_surfaces)


if __name__ == '__main__':
    from parapy.gui import display
    obj = Spoiler(label='spoiler_assembly',
                  strut_airfoil_shape=False,
                  endplate_present=True)
    display(obj)
