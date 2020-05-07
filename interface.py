from Geometry_calculator import geometry_calculator
from AVL_main import avl_main
from my_spoiler import geometry

import os

print("SPOILER DESIGN APPLICATION")
print("PLEASE SELECT ONE OF THE FOLLOWING:")
print("")
print("1. Calculate downforce for a given spoiler")
print("2. Calculate spoiler geometry for a given downforce")
print("")

var_input = int(input("Input: "))

os.system('cls')

print("Please provide the name of the input file")
print("")
file_input = str(input("Input: "))

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
        geometry()

    elif mode_input == 2:
        avl_main()

    elif mode_input == 3:
        print("Not available yet")

elif var_input == 2:
    geometry_calculator()

dummy = input("Press any key to continue")