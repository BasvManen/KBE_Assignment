from analysis.spoiler_files.section import Section
from parapy.core import *
from parapy.geom import *
from math import atan, cos, sin, radians


###############################################################################
# SECTIONAL PROPERTIES CLASS                                                  #
# In this file, several sectional properties along the spoiler are calculated #
#                                                                             #
# Inputs:                                                                     #
# - airfoils, defined in a list of strings. See documentation of the Section  #
#   class for profile definition.                                             #
# - Span of the main plate                                                    #
# - Chord of the main plate                                                   #
# - Angle of the main plate, positive defined upwards                         #
# - Skin thickness of the spoiler for the structural calculations             #
# - Number of ribs in the spoiler main plate                                  #
# - n_cuts, defined as the amount of span-wise cuts are made along the        #
#   y-direction of the main plate.                                            #
# - n_discretise, which is the number of equidistant cuts along each of the   #
#   cross sectional airfoil cutouts of the main plate. Optionally,            #
#   n_discretise can be set higher in order to get a more accurate            #
#   approximation of several of the sectional properties.                     #
###############################################################################

class SectionProperties(GeomBase):

    # Main plate inputs
    airfoils = Input()
    spoiler_span = Input()
    spoiler_chord = Input()
    spoiler_angle = Input()
    spoiler_skin_thickness = Input()
    n_ribs = Input()

    # Inputs for the discretisation of the spoiler sections
    n_cuts = Input()
    n_discretise = Input(120)

    @Part(in_tree=False)
    def sections(self):
        """ As similarly in MainPlate, create the sections based on the
        airfoils list input. They are translated such that the first section
        is at the mid and the last section is at the tip of the main plate.
        The other sections are placed equidistant from mid to tip. """
        return Section(quantify=len(self.airfoils),
                       airfoil_name=self.airfoils[child.index],
                       chord=self.spoiler_chord,
                       position=self.position if child.index == 0
                       # Position the mid section at the mid of the main plate
                       else translate(child.previous.position,
                                      'y',
                                      0.5 * self.spoiler_span / (
                                              len(self.airfoils) - 1))
                       if child.index != len(self.airfoils) - 1
                       # Position the intermediate sections equidistant
                       else translate(child.previous.position,
                                      'y',
                                      0.5 * self.spoiler_span /
                                      (len(self.airfoils) - 1)))

    @Part(in_tree=False)
    def surface_lofted(self):
        """ Create the main plate based on the sections defined in the
        sections part. The main plate is then rotated based on the spoiler
        angle given as input. """
        return RotatedSurface(surface_in=LoftedSurface(profiles=[section.curve
                                                                 for section in
                                                                 self.sections],
                                                       ),
                              rotation_point=self.position.point,
                              vector=self.position.Vy,
                              angle=radians(-self.spoiler_angle),
                              mesh_deflection=1e-4)

    @Attribute
    def cutout_curves(self):
        """ This attribute returns a list of equidistantly distanced cross
        section cutouts, in the span-wise direction. """
        spacing = self.spoiler_span / 2 / (self.n_cuts - 1)
        cutout_list = []
        for i in range(self.n_cuts):
            cutout_list.append(self.surface_lofted.intersection_curves(
                other_surface=Plane(reference=translate(self.position,
                                                        "y", i * spacing),
                                    normal=self.position.Vy)))
        return cutout_list

    @Part(in_tree=False)
    def spoiler_spanwise_cutout_curves(self):
        """ The cutout_curves list is here used to create several curve
        parts, these parts are used for several sectional property
        calculations. """
        return ComposedCurve(quantify=self.n_cuts,
                             built_from=[self.cutout_curves[child.index][0]])

    @Attribute
    def coordinates_sections_points(self):
        """ This attribute retrieves the equidistant coordinates on each of
        the curve parts. """
        crv = []
        for i in range(self.n_cuts):
            crv.append(self.spoiler_spanwise_cutout_curves[i].
                       equispaced_points(self.n_discretise))
        return crv

    @Attribute
    def amount_of_lines(self):
        """ This attribute returns the amount of needed discretised straight
        lines on each of the cutout curves. """
        return self.n_discretise - 1

    @Attribute
    def lines_on_airfoil(self):
        """ This attribute creates small linear lines between each of the
        coordinate points of the cutout curves along the spoiler. """
        line_segment_list = []
        for i in range(self.n_cuts):
            line_segment_list.append([])
            for j in range(self.amount_of_lines):
                line_segment_list[i].append(
                    LineSegment(start=self.coordinates_sections_points[i][j],
                                end=self.coordinates_sections_points[i][
                                    j + 1]))
        return line_segment_list

    @Attribute
    def centroid_calculation(self):
        """ This attribute calculates the centroid's position (x, y and z
        coordinate) of each of the cutout curves along the spoiler. """
        centroid_calculation_list = []
        for i in range(self.n_cuts):
            x = 0
            y = self.lines_on_airfoil[i][0].position.y
            z = 0
            for j in range(self.amount_of_lines):
                x = x + (self.lines_on_airfoil[i][j].midpoint.x
                         * self.lines_on_airfoil[i][j].length
                         * self.spoiler_skin_thickness) \
                    / (self.amount_of_lines
                       * self.lines_on_airfoil[i][j].length
                       * self.spoiler_skin_thickness)
                z = z + (self.lines_on_airfoil[i][j].midpoint.z
                         * self.lines_on_airfoil[i][j].length
                         * self.spoiler_skin_thickness) \
                    / (self.amount_of_lines
                       * self.lines_on_airfoil[i][j].length
                       * self.spoiler_skin_thickness)
            centroid_calculation_list.append([x, y, z])
        return centroid_calculation_list

    @Attribute
    def centroid(self):
        """ This attribute creates Point instances for each of the centroids
        along the spoiler. """
        centroid_list = []
        for i in range(self.n_cuts):
            centroid_list.append(Point(self.centroid_calculation[i][0],
                                       self.centroid_calculation[i][1],
                                       self.centroid_calculation[i][2]))
        return centroid_list

    @Attribute
    def area_along_spoiler(self):
        """ This attribute calculates the total cross sectional area of each
        of the cutouts along the spoiler. """
        area_list = []
        for i in range(self.n_cuts):
            area_cut = []
            for j in range(self.amount_of_lines):
                area_cut.append(self.lines_on_airfoil[i][j].length
                                * self.spoiler_skin_thickness)
            area_list.append(sum(area_cut))
        return area_list

    @Attribute
    def moment_inertia_displaced_area(self):
        """ This attribute calculates the first part (due to displaced area
        theorem) of the moment of inertia of each of the cutouts. It
        calculates the area of each of the line segments on the cutouts and
        multiplies it with the square of the distance between the line
        segment and the centroid of that cutout. """
        moment_inertia_displaced_area_list = []
        for i in range(self.n_cuts):
            ix_area = 0
            iz_area = 0
            ixz_area = 0
            for j in range(self.amount_of_lines):
                ix_area = ix_area + (self.lines_on_airfoil[i][j].length
                                     * self.spoiler_skin_thickness) \
                          * (self.lines_on_airfoil[i][j].midpoint.z
                             - self.centroid_calculation[i][2]) ** 2
                iz_area = iz_area + (self.lines_on_airfoil[i][j].length
                                     * self.spoiler_skin_thickness) \
                          * (self.lines_on_airfoil[i][j].midpoint.x
                             - self.centroid_calculation[i][0]) ** 2
                ixz_area = ixz_area + (self.lines_on_airfoil[i][j].length
                                       * self.spoiler_skin_thickness) \
                           * (self.lines_on_airfoil[i][j].midpoint.z
                              - self.centroid_calculation[i][2]) \
                           * (self.lines_on_airfoil[i][j].midpoint.x
                              - self.centroid_calculation[i][0])
            moment_inertia_displaced_area_list.append([ix_area,
                                                       iz_area,
                                                       ixz_area])
        return moment_inertia_displaced_area_list

    @Attribute
    def moment_inertia_area_rectangle(self):
        """ This attribute calculates the second part (due to geometric
        properties) of the moment of inertia of each of the cutouts. It
        calculates for each of the (angled) line segments along the cutout,
        the moments of inertia of a rectangle. """
        moment_inertia_area_rectangle_list = []
        for i in range(self.n_cuts):
            ix = 0
            iz = 0
            ixz = 0
            for j in range(self.amount_of_lines):
                iu = 1 / 12 * self.lines_on_airfoil[i][
                    j].length * self.spoiler_skin_thickness ** 3
                iw = 1 / 12 * self.spoiler_skin_thickness * \
                     self.lines_on_airfoil[i][j].length ** 3
                theta = radians(90) if abs(
                    self.lines_on_airfoil[i][j].point1.x -
                    self.lines_on_airfoil[i][j].point2.x) < (10 ** -10) \
                    else atan((self.lines_on_airfoil[i][j].point1.z -
                               self.lines_on_airfoil[i][j].point2.z)
                              / (self.lines_on_airfoil[i][j].point1.x -
                                 self.lines_on_airfoil[i][j].point2.x))
                ix = ix + ((iu + iw) / 2 + (iu - iw) / 2 * cos(2 * theta))
                iz = iz + ((iu + iw) / 2 - (iu - iw) / 2 * cos(2 * theta))
                ixz = ixz + ((iu - iw) / 2 * sin(2 * theta))
            moment_inertia_area_rectangle_list.append([ix, iz, ixz])
        return moment_inertia_area_rectangle_list

    @Attribute
    def moment_inertia_total(self):
        """ This attribute calculates the total moments of inertia (Ixx,
        Izz, Ixz) from the displaced area and geometric attributes above. """
        moment_inertia_list = []
        for i in range(self.n_cuts):
            ix_total = self.moment_inertia_displaced_area[i][0] + \
                       self.moment_inertia_area_rectangle[i][0]
            iz_total = self.moment_inertia_displaced_area[i][1] + \
                       self.moment_inertia_area_rectangle[i][1]
            ixz_total = self.moment_inertia_displaced_area[i][2] + \
                        self.moment_inertia_area_rectangle[i][2]
            moment_inertia_list.append([ix_total, iz_total, ixz_total])
        return moment_inertia_list

    @Attribute
    def full_moment_of_inertia(self):
        """ As the above calculations are for the half-spoiler only (since the
        main plate is first only projected as one half and later mirrored),
        this attribute returns the moments of inertia along the whole spoiler
        span."""
        full_moment_inertia_list = []
        for i in range(self.n_cuts * 2 - 1):
            if i < self.n_cuts:
                full_moment_inertia_list.append(
                    self.moment_inertia_total[self.n_cuts - i - 1])
            else:
                full_moment_inertia_list.append(
                    self.moment_inertia_total[i - self.n_cuts + 1])
        return full_moment_inertia_list

    @Attribute
    def position_ribs(self):
        """ This attribute calculates the position of the ribs along the
        half-span of the main plate. It first calculates the exact
        y-position, after which the rib curves are associated with the
        nearest discretised cutout curve, in term of their indices. """
        # total amount of ribs including spoiler tips
        n_ribs_calc = self.n_ribs + 2
        spacing_ribs = self.spoiler_span / (n_ribs_calc - 1)
        # calculate the exact y location of the ribs
        position_ribs = []
        for i in range(n_ribs_calc):
            position_ribs.append(i * spacing_ribs)
        # assign the ribs to the nearest discretised cutout curve
        spacing_discretisation = self.spoiler_span / 2 / (self.n_cuts - 1)
        ribs_indices = []
        for i in range(len(position_ribs)):
            for j in range(self.n_cuts + 1):
                y = self.spoiler_span / 2 + j * spacing_discretisation
                if y >= position_ribs[i] > (y - spacing_discretisation):
                    ribs_indices.append(j)
        return ribs_indices

    @Part(in_tree=False)
    def rib_curves(self):
        """ This part creates the rib curves from the position_ribs
        attribute. """
        return ComposedCurve(quantify=round((self.n_ribs + 2) / 2 + 0.1),
                             built_from=[self.cutout_curves[
                                             self.position_ribs[child.index]]
                                         [0]])

    @Attribute
    def ribs_area(self):
        """ This attribute calculates the cross sectional area of each of
        the ribs. """
        ribs_area_list = []
        for i in range(round((self.n_ribs + 2) / 2)):
            ribs_area_list.append(Face(self.rib_curves[i]).area)
        ribs_area_list = ribs_area_list[::-1] + ribs_area_list[1:]
        return ribs_area_list

    @Part(in_tree=False)
    def ribs_right(self):
        """ This part creates all ribs (with the same thickness as the
        skin_thickness) on one side of the spoiler. Later this can be used
        to mirror the ribs to the other side of the spoiler. """
        return RuledSolid(quantify=round((self.n_ribs + 2) / 2 + 0.1),
                          profile1=self.rib_curves[child.index],
                          profile2=
                          TranslatedCurve(curve_in=
                                          self.rib_curves[child.index],
                                          displacement=
                                          Vector(0.,
                                                 self.spoiler_skin_thickness,
                                                 0.)))

    @Part(in_tree=False)
    def ribs_left(self):
        """ Here ribs_right are mirrored in the center plane of the spoiler
        (except the rib which located in the center plane of the
        main plate in case of an uneven rib total). """
        return MirroredShape(quantify=round((self.n_ribs + 2) / 2 + 0.1)
                             if self.n_ribs % 2 == 0
                             else round((self.n_ribs + 2) / 2 + 0.1) - 1,
                             shape_in=self.ribs_right[child.index]
                             if self.n_ribs % 2 == 0
                             else self.ribs_right[child.index + 1],
                             reference_point=Point(0, 0, 0),
                             vector1=Vector(1, 0, 0),
                             vector2=Vector(0, 0, 1))

    @Part(in_tree=False)
    def ribs_total(self):
        """ This part fuses the ribs_right and ribs_left parts together,
        to create one instance of rib parts. """
        return SewnSolid(quantify=self.n_ribs + 2,
                         built_from=self.ribs_right[child.index]
                         if child.index <= round((self.n_ribs + 2) / 2 + 0.1)-1
                         else self.ribs_left[
                             child.index - round((self.n_ribs + 2) / 2 + 0.1)])




if __name__ == '__main__':
    from parapy.gui import display

    obj = SectionProperties(airfoils=['test', 'test'],
                            spoiler_span=1600.,
                            spoiler_chord=300.,
                            spoiler_angle=10.,
                            spoiler_skin_thickness=2,
                            n_cuts=40,
                            n_ribs=0)
    display(obj)
