Please mention that for now the project is in the state of Alpha (or even pre-Alpha), so some features could be clunky or not intuitive. Also, the program is not crash-proof yet and in some cases cannot provide fully correct results of the simulation (but usually results end up close to results of similar programs).

If you want to try out the program now, you should download the repository, install the requirements, and launch main.py, which is located in the node_master folder. For test grain, you can use the provided ExampleMotor.obj file. For resolution in meshing, I recommend using a value of 0.0005, and for the timestep value of the simulation, 0.1-0.03.

If you want to import your own CAD design, mention that for now it is only accepted. The obj format and design should consist of two parts: casing and grain; otherwise, the program will have difficulties importing geometry.
