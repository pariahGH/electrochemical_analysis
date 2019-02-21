from scipy.optimize import curve_fit
import numpy as np

def generateFuelCellCurveFromPoints(points, scale):	
	[equation, popt] = gencurve(points)
	
	t_zero = 0
	t_one = scale
	yield popt
	yield equation(0) #we give the t = 0 value first
	while True:
		result = sum([equation(t) for t in range(t_zero, t_one)])
		t_zero += scale
		t_one += scale
		yield result
		
def func(t, V, W, k):
    y = V - ((V - W) * (np.exp(-k * t)))
    return y
		
def gencurve(points):
	[times, outputs] = [list(t) for t in zip(*l)]	
	popt,_ = curve_fit(func, times, outputs)
	
	def curve(t):
		return func(t, popt[0], popt[1], popt[2])
	
	return [curve, popt]

def getPoints(grid):
	data = []
	for i in range(0, grid.GetNumbercols()):
		time = grid.GetCellValue(0, i)
		output = grid.GetCellValue(1,i)
		data.append((time, output))
	return data