
def read_geometry_inputs(filename_geometry):
    # Read inputs from geometry file

    mylines = []
    elements = []
    with open(filename_geometry, 'r') as myfile:
        for myline in myfile:
            mylines.append(myline)
        for element in mylines:
            elements.append(element.split())

    airfoil = []
    for i in range(len(elements[6])):
        if elements[6][i] == '#':
            break
        airfoil.append(elements[6][i])

    # MainPlate Inputs
    spoiler_airfoils = airfoil
    spoiler_span = float(elements[7][0])
    spoiler_chord = float(elements[8][0])
    spoiler_angle = float(elements[9][0])
    plate_amount = int(elements[10][0])

    # Strut Inputs
    strut_amount = int(elements[13][0])
    strut_airfoil_shape = bool(elements[14][0])
    strut_lat_location = float(elements[15][0])
    strut_height = float(elements[16][0])
    strut_chord_fraction = float(elements[17][0])
    strut_thickness = float(elements[18][0])
    strut_sweep = float(elements[19][0])
    strut_cant = float(elements[20][0])

    # Endplate Inputs
    endplate_present = bool(elements[23][0])
    endplate_thickness = float(elements[24][0])
    endplate_sweep = float(elements[25][0])
    endplate_cant = float(elements[26][0])

    # Car Inputs
    car_length = float(elements[29][0])
    car_width = float(elements[30][0])
    car_maximum_height = float(elements[31][0])
    car_middle_to_back_ratio = float(elements[32][0])

    return (spoiler_airfoils, spoiler_span, spoiler_chord, spoiler_angle,
            plate_amount, strut_amount, strut_airfoil_shape,
            strut_lat_location, strut_height, strut_chord_fraction,
            strut_thickness, strut_sweep, strut_cant, endplate_present,
            endplate_thickness, endplate_sweep, endplate_cant, car_length,
            car_width, car_maximum_height, car_middle_to_back_ratio)


def read_material_inputs(filename_materials):
    # Read inputs from materials file

    mylines = []
    elements = []
    with open(filename_materials, 'r') as myfile:
        for myline in myfile:
            mylines.append(myline)
        for element in mylines:
            elements.append(element.split())

    # Material Inputs
    material_density = float(elements[6][0])
    youngs_modulus = float(elements[7][0])
    yield_strength = float(elements[8][0])
    shear_strength = float(elements[9][0])
    poisson_ratio = float(elements[10][0])

    return material_density, youngs_modulus, yield_strength, \
        shear_strength, poisson_ratio


def read_flow_inputs(filename_flow):
    # Read inputs from external flow conditions file

    mylines = []
    elements = []
    with open(filename_flow, 'r') as myfile:
        for myline in myfile:
            mylines.append(myline)
        for element in mylines:
            elements.append(element.split())

    # External Flow Conditions
    airspeed = float(elements[6][0])
    maximum_airspeed = float(elements[7][0])
    air_density = float(elements[8][0])

    return airspeed, maximum_airspeed, air_density
