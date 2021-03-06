from analysis.spoiler_files.assembly import Spoiler
from analysis.section_properties import SectionProperties

from parapy.geom import *
from parapy.core import *


###############################################################################
# WEIGHT ESTIMATION CLASS                                                     #
# In this file, a weight estimation of the spoiler is performed               #
#                                                                             #
# Inputs:                                                                     #
# - The density of the used material.                                         #
# - The skin thickness of the spoiler main plate.                             #
# - The area of the ribs, as defined from the SectionalProperties class.      #
# - The spoiler geometry, as defined in the Spoiler class.                    #
# - The amount of struts used in the assembly.                                #
###############################################################################

class WeightEstimation(GeomBase):

    # INPUTS
    material_density = Input()
    spoiler_skin_thickness = Input()
    ribs_area = Input()
    spoiler_geometry = Input(in_tree=False)
    strut_amount = Input()

    @Part(in_tree=False)
    def surface_lofted(self):
        """ This part returns the lofted shell of the main plate geometry,
        which is an input to create the thick main plate with actual
        thickness. """
        return Solid(self.spoiler_geometry.main_plate[0].lofted_shell)

    @Part(in_tree=False)
    def thick_mainplate(self):
        """ This part returns the actual thick main plate, from the lofted
        shell in surface_lofted and the spoiler skin thickness (projected to
        the inside). """
        return ThickShell(built_from=self.surface_lofted,
                          offset=-self.spoiler_skin_thickness,
                          mesh_deflection=1e-5)

    @Part(in_tree=False)
    def thick_mainplate_mirror(self):
        """ This part mirrors the half-span thick_mainplate part, to create
        the second half-span of the total main plate. """
        return MirroredShape(shape_in=self.thick_mainplate,
                             reference_point=Point(0, 0, 0),
                             vector1=Vector(1, 0, 0),
                             vector2=Vector(0, 0, 1),
                             mesh_deflection=1e-5)

    @Attribute
    def volume_mainplate(self):
        """ This attribute retrieves the volume of the thick main plate and
        converts it to m^3. """
        calculated_volume = abs(self.thick_mainplate.volume) * 2
        return calculated_volume / 10 ** 9

    @Attribute
    def volume_endplate(self):
        """ This attribute retrieves the volume of a single endplate and
        converts it to m^3. """
        return self.spoiler_geometry.endplates.solid.built_from.volume / 10 ** 9 \
            if self.spoiler_geometry.endplate_present else 0.

    @Attribute
    def volume_strut(self):
        """ This attribute retrieves the volume of a single strut and
        converts it to m^3. """
        return self.spoiler_geometry.struts.struts_right[0].volume / 10 ** 9

    @Attribute
    def volume_ribs(self):
        """ This attribute retrieves the total volume of the ribs and
        converts it to m^3. """
        # In case endplates are present at the spoiler tips
        if self.spoiler_geometry.endplate_present:
            total_rib_area = sum(self.ribs_area[1:-1])
            ribs_volume = total_rib_area * self.spoiler_skin_thickness
        # In case no endplates are present at the spoiler tips
        else:
            total_rib_area = sum(self.ribs_area)
            ribs_volume = total_rib_area * self.spoiler_skin_thickness
        return ribs_volume / 1000

    @Attribute
    def weight_mainplate(self):
        """ This attribute calculates the total weight of the main plate,
        in kg. """
        return self.volume_mainplate * self.material_density

    @Attribute
    def weight_endplate(self):
        """ This attribute calculates the weight of a single endplate,
        in kg. """
        return self.volume_endplate * self.material_density

    @Attribute
    def weight_strut(self):
        """ This attribute calculates the weight of a single strut,
        in kg. """
        return self.volume_strut * self.material_density

    @Attribute
    def weight_ribs(self):
        """ This attribute calculates the total weight of the ribs,
        in kg. """
        return self.volume_ribs * self.material_density

    @Attribute
    def total_weight(self):
        """ This attribute calculates the total weight of the spoiler
        assembly, in kg. """
        return self.weight_mainplate * self.spoiler_geometry.plate_amount \
               + self.weight_endplate * 2  \
               + self.weight_strut * self.strut_amount + self.weight_ribs
