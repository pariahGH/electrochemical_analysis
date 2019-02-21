import wx
import wx.grid
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import util
import datetime

class UseCurveSettings():
	def __init__(self,rootPanel):
		rootSizer = wx.BoxSizer(wx.VERTICAL)
		self.rootPanel = rootPanel
		
		self.powerConsumptionRateEntry = wx.TextCtrl(self.rootPanel)
		self.batteryCapacityEntry = wx.TextCtrl(self.rootPanel)
		self.initialFuelCellOutputEntry = wx.TextCtrl(self.rootPanel)
		self.plusTenOutputEntry = wx.TextCtrl(self.rootPanel)
		self.plusHundredOutputEntry = wx.TextCtrl(self.rootPanel)
		
		powerConsumptionRateLabel = wx.StaticText(self.rootPanel, wx.ID_ANY, "Power consumption rate (mW)")
		batteryCapacityLabel = wx.StaticText(self.rootPanel, wx.ID_ANY, "Initial battery capacity (mJ)")
		
		timeLabel = wx.StaticText(self.rootPanel, wx.ID_ANY, "Time")
		outputLabel = wx.StaticText(self.rootPanel, wx.ID_ANY, "Output")
		self.timeOutputGrid = wx.grid.Grid(self.rootPanel, wx.ID_ANY)
		self.timeOutputGrid.CreateGrid(2,1)
		self.timeOutputGrid.EnableGridLines(True)
		
		timeOutputContainer = wx.BoxSizer(wx.HORIZONTAL)
		labelContainer = wx.BoxSizer(wx.VERTICAL)
		labelContainer.AddMany([timeLabel, outputLabel])
		addPairButton = wx.Button(self.rootPanel, wx.ID_ANY, "Add Time/Output Pair")
		timeGridOutputScroller = wx.ScrolledWindow(self.rootPanel, wx.ID_ANY)
		timeGridOutputScroller.EnableScrolling(True, False)
		timeGridOutputScroller.SetScrollbars(20, 0, 10, 0)
		timeOutputContainer.AddMany([labelContainer, self.timeOutputGrid])

		self.fuelCellCurveTimescaleSelector = wx.ComboBox(self.rootPanel,choices=["Hours", "Days"])
		fuelCellCurveTimescaleLabel = wx.StaticText(self.rootPanel, wx.ID_ANY, "Timescale of fuel cell readings")
		
		topSizer = wx.GridSizer(2, 4, 5, 5)
		topSizer.AddMany([
			powerConsumptionRateLabel, batteryCapacityLabel, fuelCellCurveTimescaleLabel, addPairButton,
			self.powerConsumptionRateEntry,self.batteryCapacityEntry, self.fuelCellCurveTimescaleSelector
		])
		
		rootSizer.AddMany([topSizer, timeOutputContainer])
		self.window = rootSizer
		self.rootPanel.Bind(wx.EVT_BUTTON, self.addPair, addPairButton)
		
	def clear(self, evt):
		self.powerConsumptionRateEntry.SetValue("")
		self.batteryCapacityEntry.SetValue("")
		self.initialFuelCellOutputEntry.SetValue("")
		self.plusTenOutputEntry.SetValue("")
		self.plusHundredOutputEntry.SetValue("")
		
	def addPair(self, evt):
		self.timeOutputGrid.AppendCols(1)
		
	def getSettings(self):
		return self.window
		
	def generateResults(self, panel):
		if self.timeOutputGrid.GetNumberCols() <3:
			dlg = wx.MessageDialog(self.rootPanel, "At least 3 points required for fuel cell output")
			dlg.ShowModal()
			return None
		else:
			try:
				points = util.getPoints(self.timeOutputGrid)
				consumptionRate = float(self.powerConsumptionRateEntry.GetValue())
				batteryCharge = float(self.batteryCapacityEntry.GetValue())
				scale = self.fuelCellCurveTimescaleSelector.GetStringSelection()
			except Exception as e:
				print("one or more inputs is invalid!")
				print(e)
			else:			
				scales = {"Hours": 60*60, "Days":60*60*24}
				timeFactor = scales[scale]
				outputGenerator = util.generateFuelCellCurveFromPoints(points, timeFactor)
				self.popt = next(outputGenerator)
				output = next(outputGenerator)
				chargeVsTime = [batteryCharge]
				outputVsTime = [output]
				self.timeToZeroOutput = 0
				#move this to a util function to keep gui code clean
				while batteryCharge >= 0:
					output = next(outputGenerator)
					if output >= 0.1:
						self.timeToZeroOutput+=1
					batteryCharge = min(batteryCharge + output - (consumptionRate*timeFactor), batteryCharge)
					chargeVsTime.append(batteryCharge)
					outputVsTime.append(output)
				self.timeToEmptyBattery = len(chargeVsTime)
				xaxis = range(0, len(chargeVsTime))
							
				fig, host = plt.subplots()
				fig.subplots_adjust(right=0.75)
				par1 = host.twinx()

				host.set_xlabel("Time")
				host.set_ylabel("Fuel Cell Output")
				par1.set_ylabel("Battery Charge")
					
				p1, = host.plot(xaxis, outputVsTime, color="r", label="Fuel Cell Output")
				p2, = par1.plot(xaxis, chargeVsTime, label="Battery Charge")

				host.legend()
				
				host.yaxis.label.set_color(p1.get_color())
				par1.yaxis.label.set_color(p2.get_color())

				plt.draw()
				
				#save temp copy of image, to be loaded into graph
				date = datetime.datetime.now().split(" ")
				self.filename = date[0] + date[1].split(".")[0].replace(":","_")
				plt.savefig(self.filename+".jpg",bbox_inches='tight')
				
				graph = wx.StaticBitmap(panel, wx.ID_ANY, wx.Bitmap(self.filename+".jpg"))
				graph.Show()
				grid = wx.grid.Grid(panel, -1)
				grid.CreateGrid(2, 2)
				grid.SetCellValue(0,0, f'Time to 0 charge, ${scale}')
				grid.SetCellValue(0,1, str(self.timeToEmptyBattery/(60*60*24)))
				grid.SetCellValue(1,0, f'Time to 0 fuel cell output, ${scale}')
				grid.SetCellValue(0,1, str(self.timeToZeroOutput/(60*60*24)))
				grid.Show()
				self.results = {"graph":graph,"table":grid}
				return self.results
	def exportResults():
		#we already have the image saved, we just need to export the data and the popts with equation format
		data = {
			"a": self.popts[0],
			"b": self.popts[1],
			"c": self.popts[2],
			"form": "a - ((a-b) * e^(-c*t)",
			"timeToEmptyBattery":self.timeToEmptyBattery,
			"timeToEmptyFuelCell":self.timeToZeroOutput
		}
		with open(self.filename+'.json','w') as f:
			f.write(json.dumps(data))
	