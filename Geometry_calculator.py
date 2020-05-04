from spoiler_files import Spoiler
from AVL_main import AvlAnalysis
from parapy.gui import display

input_target = float(input("Target Downforce: "))
print("-----------------------------------------------")

current = 0
target = input_target

var = 0

while current < target:
    var += 1
    spoiler = Spoiler(label="Spoiler",
                      mid_airfoil='6412',
                      tip_airfoil='6408',
                      spoiler_span=2.5,
                      spoiler_chord=0.8,
                      spoiler_angle=var,
                      strut_airfoil_shape=True,
                      strut_lat_location=0.8,
                      strut_height=0.25,
                      strut_chord=0.4,
                      strut_thickness=0.04,
                      strut_sweep=15.,
                      strut_cant=0.,
                      endplate_present=False,
                      endplate_thickness=0.01,
                      endplate_sweep=15.,
                      endplate_cant=0.)

    case = ['fixed aoa', {'alpha': 0}]

    analysis = AvlAnalysis(spoiler=spoiler,
                           case_settings=case,
                           velocity=25)

    current = analysis.total_force

    print("Current angle:", var, "degrees")
    print("Current downforce:", round(current, 0), "Newtons")
    print("")

display(analysis)
