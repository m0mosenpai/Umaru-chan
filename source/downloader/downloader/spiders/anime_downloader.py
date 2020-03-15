#A simple script that automatically downloads anime from HorribleSubs based on user's schedule and selected anime of choice.
import scrapy
from ..items import ScheduleTimeItem, CurrentSeasonItem, AllShowsItem

class animeDownloader(scrapy.Spider):
	name = 'anime'
	start_urls = [
		"https://horriblesubs.info/"
	]

	#Function to parse current season list
	def parse_season(self, response):
		items = CurrentSeasonItem()
		items['current_season'] = response.xpath('//div[@class="ind-show"]/a/text()').extract()
		yield items

	#Function to parse all shows
	def parse_allshows(self, response):
		items = AllShowsItem()
		#items['all_shows'] = {}
		shows_url = response.xpath('//div[@class="ind-show"]/a/@href').extract()
		shows = response.xpath('//div[@class="ind-show"]/a/@title').extract()

		items['all_shows'] = dict(zip(shows, shows_url))
		
		# for show in shows:
		# 	if show[0] not in items['all_shows'].keys():
		# 		items['all_shows'][show[0].upper()] = [show]
		# 	else:
		# 		items['all_shows'][show[0].upper()].append(show)	
		yield items

		#TO-DO
		#Get a particular show

	#Function to parse schedule and time of shows	
	def parse(self, response):
		items = ScheduleTimeItem()

		#Get Schedule for the day
		schedule = response.xpath('//table[@class="schedule-table"]/tr/td/a/text()').extract()
		release_time = response.xpath('//table[@class="schedule-table"]/tr/td/text()').extract()  
		items['timetable'] = dict(zip(schedule, release_time))
		yield items

		#Get Current Season
		season = response.xpath('//ul/li/a[@title="Shows airing this season"]/@href').extract_first()
		yield scrapy.Request(season, callback = self.parse_season)

		#Get all shows
		all_shows = response.xpath('//ul/li/a[@title="All shows"]/@href').extract_first()
		yield scrapy.Request(all_shows, callback = self.parse_allshows)


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