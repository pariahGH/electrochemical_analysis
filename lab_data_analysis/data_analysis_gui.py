#we want to display a folder picker to pick the folder
#we read in all the csvs in the folder, looking for the sequential currents
#we should end up with n arrays of x length

import wx
import functions
import wx.lib.scrolledpanel as scrolled

class MainScreen(wx.Frame):
	def __init__(self, *args, **kw):
		super(MainScreen, self).__init__(*args, **kw, size=(150,150))
		panel = wx.Panel(self)
		sizer = wx.BoxSizer(wx.VERTICAL)
		itButton = wx.Button(panel, label="Amperometric Analysis")
		cvButton = wx.Button(panel, label="CV Analysis")
		sizer.Add(itButton)
		sizer.Add(cvButton)
		panel.SetSizerAndFit(sizer)
		self.Bind(wx.EVT_BUTTON, self.itselected, itButton)
		self.Bind(wx.EVT_BUTTON, self.cvselected, cvButton)
	def itselected(self, event):
		f = FileSelectScreen(wx.Frame(None, wx.ID_ANY))
		f.Show()
		f.set("it")
	def cvselected(self, event):
		f = FileSelectScreen(wx.Frame(None, wx.ID_ANY))
		f.set("cv")
		f.Show()
'''
HANDLES FILE SELECTION AND GRAPH CREATION
'''
class FileSelectScreen(wx.Frame):
	dir = ""
	paths = []
	screenWidth = 375
	def __init__(self, *args, **kw,):
		super(FileSelectScreen,self).__init__(*args, **kw, size=(self.screenWidth+10,500))
		self.panel = wx.Panel(self)
		self.continueButton = wx.Button(self.panel, label="Continue")
		clearButton = wx.Button(self.panel, label="Clear")
		buttonHolder = wx.BoxSizer(wx.HORIZONTAL)
		buttonHolder.Add(self.continueButton, proportion=1)
		buttonHolder.Add(clearButton, proportion=1)
		
		self.instructions = wx.StaticText(self.panel, size=(self.screenWidth,25),label="Use file chooser to select CSVs, click clear to start over.")
		listHolder = wx.BoxSizer(wx.VERTICAL)

		self.listScrolled = scrolled.ScrolledPanel(self.panel, size=(self.screenWidth,200), style=wx.SIMPLE_BORDER)
		self.listScrolled.SetupScrolling()
		self.listScrolledSizer = wx.BoxSizer(wx.VERTICAL)
		selectFilesButton = wx.Button(self.panel,size=(self.screenWidth,25), label="Select File")
		self.listScrolled.SetSizer(self.listScrolledSizer)
		listHolder.Add(selectFilesButton)
		listHolder.Add(self.listScrolled)
		
		titleHolder = wx.BoxSizer(wx.HORIZONTAL)
		titleHolder.Add(wx.StaticText(self.panel, size=(100,25),label="Experiment Title"))
		self.titleEntry = wx.TextCtrl(self.panel, size=(275,25),id=wx.ID_ANY)
		titleHolder.Add(self.titleEntry)
		
		self.electrodeSelectionHolder = wx.BoxSizer(wx.HORIZONTAL)
		magnitudeSelectionHolder = wx.BoxSizer(wx.HORIZONTAL)
		self.magnitudeBox = wx.RadioBox(self.panel, label='Current Magnitude', pos=(0,0), choices=["Milliamp","Microamps"], majorDimension=1, style=wx.RA_SPECIFY_ROWS)
		magnitudeSelectionHolder.Add(self.magnitudeBox)
		
		directorySelectionHolder = wx.BoxSizer(wx.VERTICAL)
		directorySelect = wx.Button(self.panel, label="Select directory for image folders")
		self.dirText = wx.StaticText(self.panel, label="No directory selected")
		directorySelectionHolder.Add(directorySelect)
		directorySelectionHolder.Add(self.dirText)
		
		self.mainBox = wx.BoxSizer(wx.VERTICAL)
		self.mainBox.Add(self.instructions)
		self.mainBox.Add(titleHolder)
		self.mainBox.Add(magnitudeSelectionHolder)
		self.mainBox.Add(self.electrodeSelectionHolder)
		self.mainBox.Add(directorySelectionHolder)
		self.mainBox.Add(listHolder)
		self.mainBox.Add(buttonHolder)
		self.panel.SetSizerAndFit(self.mainBox)
		
		self.Bind(wx.EVT_BUTTON, self.dirSelectClicked, directorySelect)
		self.Bind(wx.EVT_BUTTON, self.fileSelectClicked, selectFilesButton)
		self.Bind(wx.EVT_BUTTON, self.continueClicked, self.continueButton)
		self.Bind(wx.EVT_BUTTON, self.clearClicked, clearButton)
		
	def set(self, type):
		self.type = type
		if self.type == 'it':
			self.electrodeBox = wx.RadioBox(self.panel, label='Electrode type', pos=(0,0), choices=["Glassy Carbon","Gold"], majorDimension=1, style=wx.RA_SPECIFY_ROWS)
			self.electrodeSelectionHolder.Add(self.electrodeBox)
			self.mainBox.Layout()
			self.Fit()
			#self.panel.SetSizerAndFit(self.mainBox)
			#self.panel.Refresh()
			
	def fileSelectClicked(self, event):
		with wx.FileDialog(self, "Select files", wildcard="CSV files (*.csv)|*.csv", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as fileDialog:
			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return     
			self.paths = self.paths+fileDialog.GetPaths()
			self.listScrolledSizer.Clear()
			for path in self.paths:
				label = wx.StaticText(self.listScrolled, label=path)
				self.listScrolledSizer.Add(label)
			self.listScrolledSizer.Layout()
			self.listScrolled.FitInside()
			
	def dirSelectClicked(self, event):
		with wx.DirDialog(self, "Select folder to save images to", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dirDialog:
			if dirDialog.ShowModal() == wx.ID_CANCEL:
				return     
			self.dir = dirDialog.GetPath()
			self.dirText.SetLabel(self.dir)
			
	def continueClicked(self, event):
		electrode = self.electrodeBox.GetString(self.electrodeBox.GetSelection())
		magnitudeText = self.magnitudeBox.GetString(self.magnitudeBox.GetSelection())
		titleDetails = self.titleEntry.GetValue()
		if len(self.paths) >0 and electrode != "" and magnitudeText !="" and self.dir != "":
			self.continueButton.SetLabel("Processing....")
			#make calls to the functions based on what user selected
			magnitudeParsed = functions.magnitudeSymbol(magnitudeText)
			electrodeArea = functions.electrodeSymbol(electrode)
			graphs = []
			if self.type == 'it':
				ylabel =  'Current Density (' + magnitudeParsed["name"] + ') - area = ' + str(electrodeArea) +" cm^2"
				xlabel = 'Concentration (mM)'
				title = "Current Density - " + titleDetails
				graphs = functions.makeGraphs(xlabel,ylabel,title, 'o', functions.parseFilesIT(self.paths, magnitudeParsed["number"], electrodeArea), self.dir+"\it")
				frame = GraphScreen(None)
				frame.Show()
				frame.set({"graphs":graphs,"xlabel":xlabel,"ylabel":ylabel,"title": title,"savedir":self.dir})
			if self.type == 'cv':
				graphs = functions.makeGraphs('Voltage (V)','Current',"CV - " + titleDetails, '', functions.parseFilesCV(self.paths, magnitudeParsed["number"]), self.dir+"\cv")
			#if we are doing CV, then we are done, else we need to see if some averaging is in order
			self.Destroy()
		
	def clearClicked(self,event):
			self.listScrolledSizer.Clear()
			self.paths = []
			self.listScrolledSizer.Layout()
			self.listScrolled.FitInside()
			
'''
RENDERS DATA INTO THE GRAPHS AND PERFORMS AVERAGING OPERATIONS
convert this to a frame with an options bar where you can create average graphs with selections
and has a make pairs button
'''
class GraphScreen(wx.Frame):
#takes x axis as an argument, pulls data from the objects object
	screenWidth=1000
	def __init__(self, *args, **kw):
		super(GraphScreen,self).__init__(*args, **kw, size=(self.screenWidth+10,500))
		self.panel = wx.Panel(self)
		mainBox = wx.BoxSizer(wx.VERTICAL)
		
		self.graphPanel = scrolled.ScrolledPanel(self.panel, size=(self.screenWidth,900), style=wx.SIMPLE_BORDER)
		self.graphPanel.SetupScrolling()
		
		continueButton = wx.Button(self.panel, label="Finish")
		makePairsButton = wx.Button(self.panel, label="Generate pair graphs")
		menuHolder = wx.BoxSizer(wx.HORIZONTAL)
		makeAveragesButton = wx.Button(self.panel, label="Make Average")
		self.makeAverageEntry = wx.TextCtrl(self.panel, size=(200,30))
		self.averageTitleEntry = wx.TextCtrl(self.panel, size=(200,30))
		makeAverageInstructions = wx.StaticText(self.panel, label="Type names of desired graphs, separated by commas (or type 'all') and a title for the average graph, then hit the 'Make Average' button")
		
		menuHolder.AddMany([makePairsButton, makeAverageInstructions,self.makeAverageEntry, self.averageTitleEntry, makeAveragesButton, continueButton])
			
		mainBox.Add(menuHolder)
		mainBox.Add(self.graphPanel)
		
		self.panel.SetSizerAndFit(mainBox)
		self.Bind(wx.EVT_BUTTON, self.continueClicked, continueButton);
		self.Bind(wx.EVT_BUTTON, self.makePairGraphsClicked,makePairsButton);
		self.Bind(wx.EVT_BUTTON, self.makeAverages,makeAveragesButton);
	
	def set(self, settings):
		self.settings = settings
		graphHolder = wx.GridSizer(3,round(len(settings["graphs"])/3),10)
		for object in settings["graphs"]:
			#load image, create checkbox with label
			image = wx.Image(object["imagepath"])
			image.Rescale(300,300)
			itemText = wx.StaticText(self.graphPanel, label=object["electrodeName"])
			itemHolder = wx.BoxSizer(wx.VERTICAL)
			itemHolder.Add(wx.StaticBitmap(self.graphPanel, wx.ID_ANY, wx.Bitmap(image)))
			itemHolder.Add(itemText)
			graphHolder.Add(itemHolder)
		
		self.graphPanel.SetSizer(graphHolder)
		self.graphPanel.FitInside()
		
	def makeAverages(self, event):
		filt = self.makeAverageEntry.GetValue()
		title = self.averageTitleEntry.GetValue()
		averageGraphs = list(filter(lambda graph: graph["electrodeName"] in filt or filt == "all" or filt == "'all'", self.settings["graphs"]))
		functions.makeAverageGraphs(averageGraphs, self.settings, title)
	
	def continueClicked(self, event):
		self.settings = {}
		self.Destroy()
		
	def makePairGraphsClicked(self, event):
		functions.makePairGraphs(self.settings)
		
app = wx.App()
frame = MainScreen(None, title="EC Data Analysis")
frame.Show()
app.MainLoop()