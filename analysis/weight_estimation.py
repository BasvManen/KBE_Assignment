from analysis.spoiler_files.assembly import Spoiler
from analysis.spoiler_files.section import Section
from analysis.section_properties import SectionProperties
from math import radians

from parapy.geom import *
from parapy.core import *


class WeightEstimation(GeomBase):
    # INPUTS
    material_density = Input()
    spoiler_skin_thickness = Input()
    ribs_area = Input()
    spoiler_geometry = Input(in_tree=True)
    strut_amount = Input()

    @Part(in_tree=False)
    def surface_lofted(self):
        return Solid(self.spoiler_geometry.main_plate.lofted_shell)

    # From the lofted surface, make a thick surface with the inputted skin
    # thickness projected to the inside
    @Part(in_tree=True)
    def thick_mainplate(self):
        return ThickShell(built_from=self.surface_lofted,
                          offset=-self.spoiler_skin_thickness)

    @Part(in_tree=True)
    def thick_mainplate_mirror(self):
        return MirroredShape(shape_in=self.thick_mainplate,
                             reference_point=Point(0, 0, 0),
                             vector1=Vector(1, 0, 0),
                             vector2=Vector(0, 0, 1))

    # Retrieve the volume of this thick main plate
    @Attribute
    def volume_mainplate(self):
        calculated_volume = abs(self.thick_mainplate.volume) * 2
        return calculated_volume / 10 ** 9

    # Get the volume of a single endplate
    @Attribute
    def volume_endplate(self):  # in m^3 while inputs are in mm
        return self.spoiler_geometry.endplates.endplate_right.volume / 10 ** 9 \
            if self.spoiler_geometry.endplate_present else 0.

    # Get the volume of a single strut
    @Attribute
    def volume_strut(self):  # in m^3 while inputs are in mm
        return self.spoiler_geometry.struts.struts_right[0].volume / 10 ** 9

    # Get the volume of the ribs, note that the imported area is in m^2,
    # while the skin thickness is in mm. Therefor the volume has to be
    # devided by a factor 1000.
    @Attribute
    def volume_ribs(self):
        if self.spoiler_geometry.endplate_present:
            total_rib_area = sum(self.ribs_area[1:-1])
            ribs_volume = total_rib_area * self.spoiler_skin_thickness
        else:
            total_rib_area = sum(self.ribs_area)
            ribs_volume = total_rib_area * self.spoiler_skin_thickness
        return ribs_volume / 1000

    # Calculate the weight of the thick main plate
    @Attribute
    def weight_mainplate(self):  # in kg
        return self.volume_mainplate * self.material_density

    # Calculate the weight of a single endplate
    @Attribute
    def weight_endplate(self):  # in kg
        return self.volume_endplate * self.material_density

    # Calculate the weight of a single strut
    @Attribute
    def weight_strut(self):  # in kg
        return self.volume_strut * self.material_density

    # Calculate the weight of the ribs
    @Attribute
    def weight_ribs(self):
        return self.volume_ribs * self.material_density

    # Calculate the total weight of the spoiler
    @Attribute
    def total_weight(self):
        return self.weight_mainplate + self.weight_endplate * 2 \
               + self.weight_strut * self.strut_amount + self.weight_ribs


if __name__ == '__main__':
    from parapy.gui import display


    ribs_area = SectionProperties(
            airfoils=['test', 'test'],
                      spoiler_span=1600.,
                      spoiler_chord=300.,
                      spoiler_angle=10.,
            spoiler_skin_thickness=2,
            n_cuts=4,
            n_ribs=0).ribs_area

    spoiler = Spoiler(spoiler_airfoils=['test', 'test'],
                      spoiler_span=1600.,
                      spoiler_chord=300.,
                      spoiler_angle=10.,
                      strut_amount=2,
                      strut_airfoil_shape=True,
                      strut_lat_location=0.7,
                      strut_height=250.,
                      strut_chord_fraction=0.4,
                      strut_thickness=10.,
                      strut_sweep=15.,
                      strut_cant=10.,
                      endplate_present=False,
                      endplate_thickness=3,
                      endplate_sweep=3,
                      endplate_cant=3, hidden=True)
    obj = WeightEstimation(material_density=2700., spoiler_skin_thickness=2,
                           ribs_area = ribs_area, spoiler_geometry=spoiler)

    display(obj)
