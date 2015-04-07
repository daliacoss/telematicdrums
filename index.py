from flask import Flask, render_template
from flask.ext.socketio import SocketIO
import json

app = Flask(__name__)
socketIO = SocketIO(app)
app.debug = True

@app.route("/")
def index():
    return render_template('index.html',)

@socketIO.on('my event')
def handle_source(json_data):
    text = json_data["message"]#['message'].encode('ascii', 'ignore')
    socketIO.emit('echo', {'echo': 'Server Says: '+text+'!'}, True)
    print text

if __name__ == "__main__":
    socketIO.run(app)