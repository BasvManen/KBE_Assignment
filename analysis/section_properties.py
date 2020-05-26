from analysis.spoiler_files.section import Section
from parapy.core import *
from parapy.geom import *
from math import atan, cos, sin, radians


class SectionProperties(GeomBase):
    # Main plate inputs
    airfoils = Input()
    spoiler_span = Input()
    spoiler_chord = Input()
    spoiler_angle = Input()
    spoiler_skin_thickness = Input()
    n_ribs = Input()

    # Inputs for the discretisation of the spoiler sections
    n_discretise = Input(120)
    n_cuts = Input()

    @Part(in_tree=True)
    def sections(self):
        """ Create the sections based on the airfoils list input. They are
        translated such that the first section is at the mid and the last
        section is at the tip of the main plate. The other sections are placed
        equidistant from mid to tip. """
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

    @Part(in_tree=True)
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
        return ComposedCurve(quantify=self.n_cuts,
                             built_from=[self.cutout_curves[child.index][0]])

    # Retrieve the coordinates along the curve-cutouts
    @Attribute
    def coordinates_sections_points(self):
        crv = []
        for i in range(self.n_cuts):
            crv.append(self.spoiler_spanwise_cutout_curves[i].
                       equispaced_points(self.n_discretise))
        return crv

    # Discretise the cutouts into several small straight lines.
    @Attribute
    def amount_of_lines(self):
        return self.n_discretise - 1

    @Attribute
    def lines_on_airfoil(self):
        line_segment_list = []
        for i in range(self.n_cuts):
            line_segment_list.append([])
            for j in range(self.amount_of_lines):
                line_segment_list[i].append(
                    LineSegment(start=self.coordinates_sections_points[i][j],
                                end=self.coordinates_sections_points[i][
                                    j + 1]))
        return line_segment_list

    # Calculate the centroid position along the spoiler
    @Attribute
    def centroid_calculation(self):
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
        centroid_list = []
        for i in range(self.n_cuts):
            centroid_list.append(Point(self.centroid_calculation[i][0],
                                       self.centroid_calculation[i][1],
                                       self.centroid_calculation[i][2]))
        return centroid_list

    # Calculate the moment of inertia due to the displaced area with respect
    # to the centroid along the spoiler
    @Attribute
    def area_along_spoiler(self):
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

    # Calculate the moment of inertia due to the rectangular properties of
    # the discretised lines
    @Attribute
    def moment_inertia_area_rectangle(self):
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

    # Calculate the total moments of inertia (Ixx, Izz, Ixz)
    @Attribute
    def moment_inertia_total(self):
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

    # As the above calculations are for the half-spoiler only (since the
    # mainplate is first projected as one half and then mirrored),
    # this function makes for the moment of inertia along the whole spoiler
    # span.
    @Attribute
    def full_moment_of_inertia(self):
        full_moment_inertia_list = []
        for i in range(self.n_cuts * 2 - 1):
            if i < self.n_cuts:
                full_moment_inertia_list.append(
                    self.moment_inertia_total[self.n_cuts - i - 1])
            else:
                full_moment_inertia_list.append(
                    self.moment_inertia_total[i - self.n_cuts + 1])
        return full_moment_inertia_list

    # Calculate the placement of the ribs to calculate their weights
    @Attribute
    def position_ribs(self):
        n_ribs_calc = self.n_ribs + 2
        spacing_ribs = self.spoiler_span / (n_ribs_calc - 1)
        position_ribs = []
        for i in range(n_ribs_calc):
            position_ribs.append(i * spacing_ribs)
        spacing_discretisation = self.spoiler_span / 2 / (self.n_cuts - 1)
        ribs_indices = []
        for i in range(len(position_ribs)):
            for j in range(self.n_cuts + 1):
                y = self.spoiler_span / 2 + j * spacing_discretisation
                if y >= position_ribs[i] > (y - spacing_discretisation):
                    ribs_indices.append(j)
        return ribs_indices

    # Make rib curves
    @Part(in_tree=False)
    def rib_curves(self):
        return ComposedCurve(quantify=round((self.n_ribs + 2) / 2 + 0.1),
                             built_from=[self.cutout_curves[
                                             self.position_ribs[child.index]]
                                         [0]])

    @Part(in_tree=False)
    def ribs_right(self):
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
        return MirroredShape(quantify=round((self.n_ribs + 2) / 2 + 0.1)
                             if self.n_ribs % 2 == 0
                             else round((self.n_ribs + 2) / 2 + 0.1) - 1,
                             shape_in=self.ribs_right[child.index]
                             if self.n_ribs % 2 == 0
                             else self.ribs_right[child.index + 1],
                             reference_point=Point(0, 0, 0),
                             vector1=Vector(1, 0, 0),
                             vector2=Vector(0, 0, 1))

    @Part(in_tree=True)
    def ribs_total(self):
        return SewnSolid(quantify=self.n_ribs + 2,
                         built_from=self.ribs_right[child.index]
                         if child.index <= round((self.n_ribs + 2) / 2 + 0.1)-1
                         else self.ribs_left[
                             child.index - round((self.n_ribs + 2) / 2 + 0.1)])

    # Calculate the area of the ribs
    @Attribute
    def ribs_area(self):
        ribs_area_list = []
        for i in range(round((self.n_ribs + 2) / 2)):
            ribs_area_list.append(Face(self.rib_curves[i]).area)
        ribs_area_list = ribs_area_list[::-1] + ribs_area_list[1:]
        return ribs_area_list


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
