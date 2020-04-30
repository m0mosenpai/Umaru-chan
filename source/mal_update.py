import colorama
import json
import requests
import os

colorama.init()

#Class to login to MyAnimeList
class Login:
	def __init__(self, user, passwd):
		#Login and get Access Token (Expires in 60 Minutes)
		self.loginInfo = self.loginMAL(user, passwd)
		self.accessToken = self.loginInfo["access_token"]

	#Re-authenticate session if Refresh Token expires (30 Days)
	def reAuthenticate(self, refreshToken):
		self.URL = "https://myanimelist.net/v1/oauth2/token"
		self.headers= {
		    "Host": "myanimelist.net",
		    "Accept": "application/json",
		    "Content-Type": "application/x-www-form-urlencoded",
		    "X-MAL-Client-ID": "6114d00ca681b7701d1e15fe11a4987e",
		    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
		    "Content-Length": "88",
		}
		self.data = "client_id=6114d00ca681b7701d1e15fe11a4987e&grant_type=refresh_token&refresh_token={}".format(refreshToken)
		
		self.login = requests.post(self.URL, data = self.data, headers = self.headers).json()

	#Fresh login - get new Access and Refresh Token
	def loginMAL(self, user, passwd):
		self.URL = "https://api.myanimelist.net/v2/auth/token"
		self.headers= {
		    "Host": "api.myanimelist.net",
		    "Accept": "application/json",
		    "Content-Type": "application/x-www-form-urlencoded",
		    "X-MAL-Client-ID": "6114d00ca681b7701d1e15fe11a4987e",
		    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
		    "Content-Length": "112",
		}
		self.data = "grant_type=password&client_id=6114d00ca681b7701d1e15fe11a4987e&password={}&username={}".format(passwd, user)
		
		self.login = requests.post(self.URL, data = self.data, headers= self.headers).json()

		for key in self.login.keys():
			if key == "error":
				print("Login Failed.")
				print("Error Message: {}".format(self.login['message']))
				return

		with open("tmp/tmp_login.json", 'w+') as f:
			json.dump(self.login, f, indent=4)

		return self.login

#Class to update watchlist on MAL
class UpdateList:
	def __init__(self, user, passwd, aname):
		loginObj = Login(user, passwd)
		self.search(aname, loginObj.accessToken)

	#Search anime in search field of MAL	
	def search(self, aname, accessToken):
		self.URL = "https://api.myanimelist.net/v2/anime"
		self.headers={
			"Host": "api.myanimelist.net",
			"Accept": "application/json",
			"Content-Type": "application/x-www-form-urlencoded",
			"X-MAL-Client-ID": "6114d00ca681b7701d1e15fe11a4987e",
		    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
		    "Authorization": "Bearer {}".format(accessToken)
		}
		self.aname = aname.replace(' ', '+')
		self.query = "?q={}&fields=alternative_titles,id,my_list_status".format(self.aname)
		self.searchResults = requests.get(self.URL + self.query, headers = self.headers).json()
		self.id = self.searchResults['data'][0]['node']['id']
		self.epWatched = self.searchResults['data'][0]['node']['my_list_status']['num_episodes_watched']
		self.update(self.headers, self.id, self.epWatched)

	#Updates watched value by 1	
	def update(self, headers, id, epWatched):
		self.URL = "https://api.myanimelist.net/v2/anime/{}/my_list_status".format(id)
		self.headers = headers
		self.data = "num_watched_episodes={}".format(int(epWatched) + 1)

		self.updateResponse = requests.put(self.URL, data = self.data, headers = self.headers).json()
		print(self.updateResponse)


def main():
	print("This function of the script is still in progress!")

if __name__ == "__main__":
	main()