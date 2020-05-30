#!/usr/bin/env python3
from tabulate import tabulate
import sys
import json
# Enter path to Umaru-chan source folder below
sys.path.insert(1, "/path/to/Umaru-chan/source")
import anime_parser as ap
import colorama
import logging

colorama.init()

#Global vars
data = []
table = []
headers = ["FIELD", "IDEAL VALUE", "PARSED VALUE"]
errors = []

#Read json file from provided path
with open("testdata.json", encoding="utf-8") as f:
	data = json.load(f)

for i in range(len(data)):
	table = []
	try:
		d = ap.Parse(data[i]["file_name"])
		pV = d.getParsedValues()
		finalList = d.finalList
		print("\033[94mTEST #{}\033[0m".format(i))
		print("FILENAME: \033[93m{}\033[0m".format(pV['filename']))
		try:
			idealUp = data[i]["release_group"]
			table.append(["UPLOADER", "\033[92m{}\033[0m".format(idealUp), "\033[95m{}\033[0m".format(pV['uploader'])])
		except:
			table.append(["UPLOADER", "\033[91mNA\033[0m", "\033[95m{}\033[0m".format(pV['uploader'])])
		try:
			idealName = data[i]["anime_title"]
			table.append(["ANIME NAME", "\033[92m{}\033[0m".format(idealName), "\033[95m{}\033[0m".format(pV['anime'])])
		except:
			table.append(["ANIME NAME", "\033[91mNA\033[0m", "\033[95m{}\033[0m".format(pV['anime'])])
		try:
			idealEp = data[i]["episode_number"]
			table.append(["EPISODE NUM", "\033[92m{}\033[0m".format(idealEp), "\033[95m{}\033[0m".format(pV['ep'])])
		except:
			table.append(["EPISODE NUM", "\033[91mNA\033[0m", "\033[95m{}\033[0m".format(pV['ep'])])
		try:
			idealExt = data[i]["file_extension"]
			table.append(["EXTENSION", "\033[92m{}\033[0m".format(idealExt), "\033[95m{}\033[0m".format(pV['ext'])])
		except:
			table.append(["EXTENSION", "\033[91mNA\033[0m", "\033[95m{}\033[0m".format(pV['ext'])])
		try:
			idealQual = data[i]["video_resolution"]
			table.append(["QUALITY", "\033[92m{}\033[0m".format(idealQual), "\033[95m{}\033[0m".format(pV['quality'])])
		except:
			table.append(["QUALITY", "\033[91mNA\033[0m", "\033[95m{}\033[0m".format(pV['quality'])])
		try:
			idealSrc = data[i]["source"]
			table.append(["SOURCE", "\033[92m{}\033[0m".format(idealSrc), "\033[95m{}\033[0m".format(pV['source'])])
		except:
			table.append(["SOURCE", "\033[91mNA\033[0m", "\033[95m{}\033[0m".format(pV['source'])])
		try:
			idealVid = data[i]["video_term"]
			table.append(["VIDEO", "\033[92m{}\033[0m".format(idealVid), "\033[95m{}\033[0m".format(pV['video'])])
		except:
			table.append(["VIDEO", "\033[91mNA\033[0m", "\033[95m{}\033[0m".format(pV['video'])])
		try:
			idealAud = data[i]["audio_term"]
			table.append(["AUDIO", "\033[92m{}\033[0m".format(idealAud), "\033[95m{}\033[0m".format(pV['audio'])])
		except:
			table.append(["AUDIO", "\033[91mNA\033[0m", "\033[95m{}\033[0m".format(pV['audio'])])

		print(tabulate(table, headers, tablefmt = "pretty"))
		print("FINAL_LIST: \033[96m{}\033[0m\n".format(finalList))
	except Exception as e:
		print("\033[91mError in Test Case #{}\033[0m".format(i))
		logging.exception(e)
		print("")
		errors.append(i)

print("\033[92m[*] TESTING FINISHED.\033[0m")
print("\033[91m[*] Runtime Errors: {}\033[0m".format(len(errors)))
print("\033[91m[*] Test Cases: {}\033[0m".format(errors))
