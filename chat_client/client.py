import asyncio, json, argparse, sys
from sys import stdout

class SnekClient():
	def __init__(self):
		ascii_snek = """\
        --..,_                     _,.--.
           `'.'.                .'`__ o  `;__.
              '.'.            .'.'`  '---'`  `
               '.`'--....--'`.'
                 `'--....--'`
		"""

		print(ascii_snek)

	def start_client(self, args):
		loop = asyncio.get_event_loop()
		self.userClient = self.ChatClientProtocol(loop, args["user"])
		coro = loop.create_connection(lambda: self.userClient, args["addr"], args["port"])
		server = loop.run_until_complete(coro)
		
		asyncio.async(self.userClient.msgGet(loop))
		loop.run_forever()
		loop.close()
		
	def getUserClient(self):
		return self.userClient
		
	class ChatClientProtocol(asyncio.Protocol):
		def __init__(self, loop, user, **kwargs):
			self.user = user
			self.is_open = False
			self.loop = loop
			self.last_message_sent = ""
			self.last_message_received = ""
			
		def connection_made(self, transport):
			self.sockname = transport.get_extra_info("sockname")
			self.transport = transport
			self.transport.write(self.user.encode())
			self.is_open = True
			
		def connection_lost(self, exc):
			self.is_open = False
			self.loop.stop()
			sys.exit()

		def data_received(self, data):
			while not hasattr(self, "output"): #Wait until output is established
				pass
			if data:
				message = json.loads(data.decode())
				self.messageHandle(message)

		def messageHandle(self, message):
			try:
				content = "{author}: {content}".format(**message)
				self.last_message_received = content
				self.output(content + '\n')
				
			except KeyError:
				print("Oops!")

		def send(self, data):
			if data and self.user:
				self.last_message_sent = "{author}: {content}".format(author=self.user, content=data)
				self.transport.write(data.encode())
				
		async def msgGet(self, loop):
			while True:
				msg = await loop.run_in_executor(None, input) #Get stdout input forever
				self.send(msg)

		def output(self, data):
			stdout.write(data)
			
		def getMsgLastReceived():
			return self.last_message_received
			
		def getMsgLastSent():
			return self.last_message_sent

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Client settings")
	parser.add_argument("--user", default="User", type=str)
	parser.add_argument("--addr", default="127.0.0.1", type=str)
	parser.add_argument("--port", default=50000, type=int)
	args = vars(parser.parse_args())
	
	client = SnekClient()
	client.start_client(args)