# Misc Lab Programs

The programs in these repo were written for usage in analysis of electrochemical analysis data, specifically processing cyclic voltammetry data as well as discrete chronoamperometric data, for the
characterization of electrodes. 

## Screen Recorder

This script is used for recording experimental data. The program that talks to the equipment displays a window on the screen during
run time that show real time results. The data of interest is recorded from this window at intervals. This data must be written down
by hand, as the end output of the program is not easy to search through, especially with higher sampling rates. This program takes a 
screen shot of the displayed data as well as tracking steps in the experiment, then OCRs the screen shots with Tesseract to output a nicely formatted 
CSV which can be consumed by the data analysis program, as well as being easier to read manually - this method also allows for the tracking
of other data that cannot necessarily be obtained from the equipment software. 

## Data Analysis

The data analysis script consumes the output of the screen recorder - it can also consume cyclic voltammetry data from the controller software,
as the timeframe for that data is fixed. It produces graphs using matplotlib, and can output paired graphs (ie both of the electrodes in dual configuration cell)
as well as customized averages (with +- SEM). 

## Fuel Cell Power Modeling

This program is intended to assist with identifying minimum viable fuel cell parameters for a system with a known average load and battery capacity. This is because it is 
not strictly necessary to power some systems solely with a fuel cell. In many cases, including pacemakers and sensors, the device only has to have power for a predetermined minimum 
amount of time. A battery and fuel cell can be used in combination - the fuel cell only has to be good enough to extend the battery life past the minimum lifetime. This program is intended
help with evaluating fuel cells for this application.

It takes as args the average load (mW), the starting energy storage (mJ - currently assumed to be max capacity as well), and three points on the fuel cell decay curve, spitting out a graph
showing the battery charge and fuel cell output over time, and a table displaying some key metrics.

This is currently in proof of concept stage and requires more refining to be actually useful - I intend to replace the three point system with an actual user defined table,
add more system options, and add generation of minimum viable fuel cell decay curves given system constraints. 

## Final Thoughts

This is all still in development as I figure out better ways of processing the data or additional features that would be helpful. 
It's pretty specific to my use case, but if there is anyone out there that has similar issues with electrochemical analysis equipment, reach out!