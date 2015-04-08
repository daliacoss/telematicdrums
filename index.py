from flask import Flask, render_template, request
from flask_restful import Api, Resource, reqparse
from flask.ext.socketio import SocketIO
import json, time

app = Flask(__name__)
api = Api(app)
socketIO = SocketIO(app)

sequencerData = {
	"sequence":[
		[1,0,1,0,1,1,1,0],
		[0,0,1,0,0,0,1,0],
		[1,1,1,1,1,1,1,1],
		[0,0,1,0,1,1,0,0],
	],
	"tempo":100,
}

edited = False

class HelloWorld(Resource):

	def get(self):

		i = 0
		global edited
		# while sequencerData["tempo"] == 100:
		while not edited:
			# keep connection alive for 10 seconds
			if i > 200:
				return {"message": "timeout"}
			time.sleep(.05)
			i += 1

		edited = False
		return {"message": "success", "data": sequencerData}

	def post(self):

		# sequencerData["sequence"][0][0] += 1
		# sequencerData["tempo"] = 120
		# parser = reqparse.RequestParser()
		# parser.add_argument('sequence', type=list)
		# args = parser.parse_args()

		sequence = [[] for channel in sequencerData["sequence"]]

		for i, origChannel in enumerate(sequencerData["sequence"]):
			channel = request.form.getlist("sequence[%d][]" % i)
			print channel
			if not channel:
				return {"msg":"failed: not enough channels in sequence"}, 400
			elif len(channel) != len(origChannel):
				return {"msg":"failed: wrong number of notes in channel"}, 400

			for j, note in enumerate(channel):
				try:
					sequence[i].append(int(note))
				except TypeError, ValueError:
					return {"msg":"failed: invalid note value"}, 400

		print sequence
		sequencerData["sequence"] = sequence 

		global edited
		edited = True

		# return {"msg": "success", "data":sequence}
		return {"msg": "success"}

api.add_resource(HelloWorld, '/trigger', methods=["GET", "POST"])

@app.route("/")
def index():
    return render_template('index.html',)

# @socketIO.on('my event')
# def handle_source(json_data):
#     text = json_data["message"]#['message'].encode('ascii', 'ignore')
#     socketIO.emit('echo', {'echo': 'Server Says: '+text+'!'}, True)
#     print text

if __name__ == "__main__":
    app.run(debug=True)