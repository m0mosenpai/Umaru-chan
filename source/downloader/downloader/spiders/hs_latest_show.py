import scrapy
import platform
import json
import urllib.request
import ssl
import time
import colorama

ssl._create_default_https_context = ssl._create_unverified_context
colorama.init()

links = []
queue = {}
path = ""
quality=""

#Reads config file
def readConfig():
	with open("../../data/config.json", 'r+') as f:
		config = json.load(f)
	return config

#Reads tmp queue file
def readQueue():
	with open("../../tmp/tmp_queue.json", "r") as f:
		queue = json.load(f)
	return queue	

class HSlatestShow(scrapy.Spider):
	name = 'hslatest'
	start_urls = ["https://nyaa.si/"]

	def parse(self, response):
		global queue
		global path
		global quality
		
		config = readConfig()
		queue = readQueue()
		path = config["main"]["torrent"]
		
		#Check for a trailing slash based on platform
		if platform.system() == "Linux":
			if path[-1] != "/":
				path = path + "/"
		if platform.system() == "Windows":
			if path[-1] != "\\":
				path = path + "\\"

		quality = config["main"]["quality"]

		for show in queue.keys():
			head = "https://nyaa.si/?f=0&c=0_0&q=horriblesubs+"
			tail = "+" + quality + "&p="
			name = show.replace(' ', '+')
			show = head + name + tail
			yield scrapy.Request(show, callback = self.parse_show)

	def parse_show(self, response):
		#Get the latest episode of the anime
		latest_ep = response.xpath('//td[@colspan="2"]/a[not(@class)]/@title').extract()[0]
		magnet_link = response.xpath('//td[@class="text-center"]/a/@href').extract()[1]
		aname = (latest_ep[latest_ep.index('] '):latest_ep.index(' -')][2:])
		epno = (latest_ep[latest_ep.index('- '):latest_ep.index(' [')][2:])
		print("\033[93m[*] Checking for new episode: {}\033[0m".format(aname))

		currentep = int(queue[aname])
		for i in range(currentep+1, int(epno) + 1): #ep no in config is the last downloaded ep
			link = "https://nyaa.si"
			link += response.xpath('//a[contains(text(), "- ' + f'{i:02}' +'")]/../following-sibling::td[1]/a/@href').extract()[0]
			print("[*] Found new episode: \033[95m{} [{}] - {}\033[0m".format(i, quality, aname))
			urllib.request.urlretrieve(link, path + aname + str(i) + " [{}].torrent".format(quality))
			print("\033[92m[+] Downloaded!\033[0m")

		#Update config with latest downloaded episode and time stamp	
		config = readConfig()
		config["watchlist"][aname][0] = epno
		config["watchlist"][aname][1] = str(time.time())
		with open("../../data/config.json", 'w') as f:
			json.dump(config, f, indent=4)