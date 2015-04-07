from socketIO_client import SocketIO, LoggingNamespace
from flask.ext.socketio import test_client

def on_aaa_response(*args):
	print('on_aaa_response', args)

import requests
requests.packages.urllib3.disable_warnings()

socketIO = SocketIO('localhost', 5000)
# socketIO.on('aaa_response', on_aaa_response)
# socketIO.emit('aaa')
# socketIO.wait(seconds=1)