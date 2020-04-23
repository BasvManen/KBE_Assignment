from spoiler_files.assembly import Spoiler
from spoiler_files.section import Section
from spoiler_files.mainplate import MainPlate
from spoiler_files.endplates import Endplates
from spoiler_files.strut_airfoil import StrutAirfoil
from spoiler_files.strut_plate import StrutPlate
from section_properties import SectionProperties

from math import pi, sin, cos, tan, radians
from parapy.geom import *
from parapy.core import *


class WeightEstimation(GeomBase):

    # Material Input
    material_density = Input()

    # Main Plate Inputs
    mid_airfoil = Input()
    tip_airfoil = Input()
    spoiler_span = Input()
    spoiler_chord = Input()
    spoiler_skin_thickness = Input()
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

    @Part(in_tree=False)
    def whole_spoiler(self):
        return Spoiler(mid_airfoil=self.mid_airfoil,
                       tip_airfoil=self.tip_airfoil,
                       spoiler_span=self.spoiler_span,
                       spoiler_chord=self.spoiler_chord,
                       spoiler_angle=self.spoiler_angle,
                       strut_airfoil_shape=self.strut_airfoil_shape,
                       strut_lat_location=self.strut_lat_location,
                       strut_height=self.strut_height,
                       strut_chord=self.strut_chord,
                       strut_thickness=self.strut_thickness,
                       strut_sweep=self.strut_sweep,
                       strut_cant=self.strut_cant,
                       endplate_present=self.endplate_present,
                       endplate_thickness=self.endplate_thickness,
                       endplate_sweep=self.endplate_sweep,
                       endplate_cant=self.endplate_cant)

    @Attribute
    def airfoil_names(self):
        return self.mid_airfoil, self.tip_airfoil

    @Attribute
    def section_positions(self):
        mid_position = self.position
        tip_position = self.position.translate('y', self.spoiler_span / 2)
        return mid_position, tip_position

    @Part(in_tree=False)
    def sections(self):
        return Section(quantify=2,
                       airfoil_name=self.airfoil_names[child.index],
                       chord=self.spoiler_chord,
                       angle=self.spoiler_angle,
                       position=self.section_positions[child.index])

    @Part(in_tree=False)
    def surface_lofted(self):
        return LoftedShell(profiles=[section.curve for section in self.sections])

    @Part(in_tree=True)
    def thick_mainplate(self):
        return ThickShell(built_from=self.surface_lofted, offset=-self.spoiler_skin_thickness)

    @Attribute
    def volume_mainplate(self):
        calculated_volume = abs(self.thick_mainplate.volume) * 2
        return calculated_volume / 10 ** 9

    @Attribute
    def volume_endplate(self):      # in m^3 while inputs are in mm
        return self.whole_spoiler.endplates.fillet.volume / 10**9 if self.endplate_present else 0.

    @Attribute
    def volume_strut(self):         # in m^3 while inputs are in mm
        return self.whole_spoiler.struts.strut.volume / 10**9

    @Attribute
    def weight_mainplate(self):     # in kg
        return self.volume_mainplate * self.material_density

    @Attribute
    def weight_endplate(self):     # in kg
        return self.volume_endplate * self.material_density

    @Attribute
    def weight_strut(self):     # in kg
        return self.volume_strut * self.material_density

    @Attribute
    def total_weight(self):
        return self.weight_mainplate + self.weight_endplate * 2 + self.weight_strut * 2


if __name__ == '__main__':
    from parapy.gui import display

    obj = WeightEstimation(label="Weight Estimator",
                           material_density=1600.,
                           mid_airfoil='0014',
                           tip_airfoil='0012',
                           spoiler_span=2500.,
                           spoiler_chord=800.,
                           spoiler_skin_thickness=2.,
                           spoiler_angle=0.,
                           strut_airfoil_shape=True,
                           strut_lat_location=0.8,
                           strut_height=250.,
                           strut_chord=400.,
                           strut_thickness=40.,
                           strut_sweep=15.,
                           strut_cant=15.,
                           endplate_present=False,
                           endplate_thickness=10.,
                           endplate_sweep=15.,
                           endplate_cant=10.)
    display(obj)
