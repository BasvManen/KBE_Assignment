from analysis.spoiler_files import Spoiler
from analysis.AVL_main import AvlAnalysis
from parapy.gui import display
import matplotlib.pyplot as plt

# GEOMETRY CALCULATOR CLASS
# In this file, a geometry is calculated based on the desired downforce.
# The geometry can be optimized for spoiler angle, span and chord


def geometry_calculator(geom, cond):
    # Firstly, the variable parameter is chosen
    print("PLEASE SELECT THE VARIABLE PARAMETER")
    print("1: Spoiler Angle")
    print("2: Spoiler Span")
    print("3: Spoiler Chord")
    print("4: Car Velocity")
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
        var = 0.7
    elif var_input == 3:  # Starting value for spoiler chord
        var = 0.2
    elif var_input == 4:  # Starting value for car velocity
        var = 20

    # Define history arrays to show progress
    history_x = []
    history_y = []

    # Start the iteration loop, it will stop when the desired downforce is reached
    while current < target:

        # Increase the variable each iteration
        if var_input == 1:  # Step increase for spoiler angle
            var += 1
        elif var_input == 2:  # Step increase for spoiler span
            var += 0.1
        elif var_input == 3:  # Step increase for spoiler chord
            var += 0.05
        elif var_input == 4:  # Step increase for car velocity
            var += 1

        # Create the spoiler based on the geometry inputs
        spoiler = Spoiler(label="Spoiler",
                          mid_airfoil=geom[0],
                          tip_airfoil=geom[1],
                          spoiler_span=var if var_input == 2
                          else geom[2] / 1000.,
                          spoiler_chord=var if var_input == 3 else
                          geom[3] / 1000.,
                          spoiler_angle=var if var_input == 1 else geom[4],
                          strut_airfoil_shape=geom[5],
                          strut_lat_location=geom[6],
                          strut_height=geom[7] / 1000.,
                          strut_chord_fraction=geom[8],
                          strut_thickness=geom[9] / 1000.,
                          strut_sweep=geom[10],
                          strut_cant=geom[11],
                          endplate_present=False,
                          endplate_thickness=geom[13] / 1000.,
                          endplate_sweep=geom[14],
                          endplate_cant=geom[15],
                          do_avl=True)

        # Define case used in AVL
        case = [('AoA input', {'alpha': 0})]

        # Start the AVL analysis, which will give the total downforce
        analysis = AvlAnalysis(spoiler=spoiler,
                               case_settings=case,
                               velocity=var if var_input == 4 else cond[0],
                               density=cond[2])

        # Extract total downforce from AVL and set as the current downforce
        current = analysis.total_force

        # Store iteration values in history array
        history_x.append(var)
        history_y.append(current)

        # Print the progress in the Python console
        print("Current parameter value:", var)
        print("Current downforce:", round(current, 0), "Newtons")
        print("")

    # Once the iteration is finished, show convergence history
    plt.plot(history_x, history_y)
    plt.title("Downforce convergence history")
    plt.xlabel("Variable parameter value")
    plt.ylabel("Downforce level [N]")
    plt.show()

    # Once the iteration is finished, display the final geometry and
    # AVL analysis of the final geometry
    display(analysis)
