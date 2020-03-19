from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import secrets
from time import sleep

class animelist():
	def __init__(self):
		chrome_options = Options()
		#chrome_options.add_argument("--headless")
		self.driver = webdriver.Chrome(chrome_options=chrome_options)
		self.driver.maximize_window()

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
		try:
			self.driver.get('https://myanimelist.net/animelist/{}'.format(secrets._id))
		except Exception:
			pass
		sleep(3)
		self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
		anime_elem = self.driver.find_element_by_xpath("//tr[contains(text(), animename)]")
		anime_elem.click()
		print(anime_elem)

	def updateanime(self):
		self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
		btn = self.driver.find_element_by_class_name("""//*[@id="list-container"]/div[3]/div/table/tbody[1]/tr[0]/td[6]/div/a/i""")
		btn.click()


bot = animelist()
bot.login()
bot.gotoanime(animename='Ahiru no Sora')