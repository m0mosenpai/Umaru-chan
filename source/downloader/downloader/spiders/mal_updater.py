import scrapy
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser

class MalUpdater(scrapy.Spider):
	name = 'mal_updater'
	start_urls = ['https://myanimelist.net/login.php']

	def parse(self, response):
		open_in_browser(response)
		#token = response.xpath('//*[@name="csrf_token"]/@content').extract_first()
		print('Token: ' + token)

		#return FormRequest.from_response(response, formdata={'csrf_token': str(token), 'password': 'Kgggdkp@2609', 'user_name': 'butterMiner', 'cookie': '1', 'sublogin': 'Login', 'submit': '1'}, callback=self.crawl_list)

	def crawl_list(self, response):
		#open_in_browser(response)
		print(response.body)
