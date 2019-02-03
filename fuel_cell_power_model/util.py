# utilfity functions for fuel cell modeling
from scipy.optimize import curve_fit
import numpy as np
scales = {"Hours": 60*60, "Days":60*60*24}

def generateFuelCellCurveFromPoints(initialFuelCellOutput, plusTenOutput, plusHundredOutput, scale):
	#use scale to convert t=10 and t=100 into seconds
	timeInitial = 0
	timePlusTen = 10 * scales[scale]
	timePlusHundred = 10 * timePlusTen
	
	#create a generator that will yield the curve
	
	equation = gencurve(initialFuelCellOutput, plusTenOutput, plusHundredOutput, timePlusTen, timePlusHundred)
	
	t = 0
	
	while True:
		yield equation(t)
		t+=1
		
def func(t, V, W, k):
    y = V  - ((V - W) * (1 - np.exp(-k * t)) / k)
    return y
		
def gencurve(initialFuelCellOutput, plusTenOutput, plusHundredOutput, timePlusTen, timePlusHundred):
	t_one = 0
	t_two = timePlusTen
	t_three = timePlusHundred
	
	y_one = initialFuelCellOutput
	y_two = plusTenOutput
	y_three = plusHundredOutput
		
	popt,_ = curve_fit(func, [t_one, t_two, t_three],[y_one, y_two, y_three])
	
	def curve(t):
		return func(t, popt[0], popt[1], popt[2])
	
	return curve
	