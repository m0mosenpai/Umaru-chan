import scrapy
import json
import urllib.request
import ssl
import time
import colorama
import datetime
import pytz
import logging
import sys
import os
# sys.path.insert(1, "/home/momo/Documents/Programs/Umaru-chan/source")

for handler in logging.root.handlers[:]:
	logging.root.removeHandler(handler)

logging.basicConfig(filename="../../data/serverlog.log",level=logging.DEBUG,format="[%(asctime)s][%(levelname)s]:%(message)s",
	datefmt="%Y-%m-%d %H:%M:%S")
logging.getLogger('scrapy').propagate = False

ssl._create_default_https_context = ssl._create_unverified_context
colorama.init()

links = []
path = ""
quality = ""
DONE = False
ANIME_IN_CHECK = ""

class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

#Return true if latest ep is out, otherwise return false
def checkLatestEp(response):
	gap = 518400 #6 days in seconds
	try:
		latest_ep = response.xpath('//td[@colspan="2"]/a[not(@class)]/@title').extract()[0]
		aname = (latest_ep[latest_ep.index('] '):latest_ep.index(' -')][2:])
		release_ts = float(response.xpath('//td[@class="text-center"][3]/@data-timestamp').extract()[0])
	except IndexError:
		#First episode of the season, hence no entry yet
		return False

	now_ts = time.time()

	if (now_ts - release_ts) < gap:
		#Topmost ep is the latest ep
		logging.info("({}) gap = {}, Topmost ep is the latest ep".format(aname, now_ts-release_ts))
		return True
	logging.info("({}) gap = {}, Topmost ep is not the latest ep".format(aname, now_ts-release_ts))
	return False

#Reads config file
def readConfig():
	with open("../../data/config.json", 'r+') as f:
		config = json.load(f)
	return config

#Get PDT
def getPDT():
	pst_timezone = pytz.timezone("US/Pacific")
	pdt = datetime.datetime.now(pst_timezone).time()
	return pdt

#Download episode
def downloadEp(epno, aname, response):
	config = readConfig()
	currentep = int(config["watchlist"][aname][0])

	from_ep = currentep + 1
	to_ep = int(epno) + 1

	logging.info("({}) Downloading eps {} - {}".format(aname, from_ep, to_ep))

	for i in range(from_ep, to_ep): #ep no in config is the last downloaded ep
		link = "https://nyaa.si"
		link += response.xpath('//a[contains(text(), "- ' + f'{i:02}' +'")]/../following-sibling::td[1]/a/@href').extract()[0]
		print("[*] Found new episode: \033[95m{} [{}] - {}\033[0m".format(i, quality, aname))
		urllib.request.urlretrieve(link, path + aname + str(i) + " [{}].torrent".format(quality))
		logging.info("({}) Downloaded ep {}".format(aname, i))
		print("\033[92m[+] Downloaded!\033[0m")

		#Update config with latest downloaded episode and timestamp
		config["watchlist"][aname][0] = str(i)
		config["watchlist"][aname][1] = str(time.time())

	with open("../../data/config.json", 'w') as f:
		json.dump(config, f, indent=4)

#Displays ETA message
def getETAMessage(response):
	config = readConfig()

	url = response.request.url
	name = url[url.find("+") + 1:url.find(quality) - 1].replace("+", " ")

	curr_pdt = getPDT().strftime("%H:%M")
	curr_min = int(curr_pdt[0:2]) * 60 + int(curr_pdt[3:5])

	show_time = ""
	show_min = 0
	if name in config.keys():
		show_time = config[name][2][1]
		show_min = (int(show_time / 100) * 60 + show_time % 100) + 75 #Airing time + 75 mins
	diff = 0
	if show_min > curr_min:
		diff = show_min - curr_min
	diff_hr = int(diff / 60)
	diff_min = diff % 60

	return [name, diff_hr, diff_min]


class HSlatestShow(scrapy.Spider):
	name = 'hslatest'
	start_urls = ["https://nyaa.si/"]

	def parse(self, response):
		global path
		global quality
		global ANIME_IN_CHECK

		config = readConfig()
		path = config["main"]["torrent"]
		quality = config["main"]["quality"]
		watchlist = config["watchlist"]

		for show in watchlist:
			ANIME_IN_CHECK = show
			head = "https://nyaa.si/?f=0&c=0_0&q=subsplease+"
			tail = "+" + quality + "+" + "mkv" + "&p="
			name = show.replace(' ', '+')
			if self.mode == "all" or watchlist[show][1] == "-1":
				query = head + name + tail
				yield scrapy.Request(query, callback = self.parse_show)

	def parse_show(self, response):
		#Get the latest episode of the anime
		try:
			latest_ep = response.xpath('//td[@colspan="2"]/a[not(@class)]/@title').extract()[0]
			magnet_link = response.xpath('//td[@class="text-center"]/a/@href').extract()[1]

			# print("latest_ep: {}".format(latest_ep))
			# aname = (latest_ep[latest_ep.index('] '):latest_ep.index(' -')][2:])

			with cd("../../../"):
				import anime_parser as ap

				d = ap.Parse(latest_ep)
				aname = d.getParsedValues()['anime']
				epno = d.getParsedValues()['ep']

			# epno = (latest_ep[latest_ep.index('- '):latest_ep.index(' [')][2:])

			ANIME_IN_CHECK = aname

			downloadEp(epno, aname, response)
		except IndexError:
			#First episode of season, hence page will be empty
			ETA = getETAMessage(response)
			print("[*] {}: \033[91mEmpty page\033[0m \033[96m[ETA: {}h{}m]\033[0m".format(ETA[0], ETA[1], ETA[2]))

		if self.mode == "normal":
			#Latest ep is not out, continue checking
			if not checkLatestEp(response):
				ETA = getETAMessage(response)
				print("[*] Latest episode of \033[95m{}\033[0m is still not out. Waiting. \033[96m[ETA: {}h{}m]\033[0m".format(ETA[0], ETA[1], ETA[2]))
				config = readConfig()
				config["watchlist"][ETA[0]][1] = "-1"
				with open("../../data/config.json", 'w') as f:
					json.dump(config, f, indent=4)
