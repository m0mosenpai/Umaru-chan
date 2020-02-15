#A simple script that automatically downloads anime from HorribleSubs based on user's schedule and selected anime of choice.
import scrapy

lib_path = "/media/bitlockermount/Users/sarth/Documents/Anime"
watching = []
running = True

print("What to do?")
print("1. Set up/Update Watchlist")
print("2. Show Status")
print("3. Exit")

#Shows info like time to next episode, downloaded episodes etc.
def showStatus():
	print("Current Status: ")

#Sets up Watchlist according to user
def setWatchlist():
	if not watching:
		print("Watchlist is empty")
	else:
		print("Your Watchlist: ")
		print(watching)

	print("Enter the shows you want to watch this season: (q to quit)")
	while choose != q:
		choose = input()

'''
while running != False:

	class animeDownloader(scrapy.Spider):
		name = "anime"
		start_url = [
			'https://horriblesubs.info/shows/'
		]

		def parse(self, response):
'''

