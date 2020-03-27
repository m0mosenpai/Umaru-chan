import scrapy
import json

links = []
latest_num = {}
watchlist = {}

class HSlatestShow(scrapy.Spider):
	name = 'hslatest'
	start_urls = ["https://nyaa.si/"]

	def parse(self, response):
		global watchlist
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
		global latest_num
		latest_ep = response.xpath('//tr/td[@colspan="2"]/a/@title').extract()[1]
		magnet_link = response.xpath('//tr/td[@class="text-center"]/a/@href').extract()[1]
		#print(magnet_link)
		aname = (latest_ep[latest_ep.index('] '):latest_ep.index(' -')][2:])
		epno = (latest_ep[latest_ep.index('- '):latest_ep.index(' [')][2:])

		currentep = watchlist[aname]
		for currentep in range(int(epno) + 1):
			magenet = response.xpath('//a[contains(text(), "' + currentep +'")]/../following-sibling::td[1]/a/@href').extract()[1]
			

		latest_num[aname] = epno
		#dump
		with open("../../data/latestnum.json", 'w') as f:
			json.dump(latest_num, f)