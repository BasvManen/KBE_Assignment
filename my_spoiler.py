from parapy.core import Input, Attribute, Part, child
from parapy.gui import display

from spoiler_files import Spoiler

if __name__ == '__main__':
    from parapy.gui import display
    obj = Spoiler(label="Spoiler",
                  mid_airfoil='9412',
                  tip_airfoil='9408',
                  spoiler_span=2500.,
                  spoiler_chord=800.,
                  spoiler_angle=-5.,
                  strut_airfoil_shape=True,
                  strut_lat_location=0.8,
                  strut_height=250.,
                  strut_chord=400.,
                  strut_thickness=40.,
                  strut_sweep=15.,
                  strut_cant=15.,
                  endplate_present=False,
                  endplate_thickness=10.,
                  endplate_sweep=15.,
                  endplate_cant=10.)
    display(obj)