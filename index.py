from flask import Flask, render_template, request, redirect, abort
from flask_restful import Api, Resource, reqparse
from flask.ext.socketio import SocketIO
from flask.ext.sqlalchemy import SQLAlchemy
import time, os, random, string

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")

db = SQLAlchemy(app)
socketIO = SocketIO(app)

# sequencerData = {
# 	"sequence":[
# 		[1,0,1,0,1,1,1,0],
# 		[0,0,1,0,0,0,1,0],
# 		[1,1,1,1,1,1,1,1],
# 		[0,0,1,0,1,1,0,0],
# 	],
# 	"tempo":100,
# }

# edited = False

LEN_SEQUENCE = 8
NUM_CHANNELS = 4

class Session(db.Model):
	__tablename__ = "sessions"

	id = db.Column(db.Integer, primary_key=True)
	key = db.Column(db.String(7), index=True)
	listening = db.Column(db.Boolean)

	def __init__(self, key):
		self.key = key
		self.listening = False

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

class HelloWorld(Resource):

	def get(self, session_key):

		session = db.session.query(Session).filter(Session.key==session_key).all()
		if not session:
			return {"message": "failed: session does not exist"}, 404
		# global edited
		# i = 0

		# while not edited:
		# 	# keep connection alive for 10 seconds
		# 	if i > 200:
		# 		return {"message": "timeout"}
		# 	time.sleep(.05)
		# 	i += 1

		# edited = False
		return {"message": "success"}#, "data": sequencerData, "session_key": session_key}

	def post(self, session_key):

		# sequencerData["sequence"][0][0] += 1
		# sequencerData["tempo"] = 120
		# parser = reqparse.RequestParser()
		# parser.add_argument('sequence', type=list)
		# args = parser.parse_args()

		sequence = [list(channel) for channel in sequencerData["sequence"]]

		session = db.session.query(Session).filter(Session.key==session_key).all()
		if not session:
			return {"message": "failed: session does not exist"}, 404

		db.session.commit()

		# for i, origChannel in enumerate(sequencerData["sequence"]):
		# 	channel = request.form.getlist("sequence[%d][]" % i)
		# 	print channel
		# 	if not channel:
		# 		return {"msg":"failed: not enough channels in sequence"}, 400
		# 	elif len(channel) != len(origChannel):
		# 		return {"msg":"failed: wrong number of notes in channel"}, 400

		# 	for j, note in enumerate(channel):
		# 		try:
		# 			sequence[i][j] = int(note)
		# 		except TypeError, ValueError:
		# 			return {"msg":"failed: invalid note value"}, 400

		# sequencerData["sequence"] = sequence 

		global edited
		edited = True

		# return {"msg": "success", "data":sequence}
		return {"msg": "success"}

api.add_resource(HelloWorld, '/trigger/<string:session_key>', methods=["GET", "POST"])

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
	print sequence
	# print [(x.value, x.position) for x in sequence[0]]
	# print [(x.value, x.position) for x in sequence[1]]
	# print [(x.value, x.position) for x in sequence[2]]
	# print [(x.value, x.position) for x in sequence[3]]

	return render_template('index.html', session_key=session_key)

# @socketIO.on('my event')
# def handle_source(json_data):
#     text = json_data["message"]#['message'].encode('ascii', 'ignore')
#     socketIO.emit('echo', {'echo': 'Server Says: '+text+'!'}, True)
#     print text

if __name__ == "__main__":
    app.run(debug=True)