#A simple script that automatically downloads anime from HorribleSubs based on user's schedule and selected anime of choice.
import scrapy
from ..items import DownloaderItem

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

	items = DownloaderItem()

	def parse(self, response):
		
		#Get current time
		time_url = response.css('iframe::attr(src)').extract()
		yield scrapy.Request(time_url[0], callback = self.parse_iframe)

		#Get Schedule for the day
		self.items['schedule'] = []
		showname = response.xpath('//h2/table[@class="schedule-table"]//td[@class="schedule-widget-show"/a/text()').extract()
		print(showname)

	#Function to parse time inside iframe	
	def parse_iframe(self, response):
		time = response.xpath('//tr/td/a/span/text()').extract_first()
		self.items['time'] = time


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

