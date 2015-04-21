from __future__ import print_function
from flask import Flask, render_template, request, redirect, abort
from flask_restful import Api, Resource, reqparse
# from flask.ext.socketio import SocketIO
from flask.ext.sqlalchemy import SQLAlchemy
import time, datetime, os, random, string

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")

db = SQLAlchemy(app)
# socketIO = SocketIO(app)

LEN_SEQUENCE = 8
NUM_CHANNELS = 4
MAX_LISTEN_TIMEDELTA = 10

class Session(db.Model):
	__tablename__ = "sessions"

	id = db.Column(db.Integer, primary_key=True)
	key = db.Column(db.String(7), index=True)
	listening = db.Column(db.Integer)
	edited = db.Column(db.Integer)
	last_listen = db.Column(db.DateTime)

	def __init__(self, key):
		self.key = key
		self.listening = 0
		self.edited = 0

class SequenceNote(db.Model):
	__tablename__ = "sequence_notes"

	id = db.Column(db.Integer, primary_key=True)
	session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"))
	channel_id = db.Column(db.Integer)
	position = db.Column(db.Integer)
	value = db.Column(db.Integer)

	def __init__(self, session_id, channel_id, position, value=0):
		self.session_id = session_id
		self.channel_id = channel_id
		self.value = value
		self.position = position

class Sequence(db.Model):
	__tablename__ = "sequences"

	id = db.Column(db.Integer, primary_key=True)
	session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"))
	tempo = db.Column(db.Integer)

	def __init__(self, tempo, session_id):
		self.session_id = session_id
		self.tempo = tempo

class SequenceEventListener(Resource):

	def get(self, session_key):

		session = db.session.query(Session).filter(Session.key==session_key).one()
		sequence = db.session.query(Sequence).filter(Sequence.session_id==session.id).one()

		if not session:
			return {"message": "failed: session does not exist"}, 404
		# elif (
		# 	session.listening and
		# 	session.last_listen and
		# 	(datetime.datetime.utcnow() - session.last_listen).seconds < MAX_LISTEN_TIMEDELTA
		# ):
		# 	return {"message": "failed: exceeded max number of listeners"}, 408

		session.listening += 1
		session.last_listen = datetime.datetime.utcnow()
		db.session.commit()

		i = 0

		while not session.edited:
			# keep connection alive for 10 seconds
			if i >= 200:
				#this line should be reached even if disconnect occurs
				session.listening -= 1
				db.session.commit()
				return {"message": "timeout"}
			time.sleep(.05)
			i += 1
			db.session.refresh(session)

		#subtracting 1 from edited instead of setting edited to 0 prevents us from interfering with other listeners
		session.edited -= 1
		session.listening -= 1

		seq = getSequence(session.id)
		db.session.commit()
		return {"message": "success", "data": {"sequence":seq,"tempo":sequence.tempo}, "session_key": session_key}

class SequenceEventTrigger(Resource):

	def post(self, session_key):

		session = db.session.query(Session).filter(Session.key==session_key).one()
		if not session:
			return {"message": "failed: session does not exist"}, 404
		sequence = getSequence(session.id)
		sequenceObject = db.session.query(Sequence).filter(Sequence.session_id==session.id).one()

		#for each channel
		for i in range(NUM_CHANNELS):
			channel = request.form.getlist("sequence[%d][]" % i)
			if not channel:
				return {"msg":"failed: not enough channels in sequence"}, 400
			elif len(channel) != LEN_SEQUENCE:
				return {"msg":"failed: wrong number of notes in channel"}, 400

			#for each note
			for j, note in enumerate(channel):
				try:
					sequence[i][j] = int(note)
				except TypeError, ValueError:
					return {"msg":"failed: invalid note value"}, 400

		modifySequence(session.id, sequence)

		#if there are no current listeners, then the first listener to arrive gets to see the edit
		session.edited = session.listening or 1
		tempo = int(request.form.get("tempo"))
		sequenceObject.tempo = tempo
		db.session.commit()

		return {"msg": "success"}

api.add_resource(SequenceEventTrigger, '/trigger/<string:session_key>', methods=["POST"])
api.add_resource(SequenceEventListener, '/listen/<string:session_key>', methods=["GET"])

def createSequence(session_id):
	"""create a collection of SequenceNotes to be added to the database"""

	sequence = []
	for i in range(LEN_SEQUENCE):
		for j in range(NUM_CHANNELS):
			sequence.append(SequenceNote(session_id, channel_id=j, position=i))

	return sequence

def getSequence(session_id):

	query = db.session.query(SequenceNote)\
		.filter(SequenceNote.session_id==session_id)
		# .order_by(SequenceNote.position)

	sequence = [
		[
			x.value for x in query.filter(SequenceNote.channel_id==i).order_by(SequenceNote.position).all()
		] for i in range(NUM_CHANNELS)
	]
	return sequence

def modifySequence(session_id, newSequence):

	q = db.session.query(SequenceNote).filter(SequenceNote.session_id==session_id)
	for i, channel in enumerate(newSequence):
		qc = q.filter(SequenceNote.channel_id==i)
		for j, noteVal in enumerate(channel):
			note = qc.filter(SequenceNote.position==j).one()
			note.value = noteVal
			db.session.commit()

@app.route("/")
def index():
	key = ''.join(random.SystemRandom().choice(string.lowercase+string.digits+string.uppercase) for _ in xrange(7))
	return redirect("/" + key)

@app.route("/<string:session_key>")
def player(session_key):
	if type(session_key) not in (str, unicode) or len(session_key) != 7:
		return abort(400, "Session key must be 7-character string")

	session = db.session.query(Session).filter(Session.key==session_key).first()
	if not session:
		session = Session(key=session_key)

		db.session.add(session)
		db.session.commit()

		#we wait until after we've added the session, so it has an ID
		sequence = createSequence(session.id)
		[db.session.add(note) for note in sequence]
		db.session.commit()

	#even if we've created a sequence, we want it in a nested format
	sequence = getSequence(session.id)

	sequenceObject = db.session.query(Sequence).filter(Sequence.session_id==session.id).first()
	if not sequenceObject:
		sequenceObject = Sequence(100, session.id)
		db.session.add(sequenceObject)
		db.session.commit()

	return render_template('index.html', session_key=session_key, sequence=sequence, tempo=sequenceObject.tempo)

# @socketIO.on('my event')
# def handle_source(json_data):
#     text = json_data["message"]#['message'].encode('ascii', 'ignore')
#     socketIO.emit('echo', {'echo': 'Server Says: '+text+'!'}, True)
#     print text

if __name__ == "__main__":
    app.run(debug=True)