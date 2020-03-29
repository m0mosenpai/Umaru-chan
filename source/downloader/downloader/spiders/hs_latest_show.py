import scrapy
import json
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
links = []
watchlist = {}
path = ""
quality=""

#Reads config file
def readConfig():
	with open("../../data/config.json", 'r+') as f:
		config = json.load(f)
	return config

class HSlatestShow(scrapy.Spider):
	name = 'hslatest'
	start_urls = ["https://nyaa.si/"]

	def parse(self, response):
		global watchlist
		global path
		global quality
		
		config = readConfig()
		watchlist = config['watchlist']
		path = config["main"]["torrent"]
		quality = config["main"]["quality"]

		if path == "":
			print("\033[91mTorrent directory not set. Run with -t/--torrent <PATH> to set one up!\033[0m")

		for show in watchlist:
			head = "https://nyaa.si/?f=0&c=0_0&q=horriblesubs+"
			tail = "+" + quality + "&p="
			name = show.replace(' ', '+')
			show = head + name + tail
			yield scrapy.Request(show, callback = self.parse_show)

	def parse_show(self, response):
		latest_ep = response.xpath('//td[@colspan="2"]/a[not(@class)]/@title').extract()[0]
		magnet_link = response.xpath('//td[@class="text-center"]/a/@href').extract()[1]
		aname = (latest_ep[latest_ep.index('] '):latest_ep.index(' -')][2:])
		epno = (latest_ep[latest_ep.index('- '):latest_ep.index(' [')][2:])
		print("Checking new episode for {}".format(aname))
		#print("Latest episode of {} is {}".format(aname, epno))

		currentep = int(watchlist[aname])
		for i in range(currentep+1, int(epno) + 1): #ep no in config is the last downloaded ep
			link = "https://nyaa.si"
			link += response.xpath('//a[contains(text(), "- ' + f'{i:02}' +'")]/../following-sibling::td[1]/a/@href').extract()[0]
			print("Found new episode {} [{}] for {}".format(i, quality, aname))
			urllib.request.urlretrieve(link, path + aname + str(i) + " [{}].torrent".format(quality))
			print("Downloaded!")

		config = readConfig()
		config["watchlist"][aname] = epno
		with open("../../data/config.json", 'w') as f:
			json.dump(config, f, indent=4)

			
