from scipy.optimize import curve_fit
import numpy as np
from locale import setlocale, LC_NUMERIC, atof
setlocale(LC_NUMERIC, "") 

def generateFuelCellCurveFromPoints(points, scale):	
	[equation, popt] = gencurve(points)
	
	t = 0
	while True:
		yield equation(t)
		t+=1/scale

#assuming exponential form
def func(t, a, b, c):
	y = a * np.exp(-1 * b * t/c)
	return y
	
def gencurve(points):
	[times, outputs] = [list(t) for t in zip(*points)]

	popt,_ = curve_fit(func, times, outputs)
	
	def curve(t):
		return func(t, *popt)
	
	return [curve, popt]

def getPoints(grid):
	data = []
	for i in range(0, grid.GetNumberCols()):
		time = grid.GetCellValue(0, i)
		output = grid.GetCellValue(1, i)
		if time != "" and output != "":
			data.append((atof(time), atof(output)))
	return data