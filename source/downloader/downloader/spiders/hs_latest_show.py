import scrapy
import json
import urllib.request

links = []
watchlist = {}
path = ""

class HSlatestShow(scrapy.Spider):
	name = 'hslatest'
	start_urls = ["https://nyaa.si/"]

	def parse(self, response):
		global watchlist
		global path
		# data = {}
		# season_shows = []
		# global links

		# with open('../../data/data.json', 'r') as f:
		# 	data = json.load(f)
		# 	season_shows = data["current_season"]

		# #go through every show and get latest ep num
		# for show in season_shows:
		# 	#print(show)
		# 	links.append(response.xpath('//a[@title="'+ show +'"]/@href').extract())
		pageno = 1

		with open("../../data/config.json", 'r+') as f:
			config = json.load(f)
			watchlist = config['watchlist']

		path = config["main"]["path"]

		for show in watchlist:
			# print(links[0][0])
			# home = "https://horriblesubs.info/"
			# link = home + links[0][0]
			nyaa = "https://nyaa.si/?f=0&c=0_0&q=horriblesubs+"
			name = show.replace(' ', '+')
			show = nyaa + name + "+1080p"
			yield scrapy.Request(show, callback = self.parse_show)

		#download eps


	def parse_show(self, response):
		latest_ep = response.xpath('//td[@colspan="2"]/a[not(@class)]/@title').extract()[0]
		#print("|{}|".format(latest_ep))
		magnet_link = response.xpath('//td[@class="text-center"]/a/@href').extract()[1]
		#print(magnet_link)
		aname = (latest_ep[latest_ep.index('] '):latest_ep.index(' -')][2:])
		epno = (latest_ep[latest_ep.index('- '):latest_ep.index(' [')][2:])

		#print("Latest episode of {} is {}".format(aname, epno))

		currentep = int(watchlist[aname])
		for i in range(currentep+1, int(epno) + 1): #ep no in config is the last downloaded ep
			link = "https://nyaa.si"
			link += response.xpath('//a[contains(text(), "- ' + f'{i:02}' +'")]/../following-sibling::td[1]/a/@href').extract()[0]
			#print(response.xpath('//a[contains(text(), "' + f'{i:02}' +'")]/../following-sibling::td[1]/a/@href').extract()[0])
			print("Found new episode({}) for {}".format(i, aname))
			urllib.request.urlretrieve(link, path + aname + str(i) + ".torrent")
			print("Downloaded!")

		with open("../../data/config.json", "r+") as f:
			config = json.load(f)
			config["watchlist"][aname] = epno
			f.seek(0)
			json.dump(config, f, indent=4)
