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

		#print(links)
		for link in links:
