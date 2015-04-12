import requests, sys, pickle

def listenForever(url):

	print "connecting..."

	try:
		while True:
			saveApiResult(url)
	except KeyboardInterrupt:
		sys.exit()

def saveApiResult(url):

	response = requests.get(url)
	if response.status_code == 408:
		print "too many listeners; try again later"
		sys.exit(1)

	elif response.json().get("message") == "success":
		data = response.json().get("data")

		print data

		with open("seq.p", "w") as sf:
			pickle.dump({"sequencerData":{"sequence":data,"tempo":100}}, sf)

listenForever(sys.argv[1])
