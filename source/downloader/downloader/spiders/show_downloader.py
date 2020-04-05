import scrapy
import urllib.request
import ssl
import colorama
import json
import sys

ssl._create_default_https_context = ssl._create_unverified_context
colorama.init()

#Reads config
def readConfig():
	with open('../../data/config.json', 'r') as f:
		config = json.load(f)
	return config

#Reads queue
def readQueue():
	with open('../../tmp/tmp_queue.json', 'r') as f:
		queue = json.load(f)
	return queue

query = ""
page = 1
config = readConfig()
path = config["main"]["torrent"]
quality = config["main"]["quality"]
queue = readQueue()

class DownloadShow(scrapy.Spider):
	name = 'show'
	start_urls = ["https://nyaa.si/"]

	def parse(self, response):
		global query

		aname = queue[0]
		start = int(queue[1])
		end = int(queue[2])
		head = "https://nyaa.si/?f=0&c=0_0&q=horriblesubs+"
		name = aname.replace(' ', '+')
		tail = "+" + quality + "+" + "mkv" + "&p="
		query = head + name + tail

		yield scrapy.Request(query, callback = self.parse_show, meta={'start':start, 'end':end})

	def parse_show(self, response):
		global page
		print("\033[93m[*] Page: {}\033[0m".format(page))		

		start = response.meta.get('start')
		end = response.meta.get('end')
		episodes = response.xpath('//td[@colspan="2"]/a[not(@class)]/@title').extract()
		if not episodes:
			print("\033[93m[*] No other relevant episode found.\033[0m")
			print("\033[92m[*] All done!\033[0m")
			return
		
		for ep in episodes:
			try:
				epno = int(ep[ep.index('- '):ep.index(' [')][2:])
				aname = ep[ep.index('] '):ep.index(' -')][2:]
			except:
				print("\033[91m[-] Extra/OVA/Unreadable Episode Found. Ignoring.\033[0m")
				continue
			if epno <= end and epno >= start:
				url = "https://nyaa.si"
				body = response.xpath('//a[contains(text(), "- ' + f'{epno:02}' +'")]/../following-sibling::td[1]/a/@href').extract()
				url += body[0]
				print("[*] Found new episode: \033[95m{} [{}] - {}\033[0m".format(epno, quality, aname))
				urllib.request.urlretrieve(url, path + aname + " " + str(epno) + " [{}].torrent".format(quality))
				print("\033[92m[+] Downloaded!\033[0m")

		page += 1
		return scrapy.Request(query + str(page), callback = self.parse_show, meta={'start': start, 'end': end})