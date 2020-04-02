#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import json
import sys
import fuzzyset

#global
RETRIES = 10

class animelist():
	def __init__(self):
		chrome_options = Options()
		#chrome_options.add_argument("--headless")
		self.driver = webdriver.Chrome(chrome_options=chrome_options)
		self.driver.maximize_window()

		print('command_executor: ' + self.driver.command_executor._url)
		print('session_id: ' + self.driver.session_id)

	def login(self, _id, _pass):
		self.driver.get("https://myanimelist.net/login.php?")
		sleep(5)

		email = self.driver.find_element_by_xpath("""//*[@id="loginUserName"]""")
		email.send_keys(_id)

		password = self.driver.find_element_by_xpath("""//*[@id="login-password"]""")
		password.send_keys(_pass)

		sleep(2)

		btn = self.driver.find_element_by_xpath("""//*[@id="dialog"]/tbody/tr/td/form/div/p[6]/input""")
		btn.click()

	def gotoanime(self, animename, _id):
		#f.get(animename)
		try:
			self.driver.get('https://myanimelist.net/animelist/{}?status=1&tag='.format(_id))
		except Exception:
			pass
		sleep(2)

		#fuzzy set
		correct = fuzzyset.FuzzySet()
		anames = self.driver.find_elements_by_xpath("""//a[@class="animetitle"]/span""")
		if len(anames) == 0:
			anames = self.driver.find_elements_by_xpath()
		print(anames)

		updated = False
		for r in range(RETRIES) or updated is False:
			try:
				anilist = self.driver.find_element_by_xpath("""//tbody[@class="list-item"]""")
				# print(anilist)
				# exit()
				self.driver.execute_script("window.scrollTo(0, 100)") 
				anime_elem = self.driver.find_element_by_link_text(animename)
				anime_elem.click()
				updated = True
			except Exception:
				print("couldn't find")

	def updateanime(self):
		sleep(2)
		#self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
		for r in range(RETRIES) or btn is not None:
			try:
				btn = self.driver.find_element_by_class_name('js-anime-increment-episode-button')
				btn.click()
			except Exception:
				print("couldn't update")
#sets animename from command line argument
#arglist = sys.argv
#animename = arglist[1]
animename = 'Ahiru no Sora'

with open('data/config.json', 'r+') as f:
	config = json.load(f)
	user = config['main']['username']
	passwd = config['main']['password']

bot = animelist()
bot.login(user, passwd)
bot.gotoanime(animename, user)
bot.updateanime()