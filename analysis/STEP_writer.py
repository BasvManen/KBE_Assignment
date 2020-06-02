from parapy.exchange import STEPWriter
from parapy.geom import *
from parapy.core import *

import os

DIR = os.path.dirname(__file__)


class StepWriter(GeomBase):

    geometry_input = Input()
    STEP_file_with_car = Input(True)

    # Define the STEP file nodes
    @Attribute
    def nodes_for_stepfile(self):
        if self.geometry_input.endplate_present:
            nodes = [self.geometry_input.main_plate.surface,
                     self.geometry_input.main_plate.surface_mirrored,
                     self.geometry_input.struts.strut_right,
                     self.geometry_input.struts.strut_left,
                     self.geometry_input.endplates.endplate_right,
                     self.geometry_input.endplates.endplate_left]
        else:
            nodes = [self.geometry_input.main_plate.surface,
                     self.geometry_input.main_plate.surface_mirrored,
                     self.geometry_input.struts.strut_right,
                     self.geometry_input.struts.strut_left]
        return nodes

    # Write the STEP components from the nodes
    @Part
    def step_writer_components(self):
        return STEPWriter(default_directory=DIR,
                          nodes=self.nodes_for_stepfile)
