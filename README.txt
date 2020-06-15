############ KBE APP TO SUPPORT DESIGN OF AUTOMOTIVE REAR SPOILERS ############

This application is developed for the course AE4204 Knowledge Based
Engineering. The app is designed to help with automating the design of rear car
spoilers, especially for high-performance racing divisions.

#################################### USAGE ####################################

Run the Main.py file to start the KBE application. An interface will pop up, in
which a spoiler is created using the input files as defined in the "inputs"
folder. Based on the inputs, the following analyses can be performed:

1. Output of a geometry STEP file, to be used in CAD software.
2. 3D aerodynamic analysis of the given geometry to obtain the downforce and
   drag distributions and the total forces.
3. 2D (viscous) aerodynamic analysis of a given section of the geometry to
   investigate the effect of spoiler angle on total lift force.
4. Structural analysis of the given geometry to obtain stresses, moments and
   deflections along the span of the spoiler.

Furthermore, the application is also able to calculate certain aspects of the
geometry, given a (desired) downforce. This is done with an iterative process.

1. The application can calculate the spoiler angle, spoiler span or spoiler
   chord required to achieve a desired downforce.
2. The application can calculate the required skin thickness to avoid
   structural failure, given a geometry and material.

#################################### INPUT ####################################

Three .dat files need to be provided to explore all capabilities of the spoiler
design application. These input files are defined as follows:

- Geometry Input
    1.  Section airfoils of the main plate
    2.  Span of the main plate
    3.  Chord of the main plate
    4.  Angle of the main plate (positive defined upwards)
    5.  Amount of main plates
    6.  Amount of struts
    7.  Strut shape (flat plate or airfoil shape)
    8.  Placement of the struts w.r.t. the main plate
    9.  Height of the struts
    10. Chord of the struts (as a fraction of the main plate)
    11. Thickness of the struts
    12. Sweepback angle of the struts
    13. Cant angle of the struts
    14. Definition whether endplates are present or not
    15. Thickness of the endplates
    16. Sweepback angle of the endplates
    17. Cant angle of the endplates
    18. Length of the car
    19. Width of the car
    20. (Maximum) height of the car
    21. Car middle-to-back height ratio

- Flow Conditions Input
    1. Car design 'cruise' speed
    2. Car design top speed
    3. Free flow air density

- Material Properties Input
    1. Material density
    2. Material Young's modulus
    3. Material tensile yield strength
    4. Material shear strength
    5. Material Poisson ratio

################################### OUTPUTS ###################################
The following outputs can be obtained from the application:

1. .STEP file for CAD software
2. Spoiler downforce distribution and total downforce
3. Spoiler drag distribution and total drag force
4. Sectional spoiler angle vs. downforce coefficient plot
5. Spoiler skin thickness and spoiler weight
5. Normal stress along the spoiler span
6. Shear stress along the spoiler span
7. Deflection in x and z direction along the spoiler span
8. Bending moment along the spoiler span