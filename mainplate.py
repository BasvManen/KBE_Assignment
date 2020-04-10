from parapy.core import *
from parapy.geom import *


class MainPlate(GeomBase):

    airfoil_mid = Input()
    airfoil_tip = Input()
    span = Input()
    angle = Input()
    
    