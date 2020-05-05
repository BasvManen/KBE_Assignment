from spoiler_files import Spoiler
from AVL_main import AvlAnalysis
from parapy.gui import display

# GEOMETRY CALCULATOR CLASS
# In this file, a geometry is calculated based on the desired downforce.
# The geometry can be optimized for spoiler angle, span and chord

# Firstly, the variable parameter is chosen
print("PLEASE SELECT THE VARIABLE PARAMETER")
print("1: Spoiler Angle")
print("2: Spoiler Span")
print("3: Spoiler Chord")
var_input = int(input("Input: "))

# User can input a desired downforce in Newtons
input_target = float(input("Target Downforce [N]: "))
print("-----------------------------------------------")

# Starting value for the downforce, current will represent the downforce
# of the current iteration, target represents the target downforce as
# inputted by the user
current = 0
target = input_target

# Starting value of the iteration variable, this depends on which variable
# is iterated
if var_input == 1:  # Starting value for spoiler angle
    var = 0
elif var_input == 2:  # Starting value for spoiler span
    var = 0.5
elif var_input == 3:  # Starting value for spoiler chord
    var = 0.2


# Start the iteration loop, it will stop when the desired downforce is reached
while current < target:

    # Increase the variable each iteration
    if var_input == 1:  # Step increase for spoiler angle
        var += 1
    elif var_input == 2:  # Step increase for spoiler span
        var += 0.05
    elif var_input == 3:  # Step increase for spoiler chord
        var += 0.05

    # Create the spoiler based on the geometry inputs
    spoiler = Spoiler(label="Spoiler",
                      mid_airfoil='6412',
                      tip_airfoil='6408',
                      spoiler_angle=var if var_input == 1 else 10,
                      spoiler_span=var if var_input == 2 else 2.5,
                      spoiler_chord=var if var_input == 3 else 0.8,
                      strut_airfoil_shape=True,
                      strut_lat_location=0.8,
                      strut_height=0.25,
                      strut_chord_fraction=0.5,
                      strut_thickness=0.04,
                      strut_sweep=15.,
                      strut_cant=0.,
                      endplate_present=False,
                      endplate_thickness=0.01,
                      endplate_sweep=15.,
                      endplate_cant=0.)

    # Define case used in AVL
    case = [('AoA input', {'alpha': 0})]

    # Start the AVL analysis, which will give the total downforce
    analysis = AvlAnalysis(spoiler=spoiler,
                           case_settings=case,
                           velocity=25)

    # Extract total downforce from AVL and set as the current downforce
    current = analysis.total_force

    # Print the progress in the Python console
    print("Current parameter value:", var)
    print("Current downforce:", round(current, 0), "Newtons")
    print("")

# Once the iteration is finished, display the final geometry and
# AVL analysis of the final geometry
display(analysis)
