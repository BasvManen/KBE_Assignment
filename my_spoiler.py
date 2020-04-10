from parapy.core import Input, Attribute, Part, child
from parapy.gui import display

from spoiler_files import Spoiler, StrutAirfoil


if __name__ == '__main__':
    from parapy.gui import display
    print(StrutAirfoil.height)
    obj = Spoiler(label="spoiler",
                  strut_airfoil=True,
                  endplate_input=True)
    display(obj)