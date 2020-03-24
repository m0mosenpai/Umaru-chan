#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import data.secrets as secrets
from time import sleep
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

	def login(self):
		self.driver.get("https://myanimelist.net/login.php?")
		sleep(5)

		email = self.driver.find_element_by_xpath("""//*[@id="loginUserName"]""")
		email.send_keys(secrets._id)

		password = self.driver.find_element_by_xpath("""//*[@id="login-password"]""")
		password.send_keys(secrets._pass)

		sleep(2)

		btn = self.driver.find_element_by_xpath("""//*[@id="dialog"]/tbody/tr/td/form/div/p[6]/input""")
		btn.click()

	def gotoanime(self, animename):
		#f.get(animename)
		try:
			self.driver.get('https://myanimelist.net/animelist/{}'.format(secrets._id))
		except Exception:
			pass
		sleep(2)

		for r in range(RETRIES) or anime_elem is not None:
			try:
				anilist = self.driver.find_element_by_xpath("""//tbody[@class="list-item"]""")
				# print(anilist)
				# exit()
				self.driver.execute_script("window.scrollTo(0, 100)") 
				anime_elem = self.driver.find_element_by_link_text(animename)
				anime_elem.click()
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
arglist = sys.argv
animename = arglist[1]

#Check if secrete.py contains login credentials
if secrets._id != '' and secrets._pass !='':
	bot = animelist()
	bot.login()
	bot.gotoanime(animename)
	bot.updateanime()
else:
	print("\033[91mMAL Login ID not set. Run client with '--mal-id <username> <password>' to set one up!\033[0m")
