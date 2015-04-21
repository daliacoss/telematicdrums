from __future__ import print_function
import rtmidi, pickle, sys, time

noteOn = (lambda channel, pitch, velocity=127: (143+channel, pitch, velocity))
NOTE_VALUES = [60, 48, 60, 60]

def playLoop():

	device = rtmidi.MidiOut()
	device.open_virtual_port("Telematic Drum Machine")
	print("opened port \"Telematic Drum Machine\"")

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
		#flush all MIDI channels by sending noteOffs
		for i, channel in enumerate(sequence):
			device.send_message(noteOn(i+1, NOTE_VALUES[i], 0))
		device.close_port()

if __name__ == "__main__":
	playLoop()
