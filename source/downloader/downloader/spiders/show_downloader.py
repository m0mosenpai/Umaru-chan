import scrapy
import urllib.request
import ssl
import colorama
import json
import sys
import os
import time
import re

ssl._create_default_https_context = ssl._create_unverified_context
colorama.init()

#Reads config
def readConfig():
	with open('../../data/config.json', 'r') as f:
		config = json.load(f)
	return config

#Reads queue
def readQueue():
	if not os.path.isdir("../../tmp"):
		os.mkdir("../../tmp")
	if not os.path.isfile("../../tmp/tmp_queue.json"):
		queue = {}
		with open("../../tmp/tmp_queue.json", "w+") as f:
			json.dump(queue, f, indent=4)

	with open('../../tmp/tmp_queue.json', 'r') as f:
		queue = json.load(f)
	return queue

#Download episode from episode list
def download(eplist):
	if not eplist:
		print("\033[91m[-] No relevant episode found!\033[0m")
		return

	for ep in reversed(eplist):
		print("[*] Downloading episode: \033[95m{} [{}] - {}\033[0m".format(ep[2], quality, ep[1]))
		urllib.request.urlretrieve(ep[0], path + ep[1] + " " + str(ep[2]) + " [{}].torrent".format(quality))
		print("\033[92m[+] Downloaded!\033[0m")

query = ""
page = 1
config = readConfig()
path = config["main"]["torrent"]
quality = config["main"]["quality"]
queue = readQueue()
eplist = []

class DownloadShow(scrapy.Spider):
	name = 'show'
	start_urls = ["https://nyaa.si/"]

	def parse(self, response):
		global query

		aname = queue[0]
		start = int(queue[1])
		end = int(queue[2])
		release = queue[3].replace(' ', '+')
		head = "https://nyaa.si/?f=0&c=0_0&q=" + release + "+"
		name = aname.replace(' ', '+')
		tail = "+" + quality + "+" + "mkv" + "&p="
		query = head + name + tail

		yield scrapy.Request(query, callback = self.parse_show, meta={'start':start, 'end':end})

	def parse_show(self, response):
		global page
		global eplist

		print("\033[93m[*] Searching on Page: {}\033[0m".format(page))
		time.sleep(1)		

		start = response.meta.get('start')
		end = response.meta.get('end')
		episodes = response.xpath('//td[@colspan="2"]/a[not(@class)]/@title').extract()

		#When no more episodes are found, download all in urldict
		if not episodes:
			print("\033[93m[*] Adding episodes to queue.\033[0m")
			time.sleep(2)

			download(eplist)
			print("\033[92m[*] All done!\033[0m")
			return
		
		for ep in episodes:
			try:
				#aname = ep[ep.index('] '):ep.index(' -')][2:]
				#epno = int(ep[ep.index('- '):ep.index(' [')][2:])
				aname = re.split("\]|\)|\[|\(", ep)[2].split('-')[0].replace('_', ' ').strip()
				epno = int(re.split("\]|\)|\[|\(", ep)[2].split('-')[1].strip())

			except:
				print("\033[91m[-] Extra/OVA/Unreadable Episode Found. Ignoring.\033[0m")
				continue

			if epno <= end and epno >= start:
				url = "https://nyaa.si"
				body = response.xpath('//a[contains(text(), "- ' + f'{epno:02}' +'")]/../following-sibling::td[1]/a/@href').extract()
				url += body[0]
				eplist.append([url, aname, epno])

		page += 1
		return scrapy.Request(query + str(page), callback = self.parse_show, meta={'start': start, 'end': end})