#!/usr/bin/env python3
import re
import json

"""
###PROCESS###
STEP-1: Check for extensions from list of extensions and filter it out.
STEP-2: Split string at square brackets or paranthesis and form a list.
STEP-3: Clean each string in the list by removing common separators and trailing spaces
STEP-4: Remove delimiters from the list of delimiters to form the final parsed list.
STEP-5:
"""

stuffToRemove = ["_", ",", ";"]
delimiters =["-"]
qualities = ["1080p", "1920x1080", "720p", "1280x720", "480p", "640x480"]
extList = [".mkv", ".mp4", ".ogg", ".avi", ".mov", ".wmv", ".mpeg"]

class Parse:
	def __init__(self, filename):
		self.filename = filename
		self.extension = self.removeExtension()
		self.noBracketsList = self.removeBrackets()
		self.cleanList = self.cleanStrings()
		self.noDelimitersList = self.removeDelimiters()

	# Get extension of media file
	def removeExtension(self):
		extension = None
		for ext in extList:
			idx = self.filename.find(ext)
			if idx != -1:
				#Store extension and remove it from original filename
				extension = self.filename[idx:idx + len(ext)]
				self.filename = self.filename[:idx]
				break
		return extension

	# Remove square brackets and paranthesis and break string into list at those positions
	def removeBrackets(self):
		noBracketsList = re.split("\[|]|\(|\)", self.filename)
		return noBracketsList

	# Remove space fillers / info separators
	def cleanStrings(self):
		cleanList = []
		for string in self.noBracketsList:
			# print("String: {}".format(string))
			if string != "":
				for stuff in stuffToRemove:
					# print("Stuff: {}".format(stuff))
					if stuff in string:
						string = string.replace(stuff, " ").strip(" ")
						# print("Clean String: {}".format(string))
				cleanList.append(string)
		return cleanList

	# Break list further at delimiters
	def removeDelimiters(self):
		newList = []
		for string in self.cleanList:
			for delim in delimiters:
				if string.find(delim) != -1:
					# Split string around delimiters and remove trailing white spaces from each non-blank entry in the list
					newList += [s.strip(" ") for s in string.split(delim) if s != ""]
				else:
					newList.append(string)	
		return newList

	# def getQuality(self):
	# 	for qual in qualities:
	# 		if qual in noDelimitersList:
