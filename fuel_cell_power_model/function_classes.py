import wx
import wx.grid
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import util
import datetime
from locale import setlocale, LC_NUMERIC, atof
setlocale(LC_NUMERIC, "") 
class UseCurveSettings():
	def __init__(self,rootPanel):
		rootSizer = wx.BoxSizer(wx.VERTICAL)
		self.rootPanel = rootPanel
		
		self.powerConsumptionRateEntry = wx.TextCtrl(self.rootPanel)
		self.batteryCapacityEntry = wx.TextCtrl(self.rootPanel)
		
		powerConsumptionRateLabel = wx.StaticText(self.rootPanel, wx.ID_ANY, "Power consumption rate (mW)")
		batteryCapacityLabel = wx.StaticText(self.rootPanel, wx.ID_ANY, "Initial battery capacity (mJ)")
		
		timeLabel = wx.StaticText(self.rootPanel, wx.ID_ANY, "Time")
		outputLabel = wx.StaticText(self.rootPanel, wx.ID_ANY, "Output (mW)")
		
		timeOutputContainer = wx.BoxSizer(wx.HORIZONTAL)
		labelContainer = wx.BoxSizer(wx.VERTICAL)
		labelContainer.AddMany([(timeLabel,0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL), (outputLabel,0, wx.ALIGN_BOTTOM)])
		
		addPairButton = wx.Button(self.rootPanel, wx.ID_ANY, "Add Time/Output Pair")
		self.timeOutputGrid = wx.grid.Grid(self.rootPanel, wx.ID_ANY)
		self.timeOutputGrid.CreateGrid(2,12)
		self.timeOutputGrid.EnableGridLines(True)
		self.timeOutputGrid.HideColLabels()
		self.timeOutputGrid.HideRowLabels()
		timeOutputContainer.AddMany([(labelContainer,0,wx.EXPAND), (self.timeOutputGrid,0,wx.EXPAND)])

		self.fuelCellCurveTimescaleSelector = wx.ComboBox(self.rootPanel,choices=["Hours", "Days"])
		fuelCellCurveTimescaleLabel = wx.StaticText(self.rootPanel, wx.ID_ANY, "Timescale of fuel cell readings")
		
		topSizer = wx.GridSizer(2, 4, 5, 5)
		topSizer.AddMany([
			powerConsumptionRateLabel, batteryCapacityLabel, fuelCellCurveTimescaleLabel, addPairButton,
			self.powerConsumptionRateEntry,self.batteryCapacityEntry, self.fuelCellCurveTimescaleSelector
		])
		
		rootSizer.AddMany([(topSizer,1,wx.EXPAND), (timeOutputContainer,1,wx.EXPAND)])
		self.window = rootSizer
		self.rootPanel.Bind(wx.EVT_BUTTON, self.addPair, addPairButton)
		
	def clear(self,evt):
		self.powerConsumptionRateEntry.SetValue("")
		self.batteryCapacityEntry.SetValue("")
		self.initialFuelCellOutputEntry.SetValue("")
		self.plusTenOutputEntry.SetValue("")
		self.plusHundredOutputEntry.SetValue("")
		
	def addPair(self,evt):
		self.timeOutputGrid.AppendCols(1)
		self.rootPanel.Layout()
		
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
				consumptionRate = atof(self.powerConsumptionRateEntry.GetValue())
				batteryCharge = atof(self.batteryCapacityEntry.GetValue())
				scale = self.fuelCellCurveTimescaleSelector.GetStringSelection()
			except Exception as e:
				print("one or more inputs is invalid!")
				print(e)
			else:			
				scales = {"Hours": 60*60, "Days":60*60*24}
				timeFactor = scales[scale]
				#ticks in seconds
				outputGenerator = util.generateFuelCellCurveFromPoints(points, timeFactor)
				self.popt = next(outputGenerator)
				originalOutput = next(outputGenerator)
				chargeVsTime = [batteryCharge]
				chargeVsTimeNoCell = [batteryCharge]
				outputVsTime = [originalOutput]
				self.timeToZeroOutput = 0
				self.timeToZeroChargeNoCell = 0
				batteryChargeWithoutCell = batteryCharge
				n = 1
				while batteryCharge >= 0:
				#TODO: there has to be some way to make this faster.
					output = next(outputGenerator)
					if output >= 0.01 * originalOutput:
						self.timeToZeroOutput+=1
					batteryCharge = min(batteryCharge + output - consumptionRate, batteryCharge)
					batteryChargeWithoutCell = batteryChargeWithoutCell - consumptionRate
					if self.timeToZeroChargeNoCell == 0 and batteryChargeWithoutCell <=0:
						self.timeToZeroChargeNoCell = len(chargeVsTimeNoCell)
					#only mark at hour or day endpoints
					if n == timeFactor:
						chargeVsTime.append(max(batteryCharge,0))
						chargeVsTimeNoCell.append(max(batteryChargeWithoutCell,0))
						outputVsTime.append(max(output,0))
						n = 0
					n+=1
					
				self.timeToEmptyBattery = len(chargeVsTime)
				xaxis = range(0, len(chargeVsTime), 1)
							
				fig, host = plt.subplots()
				fig.subplots_adjust(right=0.75)
				par1 = host.twinx()

				host.set_xlabel("Time")
				host.set_ylabel("Fuel Cell Output")
				par1.set_ylabel("Battery Charge")
				p1, = host.plot(xaxis, outputVsTime, color="r", label="Fuel Cell Output")
				p2, = par1.plot(xaxis, chargeVsTime, label="Battery Charge")
				p3, = par1.plot(xaxis, chargeVsTimeNoCell, label="Battery Charge - No Cell")

				host.legend()
				par1.legend()
				host.yaxis.label.set_color(p1.get_color())
				par1.yaxis.label.set_color(p2.get_color())

				plt.draw()
				
				#save temp copy of image, to be loaded into graph
				date = str(datetime.datetime.now()).split(" ")
				self.filename = date[0] + date[1].split(".")[0].replace(":","_")
				plt.savefig(self.filename+".jpg",bbox_inches='tight')
				
				graph = wx.StaticBitmap(panel, wx.ID_ANY, wx.Bitmap(self.filename+".jpg"))
				graph.Show()
				resultsSizer = wx.GridSizer(2,3,5)
				resultsSizer.AddMany([wx.StaticText(panel, wx.ID_ANY, "Time to zero charge - no fuel cell"), 
					wx.StaticText(panel, wx.ID_ANY, str(self.timeToZeroChargeNoCell)), 
					wx.StaticText(panel, wx.ID_ANY, "Time to zero charge - with fuel cell"), 
					wx.StaticText(panel, wx.ID_ANY, str(self.timeToEmptyBattery)), 
					wx.StaticText(panel, wx.ID_ANY, "Time to zero fuel cell output"), 
					wx.StaticText(panel, wx.ID_ANY, str(self.timeToZeroOutput))
				])
				
				self.results = {"graph":graph,"table":resultsSizer}
				return self.results
				
	def exportResults(self):
		#we already have the image saved, we just need to export the data and the popts with equation format
		data = {
			"a": self.popts[0],
			"b": self.popts[1],
			"c": self.popts[2],
			"form": "a - ((a-b) * e^(-c*t)",
			"timeToEmptyBattery":self.timeToEmptyBattery,
			"timeToEmptyBatteryNoCell":self.timeToEmptyBatteryNoCell,
			"timeToEmptyFuelCell":self.timeToZeroOutput,
		}
		with open(self.filename+'.json','w') as f:
			f.write(json.dumps(data))
	