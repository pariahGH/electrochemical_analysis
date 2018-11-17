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



This is all still in development as I figure out better ways of processing the data or additional features that would be helpful. 
It's pretty specific to my use case, but if there is anyone out there that has similar issues with electrochemical analysis equipment, reach out!