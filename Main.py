from parapy.core import *
from parapy.geom import *
from parapy.core.validate import *

from analysis.spoiler_files import Spoiler
from analysis.AVL_main import AvlAnalysis


class Main(GeomBase):

    # Main Plate Inputs
    spoiler_airfoils = Input()
    spoiler_span = Input(validator=Positive)
    spoiler_chord = Input(validator=Positive)
    spoiler_angle = Input(validator=Range(-60., 60.))

    # Strut Inputs
    strut_amount = Input(2, validator=GreaterThanOrEqualTo(2))
    strut_airfoil_shape = Input(True, validator=OneOf([True, False]))
    strut_lat_location = Input(validator=Range(limit1=0.1, limit2=1.0))
    strut_height = Input(validator=Positive)
    strut_chord_fraction = Input(validator=Range(0.3, 1.0))
    strut_thickness = Input(validator=Positive)
    strut_sweep = Input(validator=Range(-60., 60.))
    strut_cant = Input(validator=Range(-30., 30.))

    # Endplate Inputs
    endplate_present = Input(True, validator=OneOf([True, False]))
    endplate_thickness = Input(validator=And(Positive))
    endplate_sweep = Input(validator=Range(-60., 60.))
    endplate_cant = Input(validator=Range(-60., 60.))

    cases = Input()
    velocity = Input()
    density = Input()

    @Part
    def geometry(self):
        """ Geometry of the spoiler, as visible in the ParaPy GUI. """
        return Spoiler(spoiler_airfoils=self.spoiler_airfoils,
                       spoiler_span=self.spoiler_span,
                       spoiler_chord=self.spoiler_chord,
                       spoiler_angle=self.spoiler_angle,
                       strut_amount=self.strut_amount,
                       strut_airfoil_shape=self.strut_airfoil_shape,
                       strut_lat_location=self.strut_lat_location,
                       strut_height=self.strut_height,
                       strut_chord_fraction=self.strut_chord_fraction,
                       strut_thickness=self.strut_thickness,
                       strut_sweep=self.strut_sweep,
                       strut_cant=self.strut_cant,
                       endplate_present=self.endplate_present,
                       endplate_thickness=self.endplate_thickness,
                       endplate_sweep=self.endplate_sweep,
                       endplate_cant=self.endplate_cant)

    @Part
    def avl_analysis(self):
        """ AVL Analysis of the given spoiler geometry. """
        return AvlAnalysis(spoiler_input=self.geometry,
                           case_settings=self.cases,
                           velocity=self.velocity,
                           density=self.density)


if __name__ == '__main__':
    from parapy.gui import display

    # Inputs, this needs to be defined in a separate dat file, so this is
    # temporary.

    spoiler_airfoils = ['test', 'naca6406']
    spoiler_span = 3000
    spoiler_chord = 800
    spoiler_angle = 10
    strut_amount = 2
    strut_airfoil_shape = True
    strut_lat_location = 0.75
    strut_height = 400
    strut_chord_fraction = 0.6
    strut_thickness = 40
    strut_sweep = 10
    strut_cant = 10
    endplate_present = True
    endplate_thickness = 15
    endplate_sweep = 0
    endplate_cant = 10

    cases = [('Incoming flow angle', {'alpha': 2})]
    velocity = 25
    density = 1.225

    obj = Main(spoiler_airfoils=spoiler_airfoils,
               spoiler_span=spoiler_span,
               spoiler_chord=spoiler_chord,
               spoiler_angle=spoiler_angle,
               strut_amount=strut_amount,
               strut_airfoil_shape=strut_airfoil_shape,
               strut_lat_location=strut_lat_location,
               strut_height=strut_height,
               strut_chord_fraction=strut_chord_fraction,
               strut_thickness=strut_thickness,
               strut_sweep=strut_sweep,
               strut_cant=strut_cant,
               endplate_present=endplate_present,
               endplate_thickness=endplate_thickness,
               endplate_sweep=endplate_sweep,
               endplate_cant=endplate_cant,
               cases=cases,
               velocity=velocity,
               density=density)
    display(obj)
