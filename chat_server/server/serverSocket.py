import asyncio, json, argparse
from sys import stdout
        
class ChatServerProtocol(asyncio.Protocol):
	def __init__(self, connections, users):
		self.connections = connections
		self.users = users
		self.peername = ""
		self.user = None
		
		self.SERVER_NAME = "[Server]"
        
	def connection_made(self, transport):
		self.connections += [transport]
		self.peername = transport.get_extra_info('sockname')
		self.transport = transport

	def connection_lost(self, exc):
		if isinstance(exc, ConnectionResetError):
			self.connections.remove(self.transport)
		else:
			print(exc)
		err = "{}:{} disconnected".format(*self.peername)
		message = self.make_msg(err, self.SERVER_NAME)
		print(err)
		for connection in self.connections:
			connection.write(message)

	def data_received(self, data):
		if data:
			if not self.user:
				user = data.decode()
				if not user.isalpha():
					self.transport.write(self.make_msg("Your name must be alphanumeric!", self.SERVER_NAME))
					self.transport.close()
				else:
					self.user = data.decode()
					msg = '{} connected ({}:{})'.format(self.user, *self.peername)
					message = self.make_msg(msg, self.SERVER_NAME)
					self.output(msg)
                    
					for connection in self.connections:
						connection.write(message)
			else:
				message = data.decode()
				self.output(self.user + ": " + message)
				
				msg = self.make_msg(message, self.user)
				for connection in self.connections:
					connection.write(msg)

		else:
			msg = self.make_msg("Sorry, you message was not sent.", self.SERVER_NAME,)
			self.transport.write(msg)

	def make_msg(self, message, author):
			msg = dict()
			msg["content"] = message
			msg["author"] = author
			
			return json.dumps(msg).encode()
			
	def output(self, data):
		stdout.write(data.strip() + '\n')

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Server settings")
	parser.add_argument("--addr", default="127.0.0.1", type=str)
	parser.add_argument("--port", default=50000, type=int)
	args = vars(parser.parse_args())
                
	connections = []
	users = dict()
	loop = asyncio.get_event_loop()
	coro = loop.create_server(lambda: ChatServerProtocol(connections, users), args["addr"], args["port"])
	server = loop.run_until_complete(coro)

	ascii_snek = """\
    --..,_                     _,.--.
       `'.'.                .'`__ o  `;__.
          '.'.            .'.'`  '---'`  `
            '.`'--....--'`.'
              `'--....--'`
"""
	print(ascii_snek)
	print('Serving on {}:{}'.format(*server.sockets[0].getsockname()))
	try:
		loop.run_forever()
	except KeyboardInterrupt:
		pass

	server.close()
	loop.run_until_complete(server.wait_closed())
	loop.close()
