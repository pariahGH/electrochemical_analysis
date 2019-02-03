import pytesseract
from PIL import Image
import glob
import os

def calculateVolumes(initial_volume, initial_concentration, concentration, analyte):
	#takes in the targets and the concentration of our analyte, spits out a list of objects
	data_return = []
	for con in concentration:
		added_vol = float(format((initial_volume * (initial_concentration - con))/(con-analyte),'.3f'))
		initial_volume = initial_volume + added_vol
		initial_concentration = con
		data_return.append({"volume_to_add":added_vol,"concentration":con})
	data_return.append({"volume_to_add":'done',"concentration":'done'})
	return data_return
	
def ocr(directory, cropLocation):
	#given the target directory, goes through and returns an 
	#array of all OCR values
	files = glob.glob(directory+"/*.png")
	ocrData = []
	for i in files:
		image = Image.open(i)
		cropped = image.crop(cropLocation)
		cropped.save(directory+"/temp.png")
		data = pytesseract.image_to_string(Image.open(directory+"/temp.png")).replace("=","").replace("+","").split(" ")
		time = data[1].replace("05","0s")
		iOne = data[4]
		iTwo = data[7]
		ocrData.append({"time":time,"iOne":iOne,"iTwo":iTwo,"file":i})
		os.remove(directory+"/temp.png")
	return(ocrData)
