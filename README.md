Telematic Drum Machine
======================
The Telematic Drum Machine is a toy web app that allows one to remotely play MIDI instruments from a web browser. It was created for the PyCon 2015 poster session as an interactive demonstration of Python's virtual MIDI capabilities.

TDM consists of a server side and a client side. The server side is a Flask app, and the client side consists of two scripts (listener.py and drummachine.py) that must be run concurrently. An instance of the server side is currently deployed on Heroku (http://telematicdrums.herokuapp.com), so you only have to run the client side yourself.

Requirements
------------
**Server and Client Sides**
* python 2.7
* setuptools 1.3.2+
* pip

**Server Side**
* all dependencies listed in requirements.txt
* OPTIONAL: foreman

**Client Side**
* all dependencies listed in requirements-client.txt
* a virtual MIDI driver (OSX 10.5+ and (possibly) Linux users already have one built-in; Windows users should use LoopBe1 or MIDI-OX)

Installation and Setup
----------------------
**Server Side**  
Skip this section if you would prefer to use the existing server side instance on Heroku (recommended).

Install dependencies: `pip install -r requirements.txt`

Run the app: The entrypoint for the web app is index.py. My personal setup is to run the app using Foreman with the command `foreman start`. Foreman will automatically configure itself using the included Procfile, as long as the command is run from the top directory of the project.

**Client Side**  
Install dependencies: `pip install -r requirements-client.txt`

Usage
-----
**Server Side**  
TDM can host many **sessions** simultaneously. To start a new session, simply visit the front page of the app (e.g., http://telematicdrums.herokuapp.com). You will be redirected to a new session with a unique URL that you can revisit later. Each change you make during a session is automatically saved, and the state of the session will persist between visits.

The web interface consists of a simple 8-step, 4-channel sequencer. Each row represents a channel and each column represents a step. The entire sequence can be considered one measure; thus, each column can be considered one 8th-note. Dark squares indicate active notes, and light squares indicate inactive notes. Clicking a square toggles whether the corresponding note is active. The tempo can be adjusted with the "Slower" and "Faster" buttons.

Underneath the sequencer, you should see a URL preceded by the words "listen on". This is the URL the client side will need to listen to your session.

**Client Side**  
From the command line, run `python listener.py <URL>`, where `<URL>` is the aforementioned "listen on" URL.

From a separate command line window, and from the same directory as listener.py, run `python drummachine.py`. This will open a virtual MIDI port and begin playing the sequence loop. drummachine.py checks for changes in the sequence at the beginning of every measure. Thus, any changes you make now will not be audible until the next measure.

Each sequence channel corresponds to an actual MIDI channel (1 through 4). The pitch value of a note-on message is unique to each channel and can be customized in the NOTE_VALUES array in drummachine.py.

Both processes will run presumably forever until they are manually killed, such as with Ctrl-C.
