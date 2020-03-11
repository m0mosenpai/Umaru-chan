#A simple script that automatically downloads anime from HorribleSubs based on user's schedule and selected anime of choice.
import scrapy
from ..items import ScheduleTimeItem, CurrentTimeItem, CurrentSeasonItem

#Globals
running = True
watchlist = []
malID = "https://myanimelist.net/animelist/Momo_Senpai"
lib_path = "/media/bitlockermount/Users/sarth/Documents/Anime"

print("1. Set up/Update Watchlist")
print("2. Show Status")
print("3. Exit")

class animeDownloader(scrapy.Spider):
	name = 'anime'
	start_urls = [
		"https://horriblesubs.info/"
	]

	#Function to parse time inside iframe	
	def parse_time(self, response):
		items = CurrentTimeItem()
		yield {
				'current_time': response.xpath('//tr/td/a/span/text()').extract_first()
			}

	#Functino to parse current season list
	def parse_season(self, response):
		items = CurrentSeasonItem()
		yield {
				'current_season': response.xpath('//div[@class="ind-show"]/a/text()').extract()
		}


	#Function to parse schedule and time of shows	
	def parse(self, response):
		items = ScheduleTimeItem()

		#Get current time
		time_url = response.xpath('//iframe/@src').extract_first()
		yield scrapy.Request(time_url, callback = self.parse_time)

		#Get Schedule for the day
		schedule = response.xpath('//table[@class="schedule-table"]/tr/td/a/text()').extract()
		release_time = response.xpath('//table[@class="schedule-table"]/tr/td/text()').extract() 
		yield { 
			'timetable': list(zip(schedule, release_time))
			}

		#Get Current Season
		season = response.xpath('//ul/li/a[@title="Shows airing this season"]/@href').extract_first()
		yield scrapy.Request(season, callback = self.parse_season)

# #Shows info like time to next episode, downloaded episodes etc.
# def showStatus():
# 	print("Current Status: ")

# #Sets up Watchlist according to user
# def setWatchlist():
# 	if not watching:
# 		print("Watchlist is empty")
# 	else:
# 		print("Your Watchlist: ")
# 		print(watching)

# 	print("Enter the shows you want to watch this season: (q to quit)")
# 	while choose != q:
# 		choose = input()
# 		watching.append(choose)

'''
while running != False:

	class animeDownloader(scrapy.Spider):
		name = "anime"
		start_url = [
			'https://horriblesubs.info/shows/'
		]

		def parse(self, response):
'''

