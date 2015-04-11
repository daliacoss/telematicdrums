import requests, sys

def listen_forever(url):
	while True:
		response = requests.get(url)
		print response.json()

listen_forever(sys.argv[1])

