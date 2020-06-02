from parapy.exchange import STEPWriter
from parapy.geom import *
from parapy.core import *
from math import floor

import os

DIR = os.path.dirname(__file__)

###############################################################################
# STEP WRITER CLASS                                                           #
# In this file, the STEP-writer is defined                                    #
#                                                                             #
# Inputs:                                                                     #
# - The spoiler geometry, as defined in the Spoiler class                     #
# - STEP_file_with_car, which determines whether the car geometry is also     #
#   used for the STEP file.                                                   #
###############################################################################


class StepWriter(GeomBase):

    # Inputs
    geometry_input = Input()
    STEP_file_with_car = Input(True)

    @Attribute
    def mainplate_nodes(self):
        """ This attribute defines the STEP-file nodes for the main plate of
        the Spoiler geometry. """
        nodes = []
        for i in range(self.geometry_input.plate_amount):
            nodes.append(self.geometry_input.main_plate[i].surface)
            nodes.append(self.geometry_input.main_plate[i].mirrored_surface)
        return nodes

    @Attribute
    def strut_nodes(self):
        """ This attribute defines the STEP-file nodes for the struts of
        the Spoiler geometry. """
        nodes = []
        if self.geometry_input.strut_amount % 2 == 0:
            for i in range(self.geometry_input.strut_amount / 2):
                nodes.append(self.geometry_input.struts.struts_right[i])
                nodes.append(self.geometry_input.struts.struts_left[i])
        else:
            for i in range(floor(self.geometry_input.strut_amount / 2)):
                nodes.append(self.geometry_input.struts.struts_right[i])
                nodes.append(self.geometry_input.struts.struts_left[i])
            nodes.append(self.geometry_input.struts.strut_mid)
        return nodes

    @Attribute
    def endplate_nodes(self):
        """ This attribute defines the STEP-file nodes for the endplates of
        the Spoiler geometry. """
        nodes = [self.geometry_input.endplates.right_side,
                 self.geometry_input.endplates.left_side]
        return nodes

    @Attribute
    def car_nodes(self):
        """ This attribute defines the STEP-file nodes for the car model. """
        nodes = [self.geometry_input.car_model.car_model]
        for i in range(4):
            nodes.append(self.geometry_input.car_model.wheels[i])
        return nodes

    @Attribute
    def nodes_for_stepfile(self):
        """ This attribute collects all needed STEP-file nodes. """
        nodes = self.mainplate_nodes + self.strut_nodes
        if self.geometry_input.endplate_present:
            nodes = nodes + self.endplate_nodes
        if self.STEP_file_with_car:
            nodes = nodes + self.car_nodes
        return nodes

    @Part
    def step_writer_components(self):
        """ This part uses the STEPWriter class to create a step-file of the
        inputted Spoiler geometry. """
        return STEPWriter(default_directory=DIR,
                          nodes=self.nodes_for_stepfile)
