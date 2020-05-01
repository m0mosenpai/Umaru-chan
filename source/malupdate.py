import requests

#Constan request headers
REQUEST_HEADERS = {
	"Host": "api.myanimelist.net",
	"Accept": "application/json",
	"Content-Type": "application/x-www-form-urlencoded",
	"X-MAL-Client-ID": "6114d00ca681b7701d1e15fe11a4987e",
	"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"
}

class User:
	def login(user, passwd):
		URL = "https://api.myanimelist.net/v2/auth/token"
		headers= {
		    "Host": "api.myanimelist.net",
		    "Accept": "application/json",
		    "Content-Type": "application/x-www-form-urlencoded",
		    "X-MAL-Client-ID": "6114d00ca681b7701d1e15fe11a4987e",
		    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
		    "Content-Length": "112",
		}
		data = "grant_type=password&client_id=6114d00ca681b7701d1e15fe11a4987e&password={}&username={}".format(passwd, user)
		
		loginData = requests.post(URL, data = data, headers= headers).json()
		return loginData	

	#Re-authenticate session if Access Token expires (30 Days)
	#Probably won't need this in most use cases
	def reAuthenticate(refreshToken):
		URL = "https://myanimelist.net/v1/oauth2/token"
		headers= {
		    "Host": "myanimelist.net",
		    "Accept": "application/json",
		    "Content-Type": "application/x-www-form-urlencoded",
		    "X-MAL-Client-ID": "6114d00ca681b7701d1e15fe11a4987e",
		    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
		    "Content-Length": "88",
		}
		data = "client_id=6114d00ca681b7701d1e15fe11a4987e&grant_type=refresh_token&refresh_token={}".format(refreshToken)
		
		loginData = requests.post(URL, data = data, headers = headers).json()
		return loginData

	#Gets user's watchlist - status can be watching, completed, on_hold, dropped, plan_to_watch
	#Fields can have multiple options.	
	def getAnimeList(ACCESS_TOKEN, status, fields=[]):
		if not fields:
			URL = "https://api.myanimelist.net/v2/users/@me/animelist?status={}".format(status)
		else:
			query = "&fields="
			for field in fields:
				query += (field + ",")
			URL = "https://api.myanimelist.net/v2/users/@me/animelist?status={}".format(status) + query[:-1]

		headers = REQUEST_HEADERS
		headers["Authorization"] = "Bearer {}".format(ACCESS_TOKEN)

		animeList = requests.get(URL, headers = headers).json()
		return animeList

	#Changes values of fields as per arguments
	def updateList(ACCESS_TOKEN, id, myListFields, values):
		URL = "https://api.myanimelist.net/v2/anime/{}/my_list_status".format(id)

		headers = REQUEST_HEADERS
		headers["Authorization"] = "Bearer {}".format(ACCESS_TOKEN)

		data = ""
		for i,field in enumerate(myListFields):
			data += "{}={}&".format(field, values[i])
		updatedList = requests.put(URL, data = data[:-1], headers = headers).json()

		return updatedList

#Class to update watchlist on MAL
class Anime:
	#Search anime in search field of MAL	
	def search(ACCESS_TOKEN, aname, fields=[]):
		aname = aname.replace(' ', '+')
		if not fields:
			URL = "https://api.myanimelist.net/v2/anime?q={}".format(aname)
		else:
			query = "&fields="
			for field in fields:
				query += (field + ",")
			URL = "https://api.myanimelist.net/v2/anime?q={}".format(aname) + query[:-1]
	
		headers = REQUEST_HEADERS
		headers["Authorization"] = "Bearer {}".format(ACCESS_TOKEN)

		searchResults = requests.get(URL + query, headers = headers).json()
		return searchResults

def main():
	print("This function of the script is still in progress!")

if __name__ == "__main__":
	main()