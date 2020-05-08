from parapy.core import *
from parapy.geom import *
from math import sin, cos, radians

import kbeutils.avl as avl
from spoiler_files.section import Section

# MAIN PLATE CLASS
# In this file, the spoiler main plate is defined


class MainPlate(GeomBase):

    # INPUTS
    airfoil_mid = Input()
    airfoil_tip = Input()
    span = Input()
    chord = Input()
    angle = Input()
    tip_cant = Input()

    do_avl = Input(False)

    # Define sections in one array
    @Attribute
    def airfoil_names(self):
        return self.airfoil_mid, self.airfoil_tip

    # Define positions of sections in one array
    @Attribute
    def section_positions(self):
        mid_position = self.position
        tip_position = self.position.translate('y', self.span/2)
        return mid_position, tip_position

    # Define wetted area
    @ Attribute
    def wetted_area(self):
        t_avg = (int(self.airfoil_mid[2:4]) + int(self.airfoil_tip[2:4])) / 2 \
            if len(self.airfoil_mid) == 4 \
            else (int(self.airfoil_mid[3:5]) + int(self.airfoil_tip[3:5])) / 2
        print(t_avg)
        s_wet = self.span * self.chord * (0.5*t_avg/100 + 1.98)
        return s_wet

    # Create the sections from name and position
    @Part(in_tree=False)
    def sections(self):
        return Section(quantify=2,
                       airfoil_name=self.airfoil_names[child.index],
                       chord=self.chord,
                       angle=self.angle,
                       position=self.section_positions[child.index])

    # Create a solid between the created sections
    @Part(in_tree=False)
    def surface_whole(self):
        return LoftedSolid(profiles=[section.curve
                                     for section in self.sections],
                           ruled=True)

    # Create a cutting plane parallel to the end plate
    @Part(in_tree=False)
    def cutting_plane(self):
        return Plane(translate(XOY, 'x', self.chord*cos(radians(self.angle)),
                               'y', self.span/2,
                               'z', self.chord*sin(radians(self.angle))),
                     normal=rotate(VY, VX, -self.tip_cant, deg=True))

    # Define the part of the main plate that needs to be cut off
    @Part(in_tree=False)
    def half_space_solid(self):
        return HalfSpaceSolid(self.cutting_plane, Point(0, self.span, 0))

    # Create the canted solid from the whole plate and the cutting plane
    @Part
    def surface(self):
        return SubtractedSolid(shape_in=self.surface_whole,
                               tool=self.half_space_solid,
                               mesh_deflection=1e-5)

    # Mirror the canted solid the obtain the whole main plate
    @Part
    def surface_mirrored(self):
        return MirroredShape(shape_in=self.surface,
                             reference_point=self.position.point,
                             vector1=self.position.Vx,
                             vector2=self.position.Vz,
                             mesh_deflection=1e-5)

    # Create aerodynamic surface for AVL analysis
    @Part
    def avl_surface(self):
        return avl.Surface(name="Main Plate",
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.cosine,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.equal,
                           y_duplicate=self.position.point[1],
                           sections=[section.avl_section
                                     for section in self.sections],
                           hidden=not self.do_avl)


if __name__ == '__main__':
    from parapy.gui import display
    obj = MainPlate(airfoil_mid='9412',
                    airfoil_tip='7408',
                    span=3,
                    chord=0.8,
                    angle=0,
                    tip_cant=15)
    display(obj)