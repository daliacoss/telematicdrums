import rtmidi, pickle, sys, time

noteOn = (lambda channel, pitch, velocity=127: (143+channel, pitch, velocity))
NOTE_VALUES = [60, 48, 60, 60]

def playLoop():

	device = rtmidi.MidiOut()
	device.open_virtual_port("PyCon Drum Machine")

	try:
		while True:
			with open("seq.p") as seqFile:
				data = pickle.load(seqFile)

			sequence = data["sequencerData"]["sequence"]
			tempo = data["sequencerData"]["tempo"]
			eighth = 30./tempo
			
			#for each position
			for i in range(len(sequence[0])):
				#for each channel
				for j, channel in enumerate(sequence):
					# print i, j
					device.send_message(noteOn(j+1, NOTE_VALUES[j]*channel[i]))
				time.sleep(eighth)
	except KeyboardInterrupt:
		device.close_port()

playLoop()
