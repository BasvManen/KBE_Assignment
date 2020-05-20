from parapy.exchange.step import STEPReader
from parapy.core import Input, Attribute, Part, child
from parapy.geom import *

import os
import sys

DIR = os.path.dirname(__file__)


class Car(GeomBase):
    step_file = Input()

    @Attribute
    def car_file(self):
        return STEPReader(filename=sys.path[1] + '\\inputs\\'
                                   + self.step_file + '.stp').children

    @Part
    def solids(self):
        return TranslatedShape(
            quantify=len(self.car_file[0].children[1].children),
            shape_in=
            self.car_file[0].children[1].children[child.index].solids[0],
            displacement=Vector(0., 0., 0.))

    @Part
    def shells(self):
        return SewnShell(
            quantify=len(self.car_file[0].children[0].children),
            built_from=
            self.car_file[0].children[0].children[child.index])


if __name__ == '__main__':
    from parapy.gui import display

    obj = Car(step_file='audi_step_file')
    display(obj)
