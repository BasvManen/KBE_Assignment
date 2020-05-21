from math import radians, sin, cos, tan
from parapy.core import Input, Attribute, Part
from parapy.geom import *
from kbeutils.geom.curve import Naca4AirfoilCurve
import kbeutils.avl as avl

###############################################################################
# AIRFOIL-SHAPED STRUT CLASS                                                  #
# In this file, the spoiler struts with airfoil shapes are defined. It can    #
# return a single strut part, which will be partioned and correctly           #
# translated in the SpoilerAssembly class.                                    #
#                                                                             #
# Inputs:                                                                     #
# - Chord of the struts, as fraction of the chord of the main plate           #
# - Height of the struts, as defined from car base to spoiler base            #
# - Thickness of the struts                                                   #
# - Sweepback angle of the struts                                             #
# - Cant angle of the struts                                                  #
# - main, defined as a Part entry of the main plate geometry                  #
###############################################################################


class StrutAirfoil(GeomBase):

    chord_fraction = Input()
    strut_height = Input()
    strut_thickness = Input()
    strut_sweepback_angle = Input()
    strut_cant_angle = Input()
    main = Input()

    do_avl = Input(False)

    @Attribute
    def strut_chord(self):
        """" This attribute calculates the actual chord of the struts,
        which is defined in the x-direction. It makes sure that the chord of
        the strut will never exceed the chord (projected in x-direction) of
        the main plate. """
        return self.main.chord * self.chord_fraction \
               * cos(radians(self.main.angle))

    @Attribute
    def thickness_to_chord(self):
        """ This attribute calculates the thickness to chord ratio for the
        symmetric airfoil shape. This is further used in the retrieval of
        the NACA 4-digit airfoil name and the wetted area calculation. The
        airfoil cannot get too thick or thin, for AVL related reasons. """
        if round(self.strut_thickness / self.strut_chord * 100) < 2:
            ratio = 2
        elif round(self.strut_thickness / self.strut_chord * 100) > 40:
            ratio = 40
        else:
            ratio = int(self.strut_thickness / self.strut_chord * 100)
        return ratio

    @Attribute
    def symmetric_airfoil_name(self):
        """ This attribute retrieves the NACA 4-digit symmetric airfoil name,
        based on the thickness to chord ratio. """
        if self.thickness_to_chord >= 10:
            name = '00' + str(self.thickness_to_chord)
        else:
            name = '000' + str(self.thickness_to_chord)
        return name

    # Define wetted area
    @Attribute
    def wetted_area(self):
        """ This attribute calculates the total wetted area of the struts



        """
        return 2 * self.strut_chord * self.strut_height * \
               (0.5*self.thickness_to_chord/100 + 1.98)

    @Part(in_tree=False)
    def airfoil(self):
        """ Create the unscaled symmetric airfoil profile curve, based on
        the symmetric airfoil name and the Naca4AirfoilCurve generator. Also
        directly orient the curve in the right direction by rotating it. """
        return RotatedCurve(
            curve_in=Naca4AirfoilCurve(self.symmetric_airfoil_name,
                                       n_points=200),
            rotation_point=XOY,
            vector=self.position.Vx, angle=radians(90))

    @Part(in_tree=False)
    def upper_curve_airfoil(self):
        """ Scale the airfoil curve to the right calculated strut chord.
        This curve is later used for creating a ruled solid. """
        return ScaledCurve(curve_in=self.airfoil,
                           reference_point=XOY,
                           factor=self.strut_chord)

    @Part(in_tree=False)
    def lower_curve_airfoil(self):
        """ Create the lower airfoil curve for the ruled solid,
        by translating the upper curve in the right direction by means of
        strut height, sweepback angle and cant angle. """
        return TranslatedCurve(curve_in=self.upper_curve_airfoil,
                               displacement=Vector(-self.strut_height * tan(
                                   radians(self.strut_sweepback_angle)),
                                                   -self.strut_height * tan(radians(
                                                       self.strut_cant_angle)),
                                                   -self.strut_height))

    # Initialise AVL input for the struts
    @Part(in_tree=False)
    def avl_section_up(self):
        return avl.SectionFromCurve(curve_in=self.upper_curve_airfoil)

    @Part(in_tree=False)
    def avl_section_lo(self):
        return avl.SectionFromCurve(curve_in=self.lower_curve_airfoil)

    @Part(in_tree=False)
    def extended_airfoil(self):
        """ In order to cut off the strut at the lower side of the main
        plate (at any main plate angle), the strut upper curve is extended
        to a higher z-location from where it can be easily partioned. The
        upper curve is extended in the correct direction by means of the
        strut height, sweepback angle and the cant angle. This instance will
        make sure that the strut is always attached to the lower side of the
        main plate. """
        return TranslatedCurve(curve_in=self.upper_curve_airfoil,
                               displacement=
                               Vector((self.strut_height + self.main.chord)
                                      * sin(radians(self.strut_sweepback_angle)),
                                      (self.strut_height + self.main.chord)
                                      * sin(radians(self.strut_cant_angle)),
                                      self.strut_height + self.main.chord))

    # Create the initial solid for the extended strut, which will be
    # subtracted in the assembly class
    @Part(in_tree=True)
    def strut(self):
        """ Create the initial ruled solid for the extended strut from the
        airfoil curves. This instance will later be cut-off at the lower
        side of the main plate, and subtracted in the SpoilerAssembly class.
        """
        return RuledSolid(profile1=self.extended_airfoil,
                          profile2=self.lower_curve_airfoil,
                          mesh_deflection=1e-5)

    # # Initialise subtraction of the solid at the main plate lower surface by
    # # cutting the solid into several pieces.
    # @Part(in_tree=False)
    # def partitioned_solid(self):
    #     return PartitionedSolid(solid_in=self.main.surface,
    #                             tool=self.solid,
    #                             keep_tool=True,
    #                             mesh_deflection=1e-5)
    #
    # # Create part of the strut from the subtracted solid
    # @Part
    # def strut(self):
    #     return SubtractedSolid(shape_in=SubtractedSolid(shape_in=self.solid,
    #                                                     tool=self.partitioned_solid.solids[2]),
    #                            tool=self.partitioned_solid.solids[1],
    #                            mesh_deflection=1e-5)

    # Create aerodynamic surface for AVL analysis
    @Part
    def avl_surface(self):
        return avl.Surface(name="Struts",
                           n_chordwise=12,
                           chord_spacing=avl.Spacing.cosine,
                           n_spanwise=20,
                           span_spacing=avl.Spacing.cosine,
                           y_duplicate=self.position.point[1],
                           sections=[self.avl_section_up, self.avl_section_lo],
                           hidden=not self.do_avl)
