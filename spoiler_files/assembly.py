from parapy.core import Input, Attribute, Part, child, DynamicType
from parapy.geom import *
from math import radians

from spoiler_files import MainPlate, StrutAirfoil, StrutPlate, Endplates


class Spoiler(GeomBase):
    strut_airfoil = Input()
    endplate_input = Input()

    @Part
    def main_plate(self):
        return MainPlate(airfoil_mid='9412',
                         airfoil_tip='9408',
                         span=3000.,
                         chord=800.,
                         angle=20)

    @Attribute
    def strut_position(self):
        return self.position.translate("x", self.struts.chord / 2,
                                       "z", -self.struts.height)

    @Part
    def struts(self):
        return DynamicType(type=StrutAirfoil if self.strut_airfoil else StrutPlate,
                           spoiler_span=self.main_plate.span,
                           chord=0.5 * self.main_plate.chord,
                           strut_lat_location=0.5,
                           height=600.,
                           thickness=20.,
                           sweepback_angle=15.,
                           cant_angle=25.,
                           position=XOY.translate("y", self.struts.height/self.struts.chord)
                           if self.strut_airfoil else self.position.translate("z", -self.struts.height)
                           ) # due to earlier used transformations and scaling this is used.

    @Attribute
    def endplate_position(self):
        return self.position.translate("x", self.main_plate.position.x + self.main_plate.chord / 2)

    @Part
    def endplates(self):
        return DynamicType(type=Endplates,
                           spoiler_span=self.main_plate.span,
                           endplate_position=0.7,
                           chord=self.main_plate.chord,
                           height=400.,
                           thickness=10.,
                           sweepback_angle=15.,
                           cant_angle=15.,
                           position=self.endplate_position,
                           hidden=False if self.endplate_input else True)


if __name__ == '__main__':
    from parapy.gui import display
    obj = Spoiler(label='spoiler_assembly')
    display(obj)
