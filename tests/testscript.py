import sys
import json
import anime_parser as ap

#Global vars
args = sys.argv
jsonpath = args[1]
data = []

print("Opening '{}'".format(jsonpath))

#Read json file from provided path
with open(jsonpath, encoding="utf-8") as f:
	data = json.load(f)

for i in range(len(data)):
	#print(data[i]["file_name"])
	d = ap.Parse(data[i]["file_name"])
	print(d.getParsedValues())
	print(d.finalList)
