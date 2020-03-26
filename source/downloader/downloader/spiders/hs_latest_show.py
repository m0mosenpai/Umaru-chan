import scrapy
import json

links = []

class HSlatestShow(scrapy.Spider):
	name = 'hslatest'
	start_urls = ["https://horriblesubs.info/current-season/"]

	def parse(self, response):
		data = {}
		season_shows = []
		global links

		with open('../../data/data.json', 'r') as f:
			data = json.load(f)
			season_shows = data["current_season"]

		#go through every show and get latest ep num
		latest_num = {}
		for show in season_shows:
			#print(show)
			links.append(response.xpath('//a[@title="'+ show +'"]/@href').extract())

		# print(links[0][0])
		# home = "https://horriblesubs.info/"
		# link = home + links[0][0]
		nyaa = "https://nyaa.si/?f=0&c=0_0&q=horriblesubs+"
		name = "Boku no hero academia".replace(' ', '+')
		show = nyaa + name + "+1080p"
		yield scrapy.Request(show, callback = self.parse_show)
		#for link in links:

	def parse_show(self, response):
		latest_ep = response.xpath('//tr/td[@colspan="2"]/a/@title').extract()[1]
		#Check if latest_ep episode number is 1 greater than last downloaded, if yes, download it.
		magnet_link = response.xpath('//tr/td[@class="text-center"]/a/@href').extract()[1]
		print(magnet_link)
		print(latest_ep)	