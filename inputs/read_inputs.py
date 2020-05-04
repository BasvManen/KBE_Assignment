
# Read inputs from geometry file
filename_geometry = 'input_geometry.dat'

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
airfoil_mid = airfoil[0]
airfoil_tip = airfoil[1]
spoiler_span = float(elements[7][0])
spoiler_chord = float(elements[8][0])
spoiler_angle = float(elements[9][0])

# Strut Inputs
strut_airfoil_shape = bool(elements[12][0])
strut_lat_location = float(elements[13][0])
strut_height = float(elements[14][0])
strut_chord = float(elements[15][0])
strut_thickness = float(elements[16][0])
strut_sweep = float(elements[17][0])
strut_cant = float(elements[18][0])

# Endplate Inputs
endplate_present = bool(elements[21][0])
endplate_thickness = float(elements[22][0])
endplate_sweep = float(elements[23][0])
endplate_cant = float(elements[24][0])


# Read inputs from materials file
filename_materials = 'input_material_properties.dat'

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
shear_modulus = float(elements[9][0])
shear_strength = float(elements[10][0])


# Read inputs from external flow conditions file
filename_materials = 'input_flow_conditions.dat'

mylines = []
elements = []
with open(filename_materials, 'r') as myfile:
    for myline in myfile:
        mylines.append(myline)
    for element in mylines:
        elements.append(element.split())

# External Flow Conditions
airspeed = float(elements[6][0])
maximum_airspeed = float(elements[7][0])
air_density = float(elements[8][0])
