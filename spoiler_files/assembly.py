from parapy.core import Input, Attribute, Part, child
from parapy.geom import GeomBase, Plane

from spoiler_files import MainPlate, StrutAirfoil, StrutPlate, Endplates


class Spoiler(GeomBase):

    @Part
    def main_plate(self):
        return MainPlate(airfoil_mid='0012',
                         airfoil_tip='0008',
                         span=3000.,
                         chord=800.,
                         angle=-20)

    @Part
    def struts(self):
        return StrutAirfoil(spoiler_span=self.main_plate.span,
                            chord=0.5*self.main_plate.chord,
                            position=self.position.translate("x", self.main_plate.position.x))

    # @Part
    # def struts(self):
    #     return StrutPlate(spoiler_span=self.main_plate.span,
    #                       chord=0.5*self.main_plate.chord,
    #                       position=self.strut_position)

    # @Attribute
    # def strut_position(self):
    #     return self.position.translate("x", self.main_plate.position.x,
    #                                    "z", -self.struts.height)

    @Attribute
    def endplate_position(self):
        return self.position.translate("x", self.main_plate.position.x + self.main_plate.chord/2)

    @Part
    def endplates(self):
        return Endplates(endplate_input=True,
                         spoiler_span=self.main_plate.span,
                         endplate_position=0.7,
                         chord=self.main_plate.chord,
                         height=400.,
                         thickness=10.,
                         position=self.endplate_position)


if __name__ == '__main__':
    from parapy.gui import display
    obj = Spoiler(label='spoiler_assembly')
    display(obj)