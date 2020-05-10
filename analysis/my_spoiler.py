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
