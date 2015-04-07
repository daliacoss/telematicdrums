from socketIO_client import SocketIO, LoggingNamespace

def on_aaa_response(*args):
	print('on_aaa_response', args)

socketIO = SocketIO('localhost', 5000)
# socketIO.on('aaa_response', on_aaa_response)
# socketIO.emit('aaa')
# socketIO.wait(seconds=1)