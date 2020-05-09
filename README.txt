
# KBE app to support design of automotive rear spoilers

This application is developed for the course AE4204 Knowledge Based Engineering. The app
is designed to help with automating the design of rear car spoilers, especially for 
high-performance racing divisions. 


## Usage 

When running the interface of the application, a menu will pop up in which the user has to 
make a choice has to be between analysis approaches:

	1. Perform calculations for a given spoiler geometry
	2. Calculate spoiler geometry for a given downforce

When option 1. 'Perform calculations for a given spoiler geometry' is chosen, the user can 
choose between the following 4 analysis modes:

	1. Show geometry
	2. Calculate lift and drag distribution
	3. Calculate spoiler angle vs downforce for a given section
	4. Perform structural analysis and calculate weight

In each of these modes, the user has to specify the inputs for the geometry of the spoiler. 
For mode 2, 3 and 4, the user also has to specify the flow conditions of the spoiler. 
For mode 4, the properties of the used material have to be specified as well.
In order to specify these inputs, the interface will ask for a .dat file from the 'inputs'
folder. The user can simply type the file_name + .extension of the file, for instance as:

	input_properties.dat

Mode 1 will directly send the user to the ParaPy GUI where the whole spoiler geometry can 
be visualised and interactively altered. 
Mode 2 will perform some aerodynamic calculations for the lift and drag force of the spoiler
geometry. These calculations are from both AVL and emperical methods. It will subsequently
send the user to the ParaPy GUI where the lift and drag distributions can be evaluated.
Mode 3 will use the user specified section to do a viscous analysis using XFOIL. The 
application will send the user to the ParaPy GUI where a plot is generated in which the 
section downforce coefficient is plotted against different spoiler angles.
Mode 4 will perform calculations on wheter the geometry can withstand the aerodynamic forces
on the spoiler. It will first ask for an initial skin thickness, and will iteratively 
increase this thickness untill the spoiler does not fail under the aerodynamic forces. Next,
it will output the final total weight and it will send the user to the ParaPy GUI where 
the stresses and deflections of the spoiler geometry can be visualised.


If in the initial menu, option 2. 'Calculate spoiler geometry for a given downforce' is
chosen, again the geometry and flow conditions have to be inputted as explained above. Next,
the geometry iterator will be started, in which the user has to specify one of the 
following parameters to be iterated:

	1. Spoiler angle
	2. Spoiler span
	3. Spoiler chord
	4. Car velocity

The user has to specify a desired target downforce in Newton, which the application will 
consequently try to find by adjusting one of the above mentioned parameters. If the desired
downforce is found, the application will save the geometry for which the desired downforce is
obtained and the ParaPy GUI will be opened. Here, the geometry can be visualized and the lift 
and drag distribution of the optimized spoiler can be plotted.
