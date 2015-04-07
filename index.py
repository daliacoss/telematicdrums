from flask import Flask, render_template, request
from flask_restful import Api, Resource
from flask.ext.socketio import SocketIO
import json

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

class HelloWorld(Resource):

	def get(self):

		return sequencerData

	def post(self):

		sequencerData["sequence"][0][0] += 1
		return "ok"

api.add_resource(HelloWorld, '/trigger', methods=["GET", "POST"])

@app.route("/")
def index():
    return "hello"#render_template('index.html',)

# @socketIO.on('my event')
# def handle_source(json_data):
#     text = json_data["message"]#['message'].encode('ascii', 'ignore')
#     socketIO.emit('echo', {'echo': 'Server Says: '+text+'!'}, True)
#     print text

if __name__ == "__main__":
    app.run()