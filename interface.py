from Geometry_calculator import geometry_calculator
from AVL_main import avl_main
from my_spoiler import geometry
from structural_calculations import structural_analysis
from inputs.read_inputs import read_geometry_inputs, read_flow_inputs, \
                               read_material_inputs

import os

print("SPOILER DESIGN APPLICATION")
print("PLEASE SELECT ONE OF THE FOLLOWING:")
print("")
print("1. Perform calculations for a given spoiler geometry")
print("2. Calculate spoiler geometry for a given downforce")
print("")

var_input = int(input("Input: "))

os.system('cls')

# print("Please provide the name of the geometry input file")
# print("")
# geom_input = str(input("Input: "))
#
# geom_input = 'inputs/' + geom_input
# geom = read_geometry_inputs(geom_input)
#
# print("")
# print("Please provide the name of the flow conditions input file")
# print("")
# cond_input = str(input("Input: "))
#
# cond_input = 'inputs/' + cond_input
# cond = read_flow_inputs(cond_input)
#
# print("")
# print("Please provide the name of the material property input file")
# print("")
# mat_input = str(input("Input: "))
#
# mat_input = 'inputs/' + mat_input
# mat = read_material_inputs(mat_input)

os.system('cls')

if var_input == 1:
    print("Please select one of the following")
    print("")
    print("1. Show geometry")
    print("2. Calculate lift and drag distribution")
    print("3. Calculate structural weight and stiffness")
    print("")
    mode_input = int(input("Input: "))

    os.system('cls')
    if mode_input == 1:
        print("Please provide the name of the geometry input file")
        print("")
        geom_input = str(input("Input: "))

        geom_input = 'inputs/' + geom_input
        geom = read_geometry_inputs(geom_input)

        geometry(geom)

    elif mode_input == 2:
        print("Please provide the name of the geometry input file")
        print("")
        geom_input = str(input("Input: "))

        geom_input = 'inputs/' + geom_input
        geom = read_geometry_inputs(geom_input)

        print("")
        print("Please provide the name of the flow conditions input file")
        print("")
        cond_input = str(input("Input: "))

        cond_input = 'inputs/' + cond_input
        cond = read_flow_inputs(cond_input)

        avl_main(geom, cond)

    elif mode_input == 3:
        print("Please provide the name of the geometry input file")
        print("")
        geom_input = str(input("Input: "))

        geom_input = 'inputs/' + geom_input
        geom = read_geometry_inputs(geom_input)

        print("")
        print("Please provide the name of the flow conditions input file")
        print("")
        cond_input = str(input("Input: "))

        cond_input = 'inputs/' + cond_input
        cond = read_flow_inputs(cond_input)

        print("")
        print("Please provide the name of the material property input file")
        print("")
        mat_input = str(input("Input: "))

        mat_input = 'inputs/' + mat_input
        mat = read_material_inputs(mat_input)

        print("Please enter an initial skin thickness in meters")
        print("")
        initial_thickness = float(input("Initial skin thickness: "))
        structural_analysis(geom, cond, mat,
                            initial_skin_thickness=initial_thickness)

elif var_input == 2:
    print("Please provide the name of the geometry input file")
    print("")
    geom_input = str(input("Input: "))

    geom_input = 'inputs/' + geom_input
    geom = read_geometry_inputs(geom_input)

    print("")
    print("Please provide the name of the flow conditions input file")
    print("")
    cond_input = str(input("Input: "))

    cond_input = 'inputs/' + cond_input
    cond = read_flow_inputs(cond_input)

    geometry_calculator(geom, cond)

dummy = input("Press any key to continue")