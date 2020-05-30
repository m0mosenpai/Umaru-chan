#!/usr/bin/env python3
import re
import json

"""
### PROCESS ###
1: Check for extensions from list of extensions and filter it out.
2: Split string at square brackets or paranthesis and form a list. (noBracketsList)
3: Clean each string in the list by removing common separators and trailing spaces.
4: Remove delimiters from the list of delimiters to form the final parsed list. (cleanedList)
5: Filter out quality by checking against the list of possible quality/resolution formats and removing trailing spaces afterwards.
6: Filter out release versions by checking against the list of release version formats and removing trailing spaces.
7. Filter out episoden number of episode by checking for prefixes or ' - ' characters in strings and remove trailing spaces.
8. Filter out audio info by checking against the list of audio info formats and removing trailing spaces.
9. Filter out video info by checking against the list of video info formats and removing trailing spaces.
10. Filter out source info by checking against the list of source info formats and removing trailing spaces.
11. Clean the list one final time to remove any extra spaces/ empty entries
12. Final list will contain the Uploader, Name of the anime and possibly any other info we didn't extract.
"""

stuffToRemove = ["_", ",", ";"]
delimiters =["-"]
qualities = ["1080p", "1920x1080", "Full HD", "FHD", "FullHD", "720p", "1280x720", "HD", "480p", "640x480", "SD"]
extList = [".mkv", ".mp4", ".ogg", ".avi", ".mov", ".wmv", ".mpeg"]
epTokens = ['第', 'ep', 'episode', 'eps', 'episodes', 'e', 'E', 'Ep', 'EP', 'EPISODE', 'EPISODES', 'EPS']
audioTokens = ["2.0CH", "2CH", "5.1", "5.1CH", "DTS", "DTS-ES", "DTS5.1", "TRUEHD5.1", "AAC", "AACX2", "AACX3",
			"AACX4", "AC3", "EAC3", "E-AC-3", "FLAC", "FLACX2", "FLACX3", "FLACX4", "LOSSLESS", "MP3", "OGG",
			"VORBIS", "DUALAUDIO", "DUAL AUDIO"]
sourceTokens = ["BD", "BDRIP", "BLURAY", "BLU-RAY", "DVD", "DVD5", "DVD9", "DVD-R2J", "DVDRIP", "DVD-RIP", "R2DVD",
			"R2J", "R2JDVD", "R2JDVDRIP", "HDTV", "HDTVRIP", "TVRIP", "TV-RIP", "WEBCAST", "WEBRIP"]
videoTokens = ["8BIT", "8-BIT", "10BIT", "10BITS", "10-BIT", "10-BITS", "HI10", "HI10P", "HI444", "HI444P", "HI444PP",
			"H264", "H265", "H.264", "H.265", "X264", "X265", "X.264", "AVC", "HEVC", "HEVC2", "DIVX", "DIVX5", "DIVX6", "XVID"]
releaseTokens = ["V0", "V1", "V2", "V3", "V4"]

class Parse:
	def __init__(self, filename):
		self.filename = filename
		# Extension removed from self.filename and self.filename is updated with new value
		self.extension = self.removeExtension()
		# filename is split about paranthesis/ square brackets and noBracketsList is formed
		self.noBracketsList = self.removeBrackets()
		# List if cleaned by removed separators from stuffToRemove list and result is stored in cleanedList
		# Delimiters are carefully used to further split the list and result is stored in cleanedList
		self.cleanedList = self.cleanStrings(self.noBracketsList)
		# Quality is extracted from cleanedList and removed from the list of values. cleanedList is updated with new values
		self.quality = self.removeQuality()
		# Release version is extracted from the updated cleanedList and removed from the list of values. cleanedList is again updated with new values.
		self.releaseVer = self.removeRelease()
		# Ep num is extracted from previously updated cleanedList and removed from the list of values. cleanedList is updated again.
		self.epNum = self.removeEpisodeNum()
		# Audio info is extracted from previously updated cleanedList and removed from the list of values. cleanedList is updated.
		self.audio = self.removeAudioInfo()
		# Video info is extracted from previously updated cleanedList and removed from the list of values. cleanedList is updated.
		self.video = self.removeVideoInfo()
		# Source info is extracted from previously updated cleanedList and removed from the list of valeus. cleanedList is updated.
		self.source = self.removeSourceInfo()
		# Clean list one final time
		# At this point of time, we have extracted most (if not all) of the important information.
		# We should be left with
		self.finalList = self.cleanStrings(self.cleanedList)

		# Get final parsed values
		self.parsedOutput = self.getParsedValues()

	### HELPER TO CLEAN LIST ###
	# Remove space fillers / info separators
	def cleanStrings(self, inputList):
		cleanList = []
		for string in inputList:
			if string != "" and string != " ":
				# print("String: {}".format(string))
				for stuff in stuffToRemove:
					# print("Stuff: {}".format(stuff))
					if stuff in string:
						string = string.replace(stuff, " ").strip(" ")
						# print("Clean String: {}".format(string))

				for delim in delimiters:
					cleanList.append(string.strip(" ").strip(delim).strip(" "))
				# cleanList.append(string.strip(" "))
		return cleanList

	### MAIN PARSING METHODS ###
	# Get extension of media file
	def removeExtension(self):
		extension = None
		for ext in extList:
			idx = self.filename.find(ext)
			if idx != -1:
				#Store extension and remove it from original filename
				extension = self.filename[idx:idx + len(ext)]
				self.filename = self.filename.replace(extension, "").strip(" ")
				break
		return extension

	# Remove square brackets and paranthesis and break string into list at those positions
	def removeBrackets(self):
		noBracketsList = re.split("\[|]|\(|\)", self.filename)
		return noBracketsList


	# Get quality and remove it from the list of strings
	def removeQuality(self):
		for qual in qualities:
			if qual in self.cleanedList:
				quality = qual
				self.cleanedList.pop(self.cleanedList.index(qual))
				return quality
			else:
				for i, string in enumerate(self.cleanedList):
					idx = string.find(qual)
					if idx != -1:
						quality = string[idx: idx + len(qual)]
						self.cleanedList[i] = string.replace(quality, "").strip(" ")
						return quality
		return ""

	# Get release version and filter it from the list
	def removeRelease(self):
		for i, string in enumerate(self.cleanedList):
			lowerStr = string.lower()
			for token in releaseTokens:
				token = token.lower()
				idx = lowerStr.find(token)
				if idx != -1:
					releaseVer = string[idx: idx + len(token)]
					self.cleanedList[i] = re.compile(re.escape(releaseVer), re.IGNORECASE).sub("", string).strip(" ")
					# self.cleanedList[i] = string.replace(releaseVer, "").strip(" ")
					return releaseVer

		return ""

	# Get episode number and remove it from the list of strings
	def removeEpisodeNum(self):
		for i, string in enumerate(self.cleanedList):
			lowerStr = string.lower()
			if string.find(" - ") != -1:
				idx = string.find(" - ")
				if string[idx + 3:].isdigit():
					episodeNum = string[idx + 3:]
					self.cleanedList[i] = string.replace(episodeNum, "").strip(" ")
					return episodeNum
				elif string[:idx].isdigit():
					episodeNum = string[:idx]
					self.cleanedList[i] = string.replace(episodeNum, "").strip(" ")
					return episodeNum
			else:
				for token in epTokens:
					idx = string.find(token)
					if idx != -1 and lowerStr[idx + len(token)].isdigit():
						episodeNum = string[idx + len(token):]
						# print("EP: {}".format(episodeNum))
						# print("Token: {}".format(token))
						# print("String: {}".format(self.cleanedList[i]))
						self.cleanedList[i] = string.replace(token + episodeNum, "").strip(" ")
						# print("String: {}".format(self.cleanedList[i]))
						return episodeNum
		return ""

	#Get audio info and remove it from the list of strings
	def removeAudioInfo(self):
		for i, string in enumerate(self.cleanedList):
			lowerStr = string.lower()
			for token in audioTokens:
				token = token.lower()
				idx = lowerStr.find(token)
				if idx != -1:
					audio = string[idx: idx + len(token)]
					# self.cleanedList[i] = string.replace(audio, "").strip(" ")
					self.cleanedList[i] = re.compile(re.escape(audio), re.IGNORECASE).sub("", string).strip(" ")
					return audio
		return ""

	def removeVideoInfo(self):
		for i, string in enumerate(self.cleanedList):
			lowerStr = string.lower()
			for token in videoTokens:
				token = token.lower()
				idx = lowerStr.find(token)
				if idx != -1:
					video = string[idx: idx + len(token)]
					self.cleanedList[i] = re.compile(re.escape(video), re.IGNORECASE).sub("", string).strip(" ")
					# self.cleanedList[i] = string.replace(video, "").strip(" ")
					return video
		return ""

	def removeSourceInfo(self):
		for i, string in enumerate(self.cleanedList):
			lowerStr = string.lower()
			for token in sourceTokens:
				token = token.lower()
				idx = lowerStr.find(token)
				if idx != -1:
					source = string[idx: idx + len(token)]
					self.cleanedList[i] = re.compile(re.escape(source), re.IGNORECASE).sub("", string).strip(" ")
					# self.cleanedList[i] = string.replace(source, "").strip(" ")
					return source
		return ""

	def getParsedValues(self):
		if len(self.finalList) >= 2:
			uploader = self.finalList[0]
			anime = self.finalList[1]
		else:
			uploader = ""
			anime = self.finalList[0]

		return {"filename": self.filename, "uploader": uploader, "anime": anime, "ep": self.epNum, "ext": self.extension, "quality": self.quality,
				"release": self.releaseVer, "source": self.source, "video": self.video, "audio": self.audio}
