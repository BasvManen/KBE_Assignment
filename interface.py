from Geometry_calculator import geometry_calculator
from AVL_main import avl_main
from my_spoiler import geometry
from structural_calculations import structural_analysis
from inputs.read_inputs import read_geometry_inputs, read_flow_inputs, \
                               read_material_inputs
from XFOIL_main import xfoil_main

import os

print("SPOILER DESIGN APPLICATION")
print("PLEASE SELECT ONE OF THE FOLLOWING:")
print("")
print("1. Perform calculations for a given spoiler geometry")
print("2. Calculate spoiler geometry for a given downforce")
print("")

var_input = int(input("Input: "))

# os.system('cls')
#
# check = 0
# while check == 0:
#     print("Please provide the name of the geometry input file")
#     print("")
#     geom_input = str(input("Input: "))
#     geom_input = 'inputs/' + geom_input
#
#     if os.path.exists(geom_input):
#         check = 1
#     else:
#         print("Please provide a valid file name")
#         print("")
#
# geom = read_geometry_inputs(geom_input)
#
# check = 0
# while check == 0:
#     print("")
#     print("Please provide the name of the flow conditions input file")
#     print("")
#     cond_input = str(input("Input: "))
#     cond_input = 'inputs/' + cond_input
#
#     if os.path.exists(cond_input):
#         check = 1
#     else:
#         print("Please provide a valid file name")
#
# cond = read_flow_inputs(cond_input)
#
# check = 0
# while check == 0:
#     print("")
#     print("Please provide the name of the material property input file")
#     print("")
#     mat_input = str(input("Input: "))
#     mat_input = 'inputs/' + mat_input
#
#     if os.path.exists(mat_input):
#         check = 1
#     else:
#         print("Please provide a valid file name")
#
# mat = read_material_inputs(mat_input)

if var_input == 1:
    print("Please select one of the following")
    print("")
    print("1. Show geometry")
    print("2. Calculate lift and drag distribution")
    print("3. Calculate spoiler angle vs downforce for a given section")
    print("4. Calculate structural weight and stiffness")
    print("")
    mode_input = int(input("Input: "))

    if mode_input == 1:
        check = 0
        while check == 0:
            print("Please provide the name of the geometry input file")
            print("")
            geom_input = str(input("Input: "))
            geom_input = 'inputs/' + geom_input

            if os.path.exists(geom_input):
                check = 1
            else:
                print("Please provide a valid file name")
                print("")

        geom = read_geometry_inputs(geom_input)

        geometry(geom)

    elif mode_input == 2:
        check = 0
        while check == 0:
            print("Please provide the name of the geometry input file")
            print("")
            geom_input = str(input("Input: "))
            geom_input = 'inputs/' + geom_input

            if os.path.exists(geom_input):
                check = 1
            else:
                print("Please provide a valid file name")
                print("")

        geom = read_geometry_inputs(geom_input)

        check = 0
        while check == 0:
            print("")
            print("Please provide the name of the flow conditions input file")
            print("")
            cond_input = str(input("Input: "))
            cond_input = 'inputs/' + cond_input

            if os.path.exists(cond_input):
                check = 1
            else:
                print("Please provide a valid file name")

        cond = read_flow_inputs(cond_input)

        avl_main(geom, cond)

    elif mode_input == 3:
        check = 0
        while check == 0:
            print("Please provide the name of the geometry input file")
            print("")
            geom_input = str(input("Input: "))
            geom_input = 'inputs/' + geom_input

            if os.path.exists(geom_input):
                check = 1
            else:
                print("Please provide a valid file name")
                print("")

        geom = read_geometry_inputs(geom_input)

        check = 0
        while check == 0:
            print("")
            print("Please provide the name of the flow conditions input file")
            print("")
            cond_input = str(input("Input: "))
            cond_input = 'inputs/' + cond_input

            if os.path.exists(cond_input):
                check = 1
            else:
                print("Please provide a valid file name")

        cond = read_flow_inputs(cond_input)

        print("")
        print("Please choose a fraction of the span from 0 to 1")
        print("")
        frac = float(input("Input: "))

        xfoil_main(frac, geom, cond)

    elif mode_input == 4:
        check = 0
        while check == 0:
            print("Please provide the name of the geometry input file")
            print("")
            geom_input = str(input("Input: "))
            geom_input = 'inputs/' + geom_input

            if os.path.exists(geom_input):
                check = 1
            else:
                print("Please provide a valid file name")
                print("")

        geom = read_geometry_inputs(geom_input)

        check = 0
        while check == 0:
            print("")
            print("Please provide the name of the flow conditions input file")
            print("")
            cond_input = str(input("Input: "))
            cond_input = 'inputs/' + cond_input

            if os.path.exists(cond_input):
                check = 1
            else:
                print("Please provide a valid file name")

        cond = read_flow_inputs(cond_input)

        check = 0
        while check == 0:
            print("")
            print(
                "Please provide the name of the material property input file")
            print("")
            mat_input = str(input("Input: "))
            mat_input = 'inputs/' + mat_input

            if os.path.exists(mat_input):
                check = 1
            else:
                print("Please provide a valid file name")

        mat = read_material_inputs(mat_input)

        print("Please enter an initial skin thickness in meters")
        print("")
        initial_thickness = float(input("Initial skin thickness: "))
        structural_analysis(geom, cond, mat,
                            initial_skin_thickness=initial_thickness)

elif var_input == 2:
    check = 0
    while check == 0:
        print("Please provide the name of the geometry input file")
        print("")
        geom_input = str(input("Input: "))
        geom_input = 'inputs/' + geom_input

        if os.path.exists(geom_input):
            check = 1
        else:
            print("Please provide a valid file name")
            print("")

    geom = read_geometry_inputs(geom_input)

    check = 0
    while check == 0:
        print("")
        print("Please provide the name of the flow conditions input file")
        print("")
        cond_input = str(input("Input: "))
        cond_input = 'inputs/' + cond_input

        if os.path.exists(cond_input):
            check = 1
        else:
            print("Please provide a valid file name")

    cond = read_flow_inputs(cond_input)

    geometry_calculator(geom, cond)

dummy = input("Press any key to continue")