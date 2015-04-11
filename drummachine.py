import rtmidi, pickle, sys, time

def playLoop():
	device = rtmidi.MidiOut()
	device.open_virtual_port("PyCon Drum Machine")
	while True:
		with open("seq.p") as seqFile:
			data = pickle.load(seqFile)
		sequence = data["sequencerData"]["sequence"]
		tempo = data["sequencerData"]["tempo"]
		#	time.sleep()

playLoop()
