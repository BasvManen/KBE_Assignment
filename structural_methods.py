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

    # initialise the x and z coordinates along the span w.r.t. the centroid
    x = []
    z = []
    for i in range(len(line_coordinates)):
        x.append([])
        z.append([])
        for j in range(len(line_coordinates[0])):
            x[i].append(line_coordinates[i][j][0] - centroid_list[i][0])
            z[i].append(line_coordinates[i][j][2] - centroid_list[i][2])

    # calculate the normal stress due to bending
    sigma_y = []
    sigma_y_max = []
    for i in range(len(line_coordinates)):
        sigma_y.append([])
        for j in range(len(line_coordinates[i])):
            calc_sigma = moment_x[i] * (Izz[i] * z[i][j] - Ixz[i] * x[i][j]) \
                         / (Ixx[i] * Izz[i] - Ixz[i] ** 2) + moment_z[i] \
                         * (Ixx[i] * x[i][j] - Ixz[i] * z[i][j]) \
                         / (Ixx[i] * Izz[i] - Ixz[i] ** 2)
            sigma_y[i].append(calc_sigma)
        sigma_y_max.append(max(sigma_y[i])
                           if abs(max(sigma_y[i])) > abs(min(sigma_y[i]))
                           else min(sigma_y[i]))

    return sigma_y, sigma_y_max


def max_shear_stress(force_x, force_z, skin_thickness, Ixx, Izz, Ixz,
                     line_coordinates, centroid_list):
    """
    Function which calculates the shear stress along the spoiler due to the
    lift and drag forces along the spoiler. It returns an array of the
    maximum shear stress along the spoiler.
    """

    # initialise the x and z coordinates along the span w.r.t. the centroid
    x = []
    z = []
    for i in range(len(line_coordinates)):
        x.append([])
        z.append([])
        for j in range(len(line_coordinates[0])):
            x[i].append(line_coordinates[i][j][0] - centroid_list[i][0])
            z[i].append(line_coordinates[i][j][2] - centroid_list[i][2])

    # basic shear flow along the cutout along the spoiler span
    q_b = []  # basic shear flow
    q_b_i = []  # integration of q_b for calculating the q_s,0
    q_s_0 = []  # closed section shear flow
    q_total = []  # q_total = q_b + q_s_0
    tau_total = []  # actual shear stress
    line_length = []
    for i in range(len(line_coordinates) - 1):
        q_b.append([0])
        q_b_i.append([0])
        line_length.append(np.sqrt((line_coordinates[i][0][0]
                                    - line_coordinates[i][1][0]) ** 2
                                   + (line_coordinates[i][0][2]
                                      - line_coordinates[i][1][2]) ** 2))
        for j in range(1, len(line_coordinates[0])):
            q_b[i].append(q_b[i][j - 1]
                          - (force_x[i] * Ixx[i] - force_z[i] * Ixz[i])
                          / (Ixx[i] * Izz[i] - Ixz[i] ** 2) * skin_thickness
                          * ((x[i][j] - x[i][j - 1]) / 2 * line_length[i]
                             + x[i][j] * line_length[i]))
            q_b_i[i].append(q_b_i[i][j - 1]
                            - (force_x[i] * Ixx[i] - force_z[i] * Ixz[i])
                            / (Ixx[i] * Izz[i] - Ixz[i] ** 2) * skin_thickness
                            * ((x[i][j] - x[i][j - 1]) / 6
                               * line_length[i] ** 2
                               + x[i][j] / 2 * line_length[i] ** 2))

    # Calculate total shear flow along the cutout along the spoiler span
    for i in range(len(line_coordinates) - 1):
        q_total.append([])
        q_s_0.append(
            sum(q_b_i[i]) / (line_length[i] * len(line_coordinates[0])))
        for j in range(len(line_coordinates[0])):
            q_total[i].append(q_b[i][j] + q_s_0[i])

    # Calculate the maximum shear stress
    for i in range(len(line_coordinates) - 1):
        if max(q_total[i]) > abs(min(q_total[i])):
            tau_total.append(max(q_total[i]) / skin_thickness)
        else:
            tau_total.append(min(q_total[i]) / skin_thickness)

    return tau_total


def buckling_modes(n_ribs, span, chord, skin_thickness, Ixx_list, Izz_list,
                   area_list, youngs_modulus, poisson_ratio):
    """
    Function which calculates the critical buckling stresses that the
    spoiler can withstand. It returns the critical compressive stress,
    critical shear stress and critical column buckling stress.
    """
    # calculate effective plate length and width
    a = span / (n_ribs + 2)
    b = chord
    b_shear = b if b < a else a

    # Set critical buckling coefficients
    k_compression = 6.0
    k_shear = 7.5

    # Calculate normal and shear critical buckling stress
    sigma_crit = ((k_compression * np.pi ** 2 * youngs_modulus)
                  / (12 * (1 - poisson_ratio ** 2))
                  * (skin_thickness / b) ** 2) / 10 ** 6
    tau_crit = ((k_shear * np.pi ** 2 * youngs_modulus)
                / (12 * (1 - poisson_ratio ** 2))
                * (skin_thickness / b_shear) ** 2) / 10 ** 6

    # Calculate the critical column buckling stress
    # calculate radius of gyration in z using averages
    I_min = min([sum(Izz_list) / len(Izz_list), sum(Ixx_list) / len(Ixx_list)])
    area_avg = (sum(area_list) / len(area_list))
    sigma_column_crit = ((np.pi ** 2 * youngs_modulus * I_min)
                         / (a ** 2 * area_avg)) / 10 ** 6

    return sigma_crit, tau_crit, sigma_column_crit


def failure_modes(max_tensile_stress, max_compression_stress,
                  maxi_shear_stress, maximum_deflection, sigma_crit, tau_crit,
                  sigma_column_crit, span, yield_strength, shear_strength):
    """
    Function which determines whether the spoiler fails or not. It returns a
    bool which is True if failure occurs and is False when no failure occurs.
    """
    # failure determines whether the spoiler fails or not
    # False for no structural failure, True for structural failure
    failure = False
    failure_mode = [False, False, False, False, False, False]

    if max_tensile_stress > yield_strength:
        failure = True
        failure_mode[0] = True
    if max_compression_stress > sigma_crit:
        failure = True
        failure_mode[1] = True
    if maxi_shear_stress > shear_strength:
        failure = True
        failure_mode[2] = True
    if maxi_shear_stress > tau_crit:
        failure = True
        failure_mode[3] = True
    if maximum_deflection > 0.025 * span:
        failure = True
        failure_mode[4] = True
    if max_compression_stress > sigma_column_crit:
        failure_mode[5] = True

    # Check whether failure is only due to column buckling, if so, increase
    # amount of ribs
    due_to_ribs = False
    if max_compression_stress > sigma_column_crit and not failure:
        due_to_ribs = True

    return failure, due_to_ribs, failure_mode
