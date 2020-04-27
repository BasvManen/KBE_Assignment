from spoiler_files.section import Section
from parapy.core import *
from parapy.geom import *
from math import atan, cos, sin, radians


class SectionProperties(GeomBase):
    # Main plate inputs
    airfoil_mid = Input()
    airfoil_tip = Input()
    spoiler_span = Input()
    spoiler_chord = Input()
    spoiler_angle = Input()
    spoiler_skin_thickness = Input()

    # Inputs for the discretisation of the spoiler sections
    n_discretise = Input(300)
    n_cuts = Input()

    # Define the two section similarly as in the mainplate file to get the
    # half span of the spoiler
    @Attribute
    def airfoil_names(self):
        return self.airfoil_mid, self.airfoil_tip

    @Attribute
    def section_positions(self):
        mid_position = self.position
        tip_position = self.position.translate('y', self.spoiler_span / 2)
        return mid_position, tip_position

    @Part(in_tree=False)
    def sections(self):
        return Section(quantify=2,
                       airfoil_name=self.airfoil_names[child.index],
                       chord=self.spoiler_chord,
                       angle=self.spoiler_angle,
                       position=self.section_positions[child.index])

    # Make a lofted surface so that curve-cutouts along the spoiler can be made
    @Part(in_tree=False)
    def surface_lofted(self):
        return LoftedSurface(
            profiles=[section.curve for section in self.sections])

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


if __name__ == '__main__':
    from parapy.gui import display

    obj = SectionProperties(label='Moment of Inertia',
                            airfoil_mid='0012',
                            airfoil_tip='0012',
                            spoiler_span=3.,
                            spoiler_chord=1.,
                            spoiler_angle=0.,
                            spoiler_skin_thickness=0.004,
                            n_discretise=300,
                            n_cuts=5)
    display(obj)
