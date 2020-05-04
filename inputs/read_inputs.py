from parapy.geom import *
from parapy.core import *

filename = 'inputs/input_data.dat'

mylines = []
elements = []
with open(filename, 'r') as myfile:
    for myline in myfile:
        mylines.append(myline)
    for element in mylines:
        elements.append(element.split())

airfoil = []
for i in range(len(elements[5])):
    if elements[5][i] == '#':
        break
    airfoil.append(elements[5][i])

# MainPlate Inputs
airfoil_mid = airfoil[0]
airfoil_tip = airfoil[1]
spoiler_span = float(elements[6][0])
spoiler_chord = float(elements[7][0])
spoiler_angle = float(elements[8][0])

# Strut Inputs
strut_airfoil_shape = bool(elements[11][0])
strut_lat_location = float(elements[12][0])
strut_height = float(elements[13][0])
strut_chord = float(elements[14][0])
strut_thickness = float(elements[15][0])
strut_sweep = float(elements[16][0])
strut_cant = float(elements[17][0])

# Endplate Inputs
endplate_present = bool(elements[20][0])
endplate_thickness = float(elements[21][0])
endplate_sweep = float(elements[22][0])
endplate_cant = float(elements[23][0])

# Material Inputs
material_density = float(elements[26][0])
youngs_modulus = float(elements[27][0])
yield_strength = float(elements[28][0])
shear_modulus = float(elements[29][0])
shear_strength = float(elements[30][0])
