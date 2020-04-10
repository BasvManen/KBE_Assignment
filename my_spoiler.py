from parapy.core import Input, Attribute, Part, child
from parapy.gui import display

from spoiler_files import Spoiler

if __name__ == '__main__':
    from parapy.gui import display
    obj = Spoiler(label="spoiler",
                  strut_airfoil=False,
                  endplate_input=True)
    display(obj)