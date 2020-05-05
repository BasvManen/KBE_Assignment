from parapy.core import Input, Attribute, Part, child
from parapy.gui import display

from spoiler_files import Spoiler

if __name__ == '__main__':
    from parapy.gui import display
    obj = Spoiler(label="Spoiler",
                  mid_airfoil='9412',
                  tip_airfoil='6408',
                  spoiler_span=2500.,
                  spoiler_chord=800.,
                  spoiler_angle=5.,
                  strut_airfoil_shape=True,
                  strut_lat_location=0.8,
                  strut_height=250.,
                  strut_chord_fraction=.7,
                  strut_thickness=40.,
                  strut_sweep=0.,
                  strut_cant=15.,
                  endplate_present=True,
                  endplate_thickness=10.,
                  endplate_sweep=0.,
                  endplate_cant=15.)
    display(obj)