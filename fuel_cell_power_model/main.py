# display functionality for fuel cell modeling

import wx
import util
import function_classes

class MainWindow(wx.Frame):
	selectedSettings = None
	def __init__(self, *args, **kw):
		super(MainWindow,self).__init__(*args, **kw, size=(1000,1000))
		self.rootPanel = wx.Panel(self)
		rootSizer = wx.BoxSizer(wx.VERTICAL)
		#for selecting whether we are generating from curve or generating list of viable curves
		self.functionSelector = wx.ComboBox(self.rootPanel, choices=["Existing curve", "Generate curves"])
		instructions = wx.StaticText(self.rootPanel, wx.ID_ANY, "Choose a function")
		generateButton = wx.Button(self.rootPanel, wx.ID_ANY, "Process")
		clearButton = wx.Button(self.rootPanel, wx.ID_ANY, "Clear")
		
		self.settingsSizer = wx.BoxSizer(wx.HORIZONTAL)
		controlsSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.graphSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.tableSizer = wx.BoxSizer(wx.HORIZONTAL)
		
		controlsSizer.AddMany([instructions, self.functionSelector, generateButton, clearButton])
		
		rootSizer.AddMany([instructions, controlsSizer, self.settingsSizer, self.graphSizer, self.tableSizer])
		
		self.rootPanel.SetSizerAndFit(rootSizer)
		self.Bind(wx.EVT_COMBOBOX, self.onSelectionChanged, self.functionSelector)
		self.Bind(wx.EVT_BUTTON, self.onClearClicked, clearButton)
		self.Bind(wx.EVT_BUTTON, self.onGenerateClicked, generateButton)
		
	def onSelectionChanged(self, evt):
		selected = self.functionSelector.GetStringSelection()
		if selected == "Existing curve":
			self.selectedSettings = function_classes.UseCurveSettings(self.rootPanel)
		elif selected == "Generate curves":
			self.selectedSettings = function_classes.GenerateCurveSettings(self.rootPanel)
		self.settingsSizer.Clear()
		self.settingsSizer.Add(self.selectedSettings.getSettings())
		self.rootPanel.Layout()
		
	def onClearClicked(self, evt):
		if self.selectedSettings != None:
			self.selectedSettings.clear()
			
	def onGenerateClicked(self, evt):
		self.graphSizer.Clear()
		self.tableSizer.Clear()
		if self.selectedSettings != None:
			result = self.selectedSettings.generateResults(self.rootPanel)
			self.graphSizer.Add(result["graph"])
			self.graphSizer.Layout()
			self.tableSizer.Add(result["table"])
			self.tableSizer.Layout()
			self.rootPanel.Layout()
	
app = wx.App()
frame = MainWindow(None, title="Fuel cell modeling")
frame.Show()
app.MainLoop()