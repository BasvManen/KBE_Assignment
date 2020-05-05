from math import radians, sin, cos
from parapy.core import Input, Attribute, Part
from parapy.geom import *
from kbeutils.geom.curve import Naca4AirfoilCurve
import kbeutils.avl as avl

# AIRFOIL-SHAPED STRUT CLASS
# In this file, the spoiler struts with airfoil shapes are defined


class StrutAirfoil(GeomBase):

    # INPUTS
    strut_lat_location = Input()
    chord_fraction = Input()
    strut_height = Input()
    strut_thickness = Input()
    strut_sweepback_angle = Input()
    strut_cant_angle = Input()
    main = Input()

    # Calculate the strut chord from the spoiler chord and angle
    @Attribute
    def strut_chord(self):
        return self.main.chord * self.chord_fraction \
               * cos(radians(self.main.angle))

    # Calculate the thickness to chord ratio for the airfoil. Note that the
    # airfoil can not get too thin, otherwise AVL errors would occur.
    @Attribute
    def thickness_to_chord(
            self):
        if round(self.strut_thickness / self.strut_chord * 100) < 2:
            ratio = 2
        elif round(self.strut_thickness / self.strut_chord * 100) > 40:
            ratio = 40
        else:
            ratio = int(self.strut_thickness / self.strut_chord * 100)
        return ratio

    # Retrieve the 4-digit NACA symmetric airfoil name from the t/c ratio
    @Attribute
    def symmetric_airfoil_name(self):
        if self.thickness_to_chord >= 10:
            name = '00' + str(self.thickness_to_chord)
        else:
            name = '000' + str(self.thickness_to_chord)
        return name

    # Create the airfoil
    @Part(in_tree=False)
    def airfoil(self):
        return RotatedCurve(
            curve_in=Naca4AirfoilCurve(self.symmetric_airfoil_name,
                                       n_points=200),
            rotation_point=XOY,
            vector=self.position.Vx, angle=radians(90))

    # Scale the airfoil to correct inputted chord
    @Part(in_tree=False)
    def airfoil_scaled(self):
        return ScaledCurve(curve_in=self.airfoil,
                           reference_point=XOY,
                           factor=self.strut_chord)

    # Create the upper and lower curve for the ruled solid
    @Part(in_tree=False)
    def upper_curve_airfoil(self):
        return TranslatedCurve(curve_in=self.airfoil_scaled,
                               displacement=Vector(self.position.point[0],
                                                   self.strut_lat_location
                                                   * self.main.span / 2,
                                                   self.position.point[2]))

    @Part(in_tree=False)
    def lower_curve_airfoil(self):
        return TranslatedCurve(curve_in=self.upper_curve_airfoil,
                               displacement=Vector(-self.strut_height * sin(
                                   radians(self.strut_sweepback_angle)),
                                                   -self.strut_height * sin(radians(
                                                       self.strut_cant_angle)),
                                                   -self.strut_height))

    # Initialise AVL input for the struts
    @Part(in_tree=False)
    def avl_section_up(self):
        return avl.SectionFromCurve(curve_in=self.upper_curve_airfoil)

    @Part(in_tree=False)
    def avl_section_lo(self):
        return avl.SectionFromCurve(curve_in=self.lower_curve_airfoil)

    # In order to cut off the strut at the lower side of the main plate,
    # the strut upper curve is extended to a higher z-location from where it
    # can be easily partioned.
    @Part(in_tree=False)
    def extended_airfoil(self):
        return TranslatedCurve(curve_in=self.upper_curve_airfoil,
                               displacement=
                               Vector(self.strut_height
                                      * sin(radians(self.strut_sweepback_angle)),
                                      self.strut_height
                                      * sin(radians(self.strut_cant_angle)),
                                      self.strut_height + self.main.chord))

    # Create the initial solid for the extended strut
    @Part(in_tree=False)
    def solid(self):
        return RuledSolid(profile1=self.extended_airfoil,
                          profile2=self.lower_curve_airfoil)

    # Initialise subtraction of the solid at the main plate lower surface by
    # cutting the solid into several pieces.
    @Part(in_tree=False)
    def partitioned_solid(self):
        return PartitionedSolid(solid_in=self.main.surface,
                                tool=self.solid,
                                keep_tool=True)

    # Create part of the right strut from the subtracted solid
    @Part
    def strut_right(self):
        return SubtractedSolid(shape_in=SubtractedSolid(shape_in=self.solid,
                                                        tool=self.partitioned_solid.solids[2]),
                               tool=self.partitioned_solid.solids[1])

    # Mirror right strut to get the left strut
    @Part
    def strut_left(self):
        return MirroredShape(shape_in=self.strut_right,
                             reference_point=Point(0, 0, 0),
                             vector1=self.position.Vx,
                             vector2=self.position.Vz)

    # Create aerodynamic surface for AVL analysis
    @Part
    def avl_surface(self):
        return avl.Surface(name="Struts",
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.cosine,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.cosine,
                           y_duplicate=self.position.point[1],
                           sections=[self.avl_section_up, self.avl_section_lo])


if __name__ == '__main__':
    from parapy.gui import display

    obj = StrutAirfoil(label="strut",
                       main_plate_span=3000,
                       strut_lat_location=0.1,
                       strut_chord=400,
                       strut_height=500,
                       strut_thickness=20,
                       strut_sweepback_angle=15,
                       strut_cant_angle=0)
    display(obj)
