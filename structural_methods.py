import numpy as np

g = 9.80665


def distributed_force_moment(force_list, y_i, y_current):
    """
    This function is used in the calculation of the moment due to the
    distributed lift/weight/drag force of the spoiler as used in
    mainplate_bending_xz below. It uses a distributed
    force (force_list), the y-positions of that distributed force (y_i) and
    a current y location (y_current)
    """

    moment_list = []
    for i in range(len(force_list)):
        if y_i[i] < y_current:
            outcome = force_list[i] * (y_current - y_i[i])
        else:
            outcome = 0
        moment_list.append(outcome)
    return sum(moment_list)


def mainplate_bending_xz(lift, drag, E, Ixx, Izz, Ixz, spoiler_weight,
                         endplate_weight, spoiler_span, spoiler_chord,
                         strut_lat_location):
    """
    This function calculates the bending moment along the spoiler in x and
    z, as well as the bending displacement in x and z. It uses as inputs the
    aerodynamic forces on the spoiler, the material and sectional properties
    of the spoiler and the geometric properties of the spoiler.
    """

    # retrieve y-location of the struts
    strut_location_1 = spoiler_span / 2 * (1 - strut_lat_location)
    strut_location_2 = spoiler_span / 2 * (1 + strut_lat_location)

    # calculating y-coordinate, area and weight at each increment i. the
    # weight distribution is approximated by separate weight forces along
    # the spoiler, which are appropriate to the area of the spoiler at each i.
    y_i = np.zeros(len(lift) + 1)
    y_ii = np.zeros(len(lift))
    area_i = np.zeros(len(lift))
    weight_i = np.zeros(len(lift))
    di = spoiler_span / len(lift)

    for i in range(len(lift) + 1):
        y_i[i] = round(i * di, 3)

    for i in range(len(lift)):
        y_ii[i] = y_i[i] + (y_i[i + 1] - y_i[i]) / 2
        area_i[i] = spoiler_chord * di
        weight_i[i] = -spoiler_weight * g / (spoiler_chord * spoiler_span) \
                      * area_i[i]

    # adding the weight of the endplate to the first and last weight_i
    weight_i[0] += endplate_weight * g
    weight_i[-1] += endplate_weight * g

    # calculate the z-force on the strut by sum of forces in z
    f_strut_z = -(sum(lift) + sum(weight_i)) / 2
    # calculate the z-force on the strut by sum of forces in x
    f_strut_x = -sum(drag) / 2

    # calculate the influence of the lift and weight on the bending moment
    # for each increment i
    moment_lift_i = []
    moment_weight_i = []
    moment_drag_i = []
    for i in range(len(lift) + 1):
        y_set = y_i[i]
        moment_lift = distributed_force_moment(lift, y_ii, y_set)
        moment_weight = distributed_force_moment(weight_i, y_ii, y_set)
        moment_drag = distributed_force_moment(drag, y_ii, y_set)
        moment_lift_i.append(moment_lift)
        moment_weight_i.append(moment_weight)
        moment_drag_i.append(moment_drag)

    # calculating the moment in x along the spoiler
    moment_x_i = []
    for i in range(len(lift) + 1):
        y_set = y_i[i]
        if y_set >= strut_location_2 and y_set >= strut_location_1:
            mom_i = f_strut_z * (y_set - strut_location_2) + f_strut_z \
                    * (y_set - strut_location_1) \
                    + moment_lift_i[i] + moment_weight_i[i]
            moment_x_i.append(mom_i)
        elif strut_location_2 > y_set >= strut_location_1:
            mom_i = f_strut_z * (y_set - strut_location_1) + moment_lift_i[i] \
                    + moment_weight_i[i]
            moment_x_i.append(mom_i)
        elif y_set < strut_location_2 and y_set < strut_location_1:
            mom_i = moment_lift_i[i] + moment_weight_i[i]
            moment_x_i.append(mom_i)

    # calculating the moment in z along the spoiler
    moment_z_i = []
    for i in range(len(drag) + 1):
        y_set = y_i[i]
        if y_set >= strut_location_2 and y_set >= strut_location_1:
            mom_i = f_strut_x * (y_set - strut_location_2) + f_strut_x \
                    * (y_set - strut_location_1) + moment_drag_i[i]
            moment_z_i.append(mom_i)
        elif strut_location_2 > y_set >= strut_location_1:
            mom_i = f_strut_x * (y_set - strut_location_1) + moment_drag_i[i]
            moment_z_i.append(mom_i)
        elif y_set < strut_location_2 and y_set < strut_location_1:
            mom_i = moment_drag_i[i]
            moment_z_i.append(mom_i)

    # Calculate deflection angles and displacement using Euler-Bernoulli
    # beam theory in unsymmetrical bending. The deflection angle (theta) in the
    # centerline of the spoiler is 0. The deflections at the struts are
    # considered equal to 0. Deflections in z are described by w,
    # and deflections in x are described by u.
    w_double_prime = np.zeros(len(lift) + 1)
    u_double_prime = np.zeros(len(drag) + 1)
    theta_x_i = np.zeros(len(lift) + 1)
    theta_z_i = np.zeros(len(drag) + 1)
    for i in range(len(lift) + 1):
        w_double_prime[i] = (moment_z_i[i] * Ixz[i] / (E * Ixx[i] * Izz[i])
                             - moment_x_i[i] / (E * Ixx[i])) \
                            / (1 - Ixz[i] ** 2 / (Ixx[i] * Izz[i]))
        u_double_prime[i] = (moment_x_i[i] * Ixz[i] / (E * Ixx[i] * Izz[i])
                             - moment_z_i[i] / (E * Izz[i])) \
                            / (1 - Ixz[i] ** 2 / (Ixx[i] * Izz[i]))

    for i in range(int(len(lift) / 2) + 1, len(lift) + 1):
        theta_x_i[i] = theta_x_i[i - 1] + 0.5 * (
                -w_double_prime[i] - w_double_prime[i - 1]) * (
                               y_i[i] - y_i[i - 1])
        theta_z_i[i] = theta_z_i[i - 1] + 0.5 * (
                -u_double_prime[i] - u_double_prime[i - 1]) * (
                               y_i[i] - y_i[i - 1])

    index_strut = np.where(y_i >= strut_location_2)[0][0]
    w_i = np.zeros(len(lift) + 1)
    u_i = np.zeros(len(lift) + 1)
    for i in range(index_strut, len(lift) + 1):
        w_i[i] = w_i[i - 1] + 0.5 * (theta_x_i[i] + theta_x_i[i - 1]) * (
                y_i[i] - y_i[i - 1])
        u_i[i] = u_i[i - 1] + 0.5 * (theta_z_i[i] + theta_z_i[i - 1]) * (
                y_i[i] - y_i[i - 1])

    for i in range(index_strut + 1, int(len(lift) / 2), -1):
        w_i[i - 1] = w_i[i] - 0.5 * (theta_x_i[i] + theta_x_i[i - 1]) * (
                y_i[i] - y_i[i - 1])
        u_i[i - 1] = u_i[i] - 0.5 * (theta_z_i[i] + theta_z_i[i - 1]) * (
                y_i[i] - y_i[i - 1])

    for i in range(int(len(lift) / 2)):
        theta_x_i[i] = theta_x_i[len(lift) - i]
        theta_z_i[i] = theta_z_i[len(lift) - i]
        w_i[i] = w_i[len(lift) - i]
        u_i[i] = u_i[len(lift) - i]

    return theta_x_i, theta_z_i, w_i, u_i, y_i, moment_x_i, moment_z_i, \
           f_strut_z, f_strut_x


def normal_stress_due_to_strut(force_in_y, y_i, area_distribution,
                               strut_lat_location, spoiler_span):
    """
    Function which calculates the normal stress along the spoiler, due to
    the normal force which is present due to the cant angle of the struts.
    """

    # retrieve y-location of the struts
    strut_location_1 = spoiler_span / 2 * (1 - strut_lat_location)
    strut_location_2 = spoiler_span / 2 * (1 + strut_lat_location)

    # make normal force distribution
    normal_force = np.zeros(len(y_i))
    for i in range(len(y_i)):
        if y_i[i] < strut_location_1 or y_i[i] > strut_location_2:
            normal_force[i] = 0
        elif strut_location_1 <= y_i[i] <= strut_location_2:
            normal_force[i] = force_in_y

    # make normal stress distribution
    sigma_y = []
    for i in range(len(y_i)):
        sigma_y.append(normal_force[i] / area_distribution[i])

    return sigma_y


def bending_stress(moment_x, moment_z, Ixx, Izz, Ixz, line_coordinates,
                   centroid_list):
    """
    Function which calculates the normal stress along the spoiler due to the
    bending moment along the spoiler. It returns an array of the normal
    bending stress along the spoiler, as well as the maximum stress along
    the spoiler.
    """

    # initialise the x and z coordinates along the span
    x = []
    z = []
    for i in range(len(line_coordinates)):
        x.append([])
        z.append([])
        for j in range(len(line_coordinates[0])):
            x[i].append(line_coordinates[i][j][0])
            z[i].append(line_coordinates[i][j][2])

    # x and z coordinates of the centroid
    x_centroid = []
    z_centroid = []
    for i in range(len(centroid_list)):
        x_centroid.append(centroid_list[i][0])
        z_centroid.append(centroid_list[i][2])

    # calculate the normal stress due to bending
    sigma_y = []
    sigma_y_max = []
    for i in range(len(line_coordinates)):
        sigma_y.append([])
        for j in range(len(line_coordinates[i])):
            calc_sigma = moment_x[i] \
                         * (Izz[i] * (z[i][j] - z_centroid[i])
                            - Ixz[i] * (x[i][j] - x_centroid[i])) \
                         / (Ixx[i] * Izz[i] - Ixz[i] ** 2) \
                         + moment_z[i] \
                         * (Ixx[i] * (x[i][j] - x_centroid[i])
                            - Ixz[i] * (z[i][j] - z_centroid[i])) \
                         / (Ixx[i] * Izz[i] - Ixz[i] ** 2)
            sigma_y[i].append(calc_sigma)
        sigma_y_max.append(max(sigma_y[i])
                           if abs(max(sigma_y[i])) > abs(min(sigma_y[i]))
                           else min(sigma_y[i]))

    return sigma_y, sigma_y_max
