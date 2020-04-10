from parapy.core import Input, Attribute, Part, child
from parapy.geom import GeomBase, Plane

from spoiler_files import MainPlate, Strut, Endplates


class Spoiler(GeomBase):

    @Part
    def main_plate(self):
        return MainPlate(airfoil_mid='0012',
                         airfoil_tip='0008',
                         span=3,
                         chord=0.8,
                         angle=-20)

    @Attribute
    def strut_position(self):
        return self.position.translate("x", self.main_plate.position.x,
                                       "z", -self.struts.height)

    @Part
    def struts(self):
        return Strut(spoiler_span=self.main_plate.span,
                     position=self.strut_position)

    @Attribute
    def endplate_position(self):
        return self.position.translate("x", self.main_plate.position.x + self.main_plate.chord/2)

    @Part
    def endplates(self):
        return Endplates(endplate_input=True,
                         spoiler_span=self.main_plate.span,
                         chord=self.main_plate.chord,
                         thickness=0.01,
                         position=self.endplate_position)


