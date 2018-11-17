#gui system for the lab program
from mss import mss
import datetime
import os
import wx
import data_functions
from PIL import Image
import re

sct = mss()
settings = {}

class SettingsScreen(wx.Frame):
	#we will need to add title, fields for intiial volume, analyte conc, initial conc, and desired
	dir = ""
	def __init__(self, *args, **kw):
		super(SettingsScreen,self).__init__(*args, **kw, size=(400,400))
		panel = wx.Panel(self)
		
		titleText = wx.StaticText(panel, label="Settings for EC experiment", style=wx.ALIGN_CENTRE_HORIZONTAL)
		
		dirSelectHolder = wx.BoxSizer(wx.VERTICAL)
		dirSelectButton = wx.Button(panel, label="Select folder")
		self.dirText = wx.StaticText(panel, label="No folder selected")
		dirSelectHolder.Add(dirSelectButton)
		dirSelectHolder.Add(self.dirText)
		self.Bind(wx.EVT_BUTTON, self.dirSelectClicked, dirSelectButton)
		
		#set up our fields
		experimentText = wx.StaticText(panel, label="Experiment Name:")
		initVolText = wx.StaticText(panel, label="Initial Cell Volume (mL):")
		initConText = wx.StaticText(panel, label="Initial Concentration (mM):")
		analyteConText = wx.StaticText(panel, label="Analyte Concentration (mM):")
		desiredConText = wx.StaticText(panel, label="Target Concentrations (mM):")
		e2labelText = wx.StaticText(panel, label="Electrode 2 Label:")
		e1labelText = wx.StaticText(panel, label="Electrode 1 Label:")
		self.initVolEntry = wx.TextCtrl(panel)
		self.initConEntry = wx.TextCtrl(panel)
		self.analyteConEntry = wx.TextCtrl(panel)
		self.desiredConEntry = wx.TextCtrl(panel)
		self.e1labelEntry = wx.TextCtrl(panel)
		self.e2labelEntry = wx.TextCtrl(panel)
		self.experimentEntry = wx.TextCtrl(panel)
		
		fieldsBox = wx.FlexGridSizer(7, 2, 10, 10) #holds the fields
		fieldsBox.AddMany([
			(initVolText),(self.initVolEntry, 1, wx.EXPAND),(initConText),(self.initConEntry, 1, wx.EXPAND),
			(analyteConText),(self.analyteConEntry, 1, wx.EXPAND),(desiredConText),(self.desiredConEntry, 1, wx.EXPAND),
			(e1labelText),(self.e1labelEntry, 1, wx.EXPAND),
			(e2labelText),(self.e2labelEntry, 1, wx.EXPAND),
			(experimentText),(self.experimentEntry, 1, wx.EXPAND)
		])
		
		buttonsHolder = wx.GridSizer(1, 2 , 5, 5)
		confirmButton = wx.Button(panel, label="Confirm")
		cancelButton = wx.Button(panel, label="Cancel")
		buttonsHolder.AddMany([
		(confirmButton,0, wx.EXPAND), (cancelButton,0, wx.EXPAND)
		])
		
		#holds everything
		mainBox = wx.BoxSizer(wx.VERTICAL)
		mainBox.Add(titleText, proportion=1)
		mainBox.Add(dirSelectHolder, proportion=1)
		mainBox.Add(fieldsBox, proportion=4)		
		mainBox.Add(buttonsHolder, proportion=1)
		
		panel.SetSizerAndFit(mainBox)
		
		self.Bind(wx.EVT_BUTTON, self.cancelButtonClicked, cancelButton)
		self.Bind(wx.EVT_BUTTON, self.confirmButtonClicked, confirmButton)
			
	def intCheck(self, item):
		if item != "" and item != " ":
			return int(item)
				
	def confirmButtonClicked(self, event):
		#get all inputs, process our array, handoff to experiment screen
		if self.dir != "":
			settings["i_con"] = int(self.initConEntry.GetValue())
			settings["i_vol"] = int(self.initVolEntry.GetValue())
			settings["a_con"] = int(self.analyteConEntry.GetValue())
			settings["desired_con"] = list(filter(lambda x: x is not None,[self.intCheck(item) for item in self.desiredConEntry.GetValue().split(" ")]))
			settings["directory"] = self.dir+"\\"+self.experimentEntry.GetValue()+"-RecorderData"
			settings["timestamps"] = data_functions.calculateVolumes(settings["i_vol"],settings["i_con"],settings["desired_con"],settings["a_con"])
			settings["ionename"] = self.e1labelEntry.GetValue()
			settings["itwoname"] = self.e2labelEntry.GetValue()
			os.mkdir(settings["directory"])
			frame = ExperimentScreen(None, title=settings["directory"])
			frame.Show()
			self.Destroy()
	
	def dirSelectClicked(self, event):
		with wx.DirDialog(self, "Select folder to create experiment folder in", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as dirDialog:
			if dirDialog.ShowModal() == wx.ID_CANCEL:
				return     
			self.dir = dirDialog.GetPath()
			self.dirText.SetLabel(self.dir)
		
	def cancelButtonClicked(self, event):
		self.Destroy()
		
class ExperimentScreen(wx.Frame):
	#three rows, one for screenshot checkmarks, one for volume to add, and one for added checkmarks
	#every time we do a screenshot, check if we are on the last one - if so, we are done!
	def __init__(self, *args, **kw):
		super(ExperimentScreen,self).__init__(*args,**kw, size=(800,100))
		self.stampNumber = 0 #track where we are
		panel = wx.Panel(self)
		holder = wx.FlexGridSizer(1,3,5,5)
		labelHolder = wx.GridSizer(4,1,1,1)
		self.rowHolder = wx.GridSizer(4, len(settings["timestamps"]), 5, 5)
		buttonHolder = wx.GridSizer(2,1,5,5)
		
		self.screenshotButton = wx.Button(panel, label="Take &Screenshot")
		self.addedAnalyteButton = wx.Button(panel, label="Added &Analyte")
		self.addedAnalyteButton.Disable()#default disabled because this is should not be activated before screenshot button
		self.Bind(wx.EVT_BUTTON, self.screenShot, self.screenshotButton)
		self.Bind(wx.EVT_BUTTON, self.analyteAdded, self.addedAnalyteButton)
		buttonHolder.AddMany([(self.screenshotButton),(self.addedAnalyteButton)])
		
		#create rows - red backgrounds!
		self.screenRows = []
		self.analyteVolRows = []
		self.analyteAddedRows = []
		self.newConcentrationRows = []
		itemSize = (30,30)
		for item in settings["timestamps"]:
			#create a box each for the indicators (red backgrcunds) and the vol to add, add to appropiate rows
			volAddText = wx.StaticText(panel, label=str(item["volume_to_add"]), size=itemSize)
			screenAddText = wx.StaticText(panel, label="x", size=itemSize, style=wx.ALIGN_CENTRE_HORIZONTAL)
			screenAddText.SetBackgroundColour('red')
			analyteAddText = wx.StaticText(panel, label="x", size=itemSize, style=wx.ALIGN_CENTRE_HORIZONTAL)
			analyteAddText.SetBackgroundColour('red')
			newConcentrationText = wx.StaticText(panel, label=str(item["concentration"]), size=itemSize, style=wx.ALIGN_CENTRE_HORIZONTAL)
			self.screenRows.append((screenAddText,1,wx.EXPAND))
			self.analyteVolRows .append((volAddText,1,wx.EXPAND))
			self.analyteAddedRows.append((analyteAddText,1,wx.EXPAND))
			self.newConcentrationRows.append((newConcentrationText, 1, wx.EXPAND))
		
		screenshotLabel = wx.StaticText(panel, size=(80,20), label="Screenshot:")
		analyteLabel = wx.StaticText(panel, size=(80,20), label="Analyte Vol:")
		analyteAddedLabel = wx.StaticText(panel, size=(80,20), label="Added:")
		newConcentrationLabel = wx.StaticText(panel, size=(80,20), label="New [A]:")
		labelHolder.AddMany([(screenshotLabel),(analyteLabel),(analyteAddedLabel), (newConcentrationLabel)])
		
		self.rowHolder.AddMany(self.screenRows)
		self.rowHolder.AddMany(self.analyteVolRows)
		self.rowHolder.AddMany(self.analyteAddedRows)
		self.rowHolder.AddMany(self.newConcentrationRows)
		
		holder.AddMany([(buttonHolder, 1, wx.EXPAND),(labelHolder, 1, wx.EXPAND),(self.rowHolder, 1, wx.EXPAND)])
		panel.SetSizerAndFit(holder)
		
	#update our data when requested
	def screenShot(self, event):
		self.screenshotButton.Disable()
		#check if this is our last screenshot, if so then we go ahead and exit after taking our screenshot
		file = sct.shot(output=settings["directory"]+'\stamp'+str(self.stampNumber)+'.png')
		settings["timestamps"][self.stampNumber]["file"] = file
		#for testing, load all the stamp image filenames into our settings["timestamps"] array 
		settings["timestamps"][self.stampNumber]["time_one"] = datetime.datetime.now()
		settings["timestamps"][self.stampNumber]["concentration"] = ([0] +settings["desired_con"])[self.stampNumber]
		#change background to green
		target = self.rowHolder.GetItem(self.stampNumber).GetWindow()
		target.SetBackgroundColour('green')
		target.SetLabelText('o')
		if self.stampNumber+1 == len(settings["timestamps"]):
			settings["timestamps"][self.stampNumber]["time_two"] = datetime.datetime.now()
			settings["timestamps"][self.stampNumber]["delta"] = (settings["timestamps"][self.stampNumber]["time_two"] - settings["timestamps"][self.stampNumber]["time_one"]).total_seconds()
			settings["timestamps"][self.stampNumber]["time_one"] = str(settings["timestamps"][self.stampNumber]["time_one"].time())
			settings["timestamps"][self.stampNumber]["time_two"] = str(settings["timestamps"][self.stampNumber]["time_two"].time())
			self.screenshotButton.SetLabelText('Processing...')
			with open(settings["directory"]+"/data_pre_ocr.csv",'w') as w:
				w.write("Filename,Time of Screenshot,Time of Glucose,Time Between,Experiment Time,"+settings["ionename"]+","+settings["itwoname"]+"\n")
				for item in settings["timestamps"]:
					w.write(str(item["file"])+","+str(item["time_one"])+","+str(item["time_two"])+","+str(item["delta"])+"\n")
			frame = OCRScreen(None, title=settings["directory"])
			frame.Show()
			self.Destroy()
		self.addedAnalyteButton.Enable()

	def analyteAdded(self, event):
		self.addedAnalyteButton.Disable()
		settings["timestamps"][self.stampNumber]["time_two"] = datetime.datetime.now()
		settings["timestamps"][self.stampNumber]["delta"] = (settings["timestamps"][self.stampNumber]["time_two"] - settings["timestamps"][self.stampNumber]["time_one"]).total_seconds()
		settings["timestamps"][self.stampNumber]["time_one"] = str(settings["timestamps"][self.stampNumber]["time_one"].time())
		settings["timestamps"][self.stampNumber]["time_two"] = str(settings["timestamps"][self.stampNumber]["time_two"].time())
		#change background to green
		target = self.rowHolder.GetItem(self.stampNumber+2*len(settings["timestamps"])).GetWindow()
		target.SetBackgroundColour('green')
		target.SetLabelText('o')
		self.stampNumber +=1
		self.screenshotButton.Enable()

class OCRScreen(wx.Frame):
	#uses ocr to decipher data, then will display side by side of picture+extracted number for confirmation and fixing if needed
	def __init__(self, *args, **kw):
		super(OCRScreen,self).__init__(*args,**kw, size=(1300,600))
		self.itemNumber = 0
		#tuple, left upper right lower
		ocrData = data_functions.ocr(settings["directory"],(20, 984, 530, 1010))
		# then merge with ocrdata
		#ocrData = data_functions.ocr('.',(20, 984, 530, 1010))
		for i in ocrData:
			target = list(filter(lambda x: x["file"] == i["file"],settings["timestamps"]))[0]
			target["time"] = i["time"] 
			target["iOne"] = i["iOne"]
			target["iTwo"] = i["iTwo"]
		panel = wx.Panel(self)
		itemHolder = wx.BoxSizer(wx.HORIZONTAL)
		entryHolder = wx.GridSizer(4,2,5,5)
		
		print(settings["timestamps"])
		
		buttonHolder = wx.BoxSizer(wx.HORIZONTAL)
		self.nextButton = wx.Button(panel, label="Next")
		self.Bind(wx.EVT_BUTTON, self.nextButtonClicked, self.nextButton)
		buttonHolder.Add(self.nextButton)
		
		self.timeEntry = wx.TextCtrl(panel)
		self.ioneEntry = wx.TextCtrl(panel)
		self.itwoEntry = wx.TextCtrl(panel)
		timeLabel = wx.StaticText(panel, label="  Time")
		itwoLabel = wx.StaticText(panel, label="  I2")
		ioneLabel = wx.StaticText(panel, label="  I1")

		self.img = wx.Image(settings["timestamps"][0]["file"])
		self.img.Rescale(960,540)
		self.imagePanel = wx.StaticBitmap(panel, wx.ID_ANY,wx.Bitmap(self.img))
		#there is a character that resembles a hyphen but isnt - second to last character in the set below
		replacePat = re.compile("([^\.0-9e—-])")
		iOne = replacePat.sub("",settings["timestamps"][0]["iOne"]).replace("-","-")
		iTwo = replacePat.sub("",settings["timestamps"][0]["iTwo"]).replace("-","-")
		
		self.timeEntry.SetValue(settings["timestamps"][0]["time"])
		self.ioneEntry.SetValue(iOne)
		self.itwoEntry.SetValue(iTwo)
		
		entryHolder.AddMany([
		(timeLabel),(self.timeEntry, 1, wx.EXPAND),
		(ioneLabel),(self.ioneEntry, 1, wx.EXPAND),
		(itwoLabel),(self.itwoEntry, 1, wx.EXPAND)
		])
		
		itemHolder.Add(self.imagePanel)
		itemHolder.Add(entryHolder)
		itemHolder.Add(buttonHolder)
		
		panel.SetSizerAndFit(itemHolder)

	def nextButtonClicked(self, event):
		if self.itemNumber == len(settings["timestamps"])-1:
			#we are done, proceed to data analysis
			with open(settings["directory"]+"/data.csv",'w') as w:
				w.write("Filename,Time of Screenshot,Time of Glucose,Time Between,Experiment Time,"+settings["ionename"]+","+settings["itwoname"]+"Concentrations"+"\n")
				for item in settings["timestamps"]:
					w.write(str(item["file"])+","+str(item["time_one"])+","+str(item["time_two"])+","+str(item["delta"])+","+str(item["time"])+","+str(item["iOne"]).replace("A","")+","+str(item["iTwo"]).replace("A","")+","+str(item["concentration"])+"\n")
			self.Destroy()
		else:
			#save data 
			settings["timestamps"][self.itemNumber]["time"] = self.timeEntry.GetValue()
			settings["timestamps"][self.itemNumber]["iOne"] = self.ioneEntry.GetValue()
			settings["timestamps"][self.itemNumber]["iTwo"] = self.itwoEntry.GetValue()
			self.itemNumber+=1
			self.img = wx.Image(settings["timestamps"][self.itemNumber]["file"])
			self.img.Rescale(960,540)
			self.timeEntry.SetValue(settings["timestamps"][self.itemNumber]["time"])
			self.ioneEntry.SetValue(settings["timestamps"][self.itemNumber]["iOne"])
			self.itwoEntry.SetValue(settings["timestamps"][self.itemNumber]["iTwo"])
			self.imagePanel.SetBitmap(wx.Bitmap(self.img))

app = wx.App()
frame = SettingsScreen(None, title="EC Data Recorder")
frame.Show()
app.MainLoop()