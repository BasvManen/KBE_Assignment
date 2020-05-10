from parapy.core import Input, Attribute, Part, child
from parapy.gui import display

from analysis.spoiler_files import Spoiler


def geometry(geom):
    from parapy.gui import display
    spl = Spoiler(label="Spoiler",
                  mid_airfoil=geom[0],
                  tip_airfoil=geom[1],
                  spoiler_span=geom[2],
                  spoiler_chord=geom[3],
                  spoiler_angle=geom[4],
                  strut_airfoil_shape=geom[5],
                  strut_lat_location=geom[6],
                  strut_height=geom[7],
                  strut_chord_fraction=geom[8],
                  strut_thickness=geom[9],
                  strut_sweep=geom[10],
                  strut_cant=geom[11],
                  endplate_present=geom[12],
                  endplate_thickness=geom[13],
                  endplate_sweep=geom[14],
                  endplate_cant=geom[15])
    display(spl)


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
                  strut_thickness=20.,
                  strut_sweep=0.,
                  strut_cant=15.,
                  endplate_present=True,
                  endplate_thickness=10.,
                  endplate_sweep=0.,
                  endplate_cant=15.)
    display(obj)