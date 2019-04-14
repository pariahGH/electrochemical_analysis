import wx
import util
import function_classes
import time

#TODO: write a test file ffs
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA

class MainWindow(wx.Frame):
	selectedSettings = None
	def __init__(self, *args, **kw):
		super(MainWindow,self).__init__(*args, **kw, size=(1000,1000))
		
		self.rootPanel = wx.Panel(self)
		rootSizer = wx.BoxSizer(wx.VERTICAL)
		generateButton = wx.Button(self.rootPanel, wx.ID_ANY, "Process")
		self.exportResultsButton = wx.Button(self.rootPanel, wx.ID_ANY, "Export Results")
		self.exportResultsButton.Enable(False)
		clearButton = wx.Button(self.rootPanel, wx.ID_ANY, "Clear")
		
		self.settingsSizer = wx.BoxSizer(wx.HORIZONTAL)
		controlsSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.graphSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.tableSizer = wx.BoxSizer(wx.HORIZONTAL)
		#over time, should be able to add arbitrary types of generated extrapolations
		#that can easily be swapped
		self.selectedSettings = function_classes.UseCurveSettings(self.rootPanel)
		controlsSizer.AddMany([generateButton, clearButton, self.exportResultsButton])
		
		rootSizer.AddMany([(controlsSizer,0,wx.ALIGN_CENTER_HORIZONTAL), (self.selectedSettings.getSettings(),0,wx.ALIGN_CENTER_HORIZONTAL), 
			(self.graphSizer,1,wx.ALIGN_CENTER_HORIZONTAL), (self.tableSizer,1,wx.ALIGN_CENTER_HORIZONTAL)])
		
		self.rootPanel.SetSizerAndFit(rootSizer)
		self.Bind(wx.EVT_BUTTON, self.onClearClicked, clearButton)
		self.Bind(wx.EVT_BUTTON, self.onGenerateClicked, generateButton)
		self.Bind(wx.EVT_BUTTON, self.onExportResultsClicked, self.exportResultsButton)
		
	def onClearClicked(self, evt):
		self.selectedSettings.clear(evt)
			
	def onGenerateClicked(self, evt):
		self.graphSizer.Clear()
		self.tableSizer.Clear()
		self.exportResultsButton.Enable(True)
		if self.selectedSettings != None:
			result = self.selectedSettings.generateResults(self.rootPanel)
			if result is not None:
				self.graphSizer.Add(result["graph"])
				self.graphSizer.Layout()
				self.tableSizer.Add(result["table"])
				self.tableSizer.Layout()
				self.rootPanel.Layout()
				
	def onExportResultsClicked(self, evt):
		if self.selectedSettings != None:
			self.selectedSettings.exportResults()
		
app = wx.App()
frame = MainWindow(None, title="Fuel cell modeling")
frame.Show()
app.MainLoop()