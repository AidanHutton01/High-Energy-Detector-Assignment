# High-Energy-Detector-Assignment

This repository contains all my code and files used for the assignmnet. SpecPlot.py will work with one data file to make one plot. Calibrate.py will take a config file (see Example_config.txt) and produce a new data file which can then be fed into Resolution.py, Efficiency.py and OffAxis.py. The config files and the files output by Calibrate.py are a specific format, if changed significantly they will not be read properly by the scripts.

Edit:
To explain in more detail, the pipeline for processing data works like this:

config_file----->Calibrate.py----->calibration_output(graph + file)

calibration_output(file only)----->Resolution.py----->resolution_output(graph + file)

calibration_output(file)----->Efficiency.py----->efficiency_output(just a graph)

For off-axis analysis a new config sould be made with different angels as seperate sources, this file is run through Resolution.py before OffAngle.py

config_file(angle measurments)----->Calibrate.py----->calibration_output(graph + file)

calibration_output(file)----->OffAngle.py----->off_angle_output(just a graph)

All config and output fiels are already in this repository, when running the code you can either clear them or make new files. However the config files need to be in a specific format
