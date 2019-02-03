import wx
import wx.grid
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import util

#create a class for each of the possible functions - should implement clear fucntion, get params function
#these should also handle calling the generating functions, and should return data to be displayed
class GenerateCurveSettings():
	def __init__(self, panel):
		rootPanel = wx.Panel(panel)
		rootSizer = wx.BoxSizer(wx.HORIZONTAL)
		
	def clear(self, evt):
		print("cleared")
		
	def generateResults():
		return window
		
	def getSettings(self):
		return self.window
		
class UseCurveSettings():
	def __init__(self,rootPanel):
		rootSizer = wx.GridSizer(2, 6, 5, 5)
		
		self.powerConsumptionRateEntry = wx.TextCtrl(rootPanel)
		self.batteryCapacityEntry = wx.TextCtrl(rootPanel)
		self.initialFuelCellOutputEntry = wx.TextCtrl(rootPanel)
		self.plusTenOutputEntry = wx.TextCtrl(rootPanel)
		self.plusHundredOutputEntry = wx.TextCtrl(rootPanel)
		
		powerConsumptionRateLabel = wx.StaticText(rootPanel, wx.ID_ANY, "Power consumption rate (mW)")
		batteryCapacityLabel = wx.StaticText(rootPanel, wx.ID_ANY, "Initial battery capacity (mJ)")
		initialFuelCellOutputLabel = wx.StaticText(rootPanel, wx.ID_ANY, "Fuel cell output t=0 (mW)")
		plusTenOutputLabel = wx.StaticText(rootPanel, wx.ID_ANY, "Fuel cell output t=10")
		plusHundredOutputLabel = wx.StaticText(rootPanel, wx.ID_ANY, "Fuel cell output t=100")
		
		'''
		TODO: change this to take one initial value and 9 additional values with user specified times, user still selects scale
		'''
		
		self.fuelCellCurveTimescaleSelector = wx.ComboBox(rootPanel,choices=["Hours", "Days"])
		fuelCellCurveTimescaleLabel = wx.StaticText(rootPanel, wx.ID_ANY, "Timescale of fuel cell readings")
		
		rootSizer.AddMany([powerConsumptionRateLabel, batteryCapacityLabel, initialFuelCellOutputLabel,
		plusTenOutputLabel, plusHundredOutputLabel,fuelCellCurveTimescaleLabel,
			self.powerConsumptionRateEntry,
			self.batteryCapacityEntry,
			self.initialFuelCellOutputEntry,
			self.plusTenOutputEntry,
			self.plusHundredOutputEntry,
			self.fuelCellCurveTimescaleSelector
		])
		self.window = rootSizer
		
	def clear(self, evt):
		self.powerConsumptionRateEntry.SetValue("")
		self.batteryCapacityEntry.SetValue("")
		self.initialFuelCellOutputEntry.SetValue("")
		self.plusTenOutputEntry.SetValue("")
		self.plusHundredOutputEntry.SetValue("")
		
	def getSettings(self):
		return self.window
		
	def generateResults(self, panel):
		try:
			consumptionRate = float(self.powerConsumptionRateEntry.GetValue())
			batteryCharge = float(self.batteryCapacityEntry.GetValue())
			initialFuelCellOutput = float(self.initialFuelCellOutputEntry.GetValue())
			plusTenOutput = float(self.plusTenOutputEntry.GetValue())
			plusHundredOutput = float(self.plusHundredOutputEntry.GetValue())
			scale = self.fuelCellCurveTimescaleSelector.GetStringSelection()
		except Exception as e:
			print("one or more inputs is invalid!")
			print(e)
		else:
			#TODO: rework this whole section for memory efficiency
			#instead of calculating raw seconds, use summing and integrals to calculate in hours and days
			outputGenerator = util.generateFuelCellCurveFromPoints(initialFuelCellOutput, plusTenOutput, plusHundredOutput, scale)
			
			output = next(outputGenerator)
			chargeVsTime = [batteryCharge]
			outputVsTime = [output]
			timeToZeroOutput = 0
			#ticks in seconds
			while batteryCharge >= 0:
				output = next(outputGenerator)
				if output >= 0.1:
					timeToZeroOutput+=1
				batteryCharge = min(batteryCharge + output - consumptionRate, batteryCharge)
				chargeVsTime.append(batteryCharge)
				outputVsTime.append(output)
				
			xaxis = range(0, len(chargeVsTime))
						
			fig, host = plt.subplots()
			fig.subplots_adjust(right=0.75)
			par1 = host.twinx()

			host.set_xlabel("Time")
			host.set_ylabel("Fuel Cell Output")
			par1.set_ylabel("Battery Charge")

			#convert our x axis to minutes if in hours, hours if in days - fix this later
			sampleTime = 60
			if scale == "Days":
				samepleTime = sampleTime * 60
			index = 0
			sampledCharge = []
			sampledOutput = []
			sampledTime = []
			while index <= len(chargeVsTime) - 1 :
				sampledCharge.append(chargeVsTime[index])
				sampledOutput.append(outputVsTime[index])
				sampledTime.append(index/sampleTime)
				index += sampleTime
				
			if index != len(chargeVsTime) -1 :
				sampledCharge.append(chargeVsTime[-1])
				sampledOutput.append(outputVsTime[-1])
				sampledTime.append(xaxis[-1]/sampleTime)
				
			p1, = host.plot(sampledTime, sampledOutput, color="r", label="Fuel Cell Output")
			p2, = par1.plot(sampledTime, sampledCharge, label="Battery Charge")

			host.legend()
			
			host.yaxis.label.set_color(p1.get_color())
			par1.yaxis.label.set_color(p2.get_color())

			plt.draw()
			
			#save temp copy of image, to be loaded into graph
			plt.savefig("temp.jpg",bbox_inches='tight')
			
			graph = wx.StaticBitmap(panel, wx.ID_ANY, wx.Bitmap("temp.jpg"))
			graph.Show()
			grid = wx.grid.Grid(panel, -1)
			grid.CreateGrid(2, 2)
			grid.SetCellValue(0,0, f'Time to 0 charge, ${scale}')
			grid.SetCellValue(0,1, str(len(chargeVsTime)/(60*60*24)))
			grid.SetCellValue(1,0, f'Time to 0 fuel cell output, ${scale}')
			grid.SetCellValue(0,1, str(timeToZeroOutput/(60*60*24)))
			grid.Show()
			return {"graph":graph,"table":grid}