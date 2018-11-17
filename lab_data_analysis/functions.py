from decimal import Decimal as dec
import decimal
import re
import matplotlib.pyplot as plt
import os
decimal.getcontext().rounding = 'ROUND_HALF_UP'

def parseFilesIT(paths, magnitude, electrodeArea):
	allParsedData = []
	for path in paths:
		#last and second to last are electrodes, third to last is the axis item (concentration for it)
		dataOne = []
		dataTwo = []
		axis = []
		try:
			file = open(path, 'r').readlines()
			eOne = file[0].split(",")[-3].replace("\n","")
			eTwo = file[0].split(",")[-2].replace("\n","")
			for line in file[1:]:
				target = line.split(",")
				#convert to current density by multiplying by desired magnitude (ie 1E6 for microamps) and dividing by electrode area
				dataOne.append(dec(target[-3])*dec(magnitude)/dec(electrodeArea))
				dataTwo.append(dec(target[-2])*dec(magnitude)/dec(electrodeArea))
				axis.append(dec(target[-1]))
			allParsedData.append({"data":dataOne,"path":path,"pairname":eOne+","+eTwo,"electrodeName":eOne,"xaxis":axis})
			allParsedData.append({"data":dataTwo,"path":path,"pairname":eOne+","+eTwo,"electrodeName":eTwo,"xaxis":axis})
		except IOError:
			wx.LogError("Cannot open file")
		except decimal.InvalidOperation:
			print(path)
			x = input()
			exit()
		except UnicodeDecodeError:
			print(path)
			x = input()
			exit()
	return allParsedData

electrodeNamePattern = re.compile("(e+[0-9]*)")
def parseFilesCV(paths, magnitude):
	allParsedData = []
	for path in paths: 
		dataOne = []
		dataTwo = []
		axis = []
		try:
			file = open(path, 'r').readlines()
			#the last 1000 lines contain the final CV sweep
			for line in file[-1000:]:
				target = line.split(",")
				#convert to desired units by multiplying by magnitude
				dataOne.append(dec(target[-2])*dec(magnitude))
				dataTwo.append(dec(target[-1])*dec(magnitude))
				## this needs to be changed
				axis.append(dec((target[-3])))
			electrodenames = electrodeNamePattern.findall(path.split("\\")[-1])
			data.append({"data":dataOne,"path":path,"electrodeName":electrodeNames[0],"pairname":electrodenames,"xaxis":axis})
			data.append({"data":dataTwo,"path":path,"electrodeName":electrodeNames[1],"pairname":electrodenames,"xaxis":axis})
			file.close()
		except IOError:
			wx.LogError("Cannot open file")
	return allParsedData
	'''
	DO DIRECTORY EXISTENCE CHECKS BEFORE WRITING
	'''
def makeGraphs(xlabel, ylabel, title, markerSymbol,data, savedir):
	graphs = []
	if not os.path.exists(savedir):
		os.mkdir(savedir)
	for index,electrode in enumerate(data):
		#plot the array against concentration
		#create object with the data and the filepath
		fig = plt.figure()
		plt.plot(electrode['xaxis'], electrode["data"], marker=markerSymbol)
		plt.xlabel(xlabel)
		plt.ylabel(ylabel)
		plt.title(title + " - " + electrode["electrodeName"])
		plt.grid()
		imagePath = (savedir + "/"+str(electrode["electrodeName"]).replace(" ","_")+".png")
		fig.savefig(imagePath,bbox_inches='tight')
		plt.close(fig)
		electrode["imagepath"] = imagePath
		electrode["selected"] = False
		graphs.append(electrode)
	return graphs
	
def makeAverageGraphs(graphs, settings, averageTitle):
	#average together all the electrodes out of their pairsaverageData = []
	#check which ones were selected and put them into our averaging set
	if not os.path.exists(settings["savedir"]+"/averaged"):
		os.mkdir(settings["savedir"]+"/averaged")
	averageData = []
	for object in graphs:
		averageData.append(object["data"])
	numberOfSets = dec(len(averageData)) #number of points in each row, where each point comes from a different set
	rows = []
	averages = []
	stdDevs = []
	sems = []
	#transfrom selected into an array of relevant points
	for index, number in enumerate(averageData[0]):
		rows.append([])
		for object in averageData:
			rows[index].append(object[index])
	#calculate averages
	for row in rows:
		averages.append(dec(sum(row))/numberOfSets)
	#calculate std deviations
	fig = plt.figure()
	for index,avg in enumerate(averages):
		stdDev =(sum([(e-avg)**dec('2.0') for e in rows[index]])/(numberOfSets-1))**dec('.5')
		stdDevs.append(stdDev)
		sems.append(stdDev/(numberOfSets**dec('.5')))
	plt.errorbar(graphs[0]["xaxis"], averages, yerr=sems, capsize=5, marker="o")
	plt.xlabel(settings["xlabel"])
	plt.ylabel(settings["ylabel"])
	plt.title(settings['title']+' - '+averageTitle+' (Average +- Std Dev) ' + str(len(graphs)) + ' runs')
	plt.xticks([float(i) for i in graphs[0]["xaxis"]])
	plt.grid()
	imgfilename = settings["savedir"]+"/averaged/"+averageTitle.replace(" ","_")+".png"
	csvfilename = settings["savedir"]+"/averaged/"+averageTitle.replace(" ","_")+".csv"
	fig.savefig(imgfilename,bbox_inches='tight')
	plt.close(fig)
	with open(csvfilename,'w') as w:
		w.write("Average Current Density,Standard Deviation,Standard Error of the Mean, Number of Data Points\n")
		for index, item in enumerate(averages):
				w.write(str(item)+","+str(stdDevs[index])+","+str(sems[index])+","+str(numberOfSets)+"\n")
	return
	
#order is preserved so we just match up pairs
def makePairGraphs(settings):
	if not os.path.exists(settings["savedir"]+"/it_pairs"):
		os.mkdir(settings["savedir"]+"/it_pairs")
	#each pair contains the two electrodes and their data - they just need to be plotted together
	for index, electrode in enumerate(settings["graphs"]):
		if index%2 != 0:
			continue
		else:
			fig = plt.figure()
			line = plt.plot(electrode['xaxis'], electrode["data"], marker="o")[0]
			line.set_label(electrode["electrodeName"])
			if index+1 != len(settings):
				linetwo = plt.plot(settings["graphs"][index+1]['xaxis'], settings["graphs"][index+1]["data"], marker="o")[0]
				linetwo.set_label(settings["graphs"][index+1]["electrodeName"])
			plt.xlabel(settings["xlabel"])
			plt.ylabel(settings["ylabel"])
			plt.title(settings["title"]+" "+electrode["pairname"])
			plt.xticks([float(i) for i in electrode['xaxis']])
			plt.grid()
			plt.legend()
			fig.savefig(settings["savedir"]+"/it_pairs/"+electrode["pairname"].replace(" ","_"),bbox_inches='tight')
			plt.close(fig)
	return
	
magnitudeNames = {"Milliamps":"mA","Microamps":"uA"}
magnitudeNumbers = {"Milliamps":1E3,"Microamps":1E6}
def magnitudeSymbol(magnitude):
	return {"name":magnitudeNames[magnitude],"number":magnitudeNumbers[magnitude]}
	
electrodeAreas = {"Glassy Carbon":.07,"Gold":.03}
def electrodeSymbol(electrode):
	return electrodeAreas[electrode]