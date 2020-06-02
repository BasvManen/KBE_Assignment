from parapy.core import *
from parapy.geom import *
from parapy.core.validate import *

from analysis.spoiler_files import Spoiler
from analysis.AVL_main import AvlAnalysis
from analysis.structural_calculations import StructuralAnalysis
from numpy import round


class Main(GeomBase):
    # Main Plate Inputs
    spoiler_airfoils = Input()
    spoiler_span = Input(validator=Positive)
    spoiler_chord = Input(validator=Positive)
    spoiler_angle = Input(validator=Range(-60., 60.))
    plate_amount = Input(validator=GreaterThanOrEqualTo(1))

    # Strut Inputs
    strut_amount = Input(2, validator=GreaterThanOrEqualTo(2))
    strut_airfoil_shape = Input(True, validator=OneOf([True, False]))
    strut_lat_location = Input(validator=Range(limit1=0.1, limit2=1.0))
    strut_height = Input(validator=Positive)
    strut_chord_fraction = Input(validator=Range(0.3, 1.0))
    strut_thickness = Input(validator=Positive)
    strut_sweep = Input(validator=Range(-60., 60.))
    strut_cant = Input(validator=Range(-30., 30.))

    # Endplate Inputs
    endplate_present = Input(True, validator=OneOf([True, False]))
    endplate_thickness = Input(validator=And(Positive))
    endplate_sweep = Input(validator=Range(-60., 60.))
    endplate_cant = Input(validator=Range(-60., 60.))

    # Car Inputs
    car_length = Input()
    car_width = Input()
    car_maximum_height = Input()
    car_middle_to_back_ratio = Input()

    # Aerodynamic Inputs
    velocity = Input()
    maximum_velocity = Input()
    density = Input()
    iteration_parameter = Input("angle")
    target_downforce = Input(0.)

    # Structural Inputs
    spoiler_skin_thickness = Input()
    n_ribs = Input()
    youngs_modulus = Input()
    yield_strength = Input()
    shear_strength = Input()
    material_density = Input()
    poisson_ratio = Input()

    @Part
    def geometry(self):
        """ Geometry of the spoiler, as visible in the ParaPy GUI. """
        return Spoiler(spoiler_airfoils=self.spoiler_airfoils,
                       spoiler_span=self.spoiler_span,
                       spoiler_chord=self.spoiler_chord,
                       spoiler_angle=self.spoiler_angle,
                       plate_amount=self.plate_amount,
                       strut_amount=self.strut_amount,
                       strut_airfoil_shape=self.strut_airfoil_shape,
                       strut_lat_location=self.strut_lat_location,
                       strut_height=self.strut_height,
                       strut_chord_fraction=self.strut_chord_fraction,
                       strut_thickness=self.strut_thickness,
                       strut_sweep=self.strut_sweep,
                       strut_cant=self.strut_cant,
                       endplate_present=self.endplate_present,
                       endplate_thickness=self.endplate_thickness,
                       endplate_sweep=self.endplate_sweep,
                       endplate_cant=self.endplate_cant,
                       car_length=self.car_length,
                       car_width=self.car_width,
                       car_maximum_height=self.car_maximum_height,
                       car_middle_to_back_ratio=self.car_middle_to_back_ratio)

    @Attribute
    def avl_case(self):
        case = [('Incoming flow angle', {'alpha':
                                         self.geometry.car_model.avl_angle})]
        return case

    @action(label="Geometry Iterator")
    def geometry_iterator(self):
        """ This action changes the geometry to achieve a certain downforce
        level. As input, the variable parameter and the target downforce is
        given. The iterator increases the parameter until the downforce is
        reached. The geometry is changed automatically. """

        print("-----------------------------------------------")
        print('Geometry iterator: The chosen parameter will be ')
        print('increased until the desired downforce is reached. ')
        print("")
        print("Chosen parameter: " + str(self.iteration_parameter))
        print("Target downforce: " + str(self.target_downforce))
        print("-----------------------------------------------")
        # Obtain the zero measurements and define iteration number
        target = self.target_downforce
        current = self.avl_analysis.total_force
        iteration_n = 0

        # First, check if there are no typo's in the variable name. If there
        # are typo's, cancel the iteration process and return nothing.
        if self.iteration_parameter != "angle" and \
           self.iteration_parameter != "span" and  \
           self.iteration_parameter != "chord" and \
           self.iteration_parameter != "velocity":
            print("Selected parameter cannot be iterated")
            print("")
            print("ITERATION FINISHED")
            print("-----------------------------------------------")
            return None

        # Print the zero measurements on the screen
        print("Iteration #: " + str(iteration_n))
        print("Current downforce: " + str(round(current, 1)) + " [N]")

        # Start the iteration loop
        while current < target:
            iteration_n += 1

            # Increase the parameter
            if self.iteration_parameter == "angle":
                self.spoiler_angle += 1
            elif self.iteration_parameter == "span":
                self.spoiler_span += 50
            elif self.iteration_parameter == "chord":
                self.spoiler_chord += 25
            elif self.iteration_parameter == "velocity":
                self.velocity += 2

            # Calculate the new downforce based on the new geometry
            current = AvlAnalysis(spoiler_input=self.geometry,
                                  case_settings=self.avl_case,
                                  velocity=self.velocity,
                                  density=self.density).total_force

            # Print the iteration and current downforce on screen
            print("Iteration #: " + str(iteration_n))
            print("Current downforce: " + str(round(current, 1)) + " [N]")
        print("")
        print("ITERATION FINISHED")
        print("-----------------------------------------------")

    @Part
    def avl_analysis(self):
        """ AVL Analysis of the given spoiler geometry. """
        return AvlAnalysis(spoiler_input=self.geometry,
                           case_settings=self.avl_case,
                           velocity=self.velocity,
                           density=self.density)

    @Attribute
    def skin_thickness_iterator(self):
        """ This attribute calculates the needed skin thickness and ribs,
        by iterating the skin thickness to overcome all failure modes for
        the spoiler. If a failure mode occurs, the skin thickness is
        increased and calculations are performed again. If it turns out that
        the spoiler only fails due to the lack of ribs, the amount of ribs
        are increased. In the Python Console, a log is printed. """
        
        print("-----------------------------------------------")
        print('Structural iterator: the spoiler skin thickness '
              'will be increased until the spoiler failure modes are '
              'satisfied.')
        print("")

        # initialising iterator
        delta_thickness = 0.001
        failure = True
        skin_thickness = self.spoiler_skin_thickness / 1000.
        number_of_ribs = self.n_ribs

        # enter iteration loop
        while failure:
            print('Current skin thickness = '
                  + str(round(skin_thickness, (len(str(delta_thickness)) - 2)))
                  + ', amount of ribs = ' + str(number_of_ribs))
            structural_analysis = StructuralAnalysis(
                spoiler_airfoils=self.spoiler_airfoils,
                spoiler_span=self.spoiler_span / 1000.,
                spoiler_chord=self.spoiler_chord / 1000.,
                spoiler_angle=self.spoiler_angle,
                spoiler_skin_thickness=skin_thickness,
                n_ribs=number_of_ribs,
                strut_amount=self.strut_amount,
                strut_airfoil_shape=self.strut_airfoil_shape,
                strut_lat_location=self.strut_lat_location,
                strut_height=self.strut_height / 1000.,
                strut_chord_fraction=self.strut_chord_fraction,
                strut_thickness=self.strut_thickness / 1000.,
                strut_sweep=self.strut_sweep,
                strut_cant=self.strut_cant,
                endplate_present=self.endplate_present,
                endplate_thickness=self.endplate_thickness / 1000.,
                endplate_sweep=self.endplate_sweep,
                endplate_cant=self.endplate_cant,
                car_length=self.car_length / 1000,
                car_width=self.car_width / 1000,
                car_maximum_height=self.car_maximum_height / 1000,
                car_middle_to_back_ratio=self.car_middle_to_back_ratio,
                maximum_velocity=self.maximum_velocity,
                air_density=self.density,
                youngs_modulus=self.youngs_modulus * 10 ** 9,
                yield_strength=self.yield_strength,
                shear_strength=self.shear_strength,
                material_density=self.material_density,
                poisson_ratio=self.poisson_ratio)

            failure = structural_analysis.failure[0]
            failure_due_to_ribs = structural_analysis.failure[1]
            failure_due_to_mode = structural_analysis.failure[2]

            failure_text = ['   -Failure due to tensile yielding',
                            '   -Failure due to compressive stress buckling',
                            '   -Failure due to shear yielding',
                            '   -Failure due to shear stress buckling',
                            '   -Failure due to too high bending deflection',
                            '   -Failure due to column buckling']
            for i in range(len(failure_due_to_mode)):
                if failure_due_to_mode[i]:
                    print(failure_text[i])

            if failure_due_to_ribs:
                failure = True
                number_of_ribs += 1
                print('Failure occurred only due to lack of ribs, increasing '
                      'amount of ribs...')
                print("")
            elif failure:
                skin_thickness += delta_thickness
                print('Increasing skin thickness...')
                print("")
            elif not failure:
                print(' -All failure modes satisfied')

        print("")
        print("-----------------------------------------------")
        print('Final skin thickness = '
              + str(round(skin_thickness,
                          (len(str(delta_thickness)) - 2))) + ' m')

        # Additionally, it is checked whether the skin thickness is viable
        # compared to the thickness of the spoiler itself.
        # t_c_mid = float(geom[0][-2:])
        # t_c_tip = float(geom[1][-2:])
        # minimum_t_c_ratio = min(t_c_mid, t_c_tip)
        # geom_thickness = geom[3] / 1000. * minimum_t_c_ratio / 100
        # if skin_thickness > 0.5 * geom_thickness:
        #     msg = "Calculated skin thickness is too large for the " \
        #           "thickness of the airfoil geometry. Define a thicker " \
        #           "airfoil/larger chord or choose a stiffer material. "
        #     header = "WARNING: GEOMETRY NOT POSSIBLE"
        #     warnings.warn(msg)

        print('Final amount of ribs = ' + str(number_of_ribs))
        print('Calculated total weight = ' + str(
            round(structural_analysis.weights[4], 4)) + ' kg')
        print("-----------------------------------------------")

        return skin_thickness, number_of_ribs

    @Part
    def structural_analysis(self):
        """ Structural analysis for the calculated spoiler geometry,
        aerodynamic calculations and material input. Note that the inputs
        are needed in meters instead of millimeters. """
        return StructuralAnalysis(spoiler_airfoils=self.spoiler_airfoils,
                                  spoiler_span=self.spoiler_span / 1000.,
                                  spoiler_chord=self.spoiler_chord / 1000.,
                                  spoiler_angle=self.spoiler_angle,
                                  spoiler_skin_thickness=
                                  self.skin_thickness_iterator[0],
                                  n_ribs=self.skin_thickness_iterator[1],
                                  strut_amount=self.strut_amount,
                                  strut_airfoil_shape=self.strut_airfoil_shape,
                                  strut_lat_location=self.strut_lat_location,
                                  strut_height=self.strut_height / 1000.,
                                  strut_chord_fraction=
                                  self.strut_chord_fraction,
                                  strut_thickness=self.strut_thickness / 1000.,
                                  strut_sweep=self.strut_sweep,
                                  strut_cant=self.strut_cant,
                                  endplate_present=self.endplate_present,
                                  endplate_thickness=
                                  self.endplate_thickness / 1000.,
                                  endplate_sweep=self.endplate_sweep,
                                  endplate_cant=self.endplate_cant,
                                  car_length=self.car_length / 1000,
                                  car_width=self.car_width / 1000,
                                  car_maximum_height=
                                  self.car_maximum_height / 1000,
                                  car_middle_to_back_ratio=
                                  self.car_middle_to_back_ratio,
                                  maximum_velocity=self.maximum_velocity,
                                  air_density=self.density,
                                  youngs_modulus=self.youngs_modulus * 10 ** 9,
                                  yield_strength=self.yield_strength,
                                  shear_strength=self.shear_strength,
                                  material_density=self.material_density,
                                  poisson_ratio=self.poisson_ratio)


if __name__ == '__main__':
    from parapy.gui import display

    # Inputs, this needs to be defined in a separate dat file, so this is
    # temporary.

    spoiler_airfoils = ['test', 'naca6406']
    spoiler_span = 3000
    spoiler_chord = 300
    spoiler_angle = 10
    plate_amount = 2
    strut_amount = 2
    strut_airfoil_shape = True
    strut_lat_location = 0.6
    strut_height = 250
    strut_chord_fraction = 0.6
    strut_thickness = 15
    strut_sweep = 20
    strut_cant = 10
    endplate_present = True
    endplate_thickness = 5
    endplate_sweep = 15
    endplate_cant = 0
    car_length = 4800.
    car_width = 2050.
    car_maximum_height = 1300.
    car_middle_to_back_ratio = 1.4

    velocity = 25
    maximum_velocity = 60
    density = 1.225

    initial_spoiler_skin_thickness = 1
    initial_n_ribs = 1
    youngs_modulus = 69
    yield_strength = 225
    shear_strength = 225
    material_density = 2700
    poisson_ratio = 0.33

    obj = Main(spoiler_airfoils=spoiler_airfoils,
               spoiler_span=spoiler_span,
               spoiler_chord=spoiler_chord,
               spoiler_angle=spoiler_angle,
               plate_amount=plate_amount,
               strut_amount=strut_amount,
               strut_airfoil_shape=strut_airfoil_shape,
               strut_lat_location=strut_lat_location,
               strut_height=strut_height,
               strut_chord_fraction=strut_chord_fraction,
               strut_thickness=strut_thickness,
               strut_sweep=strut_sweep,
               strut_cant=strut_cant,
               endplate_present=endplate_present,
               endplate_thickness=endplate_thickness,
               endplate_sweep=endplate_sweep,
               endplate_cant=endplate_cant,
               velocity=velocity,
               maximum_velocity=maximum_velocity,
               density=density,
               spoiler_skin_thickness=initial_spoiler_skin_thickness,
               n_ribs=initial_n_ribs,
               youngs_modulus=youngs_modulus,
               yield_strength=yield_strength,
               shear_strength=shear_strength,
               material_density=material_density,
               poisson_ratio=poisson_ratio,
               car_length=car_length,
               car_width=car_width,
               car_maximum_height=car_maximum_height,
               car_middle_to_back_ratio=car_middle_to_back_ratio)

    display(obj)
