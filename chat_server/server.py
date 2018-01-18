import asyncio, json, argparse
from sys import stdout
        
class SnekServer():
	connections = []
	users = dict()

	def __init__(self):
		ascii_snek = """\
        --..,_                     _,.--.
           `'.'.                .'`__ o  `;__.
              '.'.            .'.'`  '---'`  `
               '.`'--....--'`.'
                 `'--....--'`
		"""

		print(ascii_snek)
		
	def start_server(self, *args, **kwargs):
		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)

		coro = loop.create_server(lambda: self.ChatServerProtocol(self.connections, self.users), kwargs["addr"], kwargs["port"])
		server = loop.run_until_complete(coro)
		
		print('Serving on {}:{}'.format(*server.sockets[0].getsockname()))
		try:
			loop.run_forever()
		except KeyboardInterrupt:
			pass

		server.close()
		loop.run_until_complete(server.wait_closed())
		loop.close()
	
	class ChatServerProtocol(asyncio.Protocol):
		def __init__(self, connections, users):
			self.connections = connections
			self.users = users
			self.peername = ""
			self.user = None
			self.is_loggined = False
			
			self.SERVER_NAME = "[Server]"
			
		def connection_made(self, transport):
			self.connections += [transport]
			self.peername = transport.get_extra_info('sockname')
			self.transport = transport

		def connection_lost(self, exc):				
			err = "{} disconnected".format(self.user)
			message = self.msgMake(err, self.SERVER_NAME)

			for connection in self.connections:
				connection.write(message)
				
			self.connections.remove(self.transport)

		def data_received(self, data):
			if data:
				if not self.user:
					user = data.decode()
					if not user.isalpha():
						self.transport.write(self.msgMake("Your name must be alphanumeric!", self.SERVER_NAME))
						self.transport.close()
					elif user in self.users.keys():
						self.transport.write(self.msgMake("There is already a user with that nickname connected!", self.SERVER_NAME))
						self.transport.close()
					else:
						self.user = data.decode()
						msg = '{} connected'.format(self.user)
						self.transport.write(self.msgMake(msg, self.SERVER_NAME))
						
				else:
					self.message = data.decode()
					custom_connections = self.messageHandle()
					
					if self.is_loggined and len(custom_connections) != 0 and self.message != "":
						msg = self.msgMake(self.message, self.user)
						self.msgSend(msg, custom_connections)

			else:
				self.transport.write(self.msgMake("Sorry, you message was not sent.", self.SERVER_NAME))

		def messageHandle(self):
			message = self.message
			
			if "/login" in message:
				self.is_loggined = True
				self.users[self.user] = self.transport
				
				self.message = ""
				return self.connections
				
			elif "/disconnect" in message:
				self.transport.close()
				
				self.message = ""
				return None
				
			elif "/w" in message:
				wispered_user = message.split(" ")[1]
				if wispered_user in self.users:
					whispered_connection = self.users[wispered_user]
					
					self.message = message.strip("/w "+wispered_user+" ")
					self.message = "<whisper> " + self.message
					return [whispered_connection]
					
			else:
				self.message = message
				return self.connections
				
		def msgMake(self, message, author):
			msg = dict()
			msg["content"] = message
			msg["author"] = author
				
			self.output(author+": "+message)
			return json.dumps(msg).encode()
			
		def msgSend(self, message_encoded, connections):
			for connection in connections:
				if self.is_loggined:
					connection.write(message_encoded)
				
		def output(self, data):
			stdout.write(data.strip() + '\n')

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Server settings")
	parser.add_argument("--addr", default="127.0.0.1", type=str)
	parser.add_argument("--port", default=50000, type=int)
	args = vars(parser.parse_args())
	
	server = SnekServer()
	server.start_server(**args)