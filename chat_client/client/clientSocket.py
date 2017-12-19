import asyncio, json, argparse
from sys import stdout

class Client(asyncio.Protocol):
    def __init__(self, loop, user, **kwargs):
        self.user = user
        self.is_open = False
        self.loop = loop
        self.last_message = ""
        
    def connection_made(self, transport):
        self.sockname = transport.get_extra_info("sockname")
        self.transport = transport
        self.transport.write(self.user.encode())
        self.is_open = True
        
    def connection_lost(self, exc):
        self.is_open = False
        self.loop.stop()

    def data_received(self, data):
        while not hasattr(self, "output"): #Wait until output is established
            pass
        if data:
            message = json.loads(data.decode())
            self.process_message(message)

    def process_message(self, message):
        try:
            if message["event"] == "servermsg":
                content = "{timestamp} | {author} {content}".format(**message)
            else:
                content = "{timestamp} | {author}: {content}".format(**message)
            
            self.output(content.strip() + '\n')
        except KeyError:
            print("Malformed message, skipping")

    def send(self, data):
        if data and self.user:
            self.last_message = "{author}: {content}".format(author=self.user, content=data)
            self.transport.write(data.encode())
            
    async def getmsgs(self, loop):
        self.output("Connected to {0}:{1}\n".format(*self.sockname))
        while True:
            msg = await loop.run_in_executor(None, input, "{}: ".format(self.user)) #Get stdout input forever
            self.send(msg)

    def output(self, data):
        if self.last_message.strip() == data.strip():
            return #Unclouds stdout with duplicate messages (sent and received)
        else:
            stdout.write(data.strip() + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client settings")
    parser.add_argument("--user", default="User", type=str)
    parser.add_argument("--addr", default="127.0.0.1", type=str)
    parser.add_argument("--port", default=50000, type=int)
    args = vars(parser.parse_args())

    loop = asyncio.get_event_loop()
    userClient = Client(loop, args["user"])
    coro = loop.create_connection(lambda: userClient, args["addr"], args["port"])
    server = loop.run_until_complete(coro)

    asyncio.async(userClient.getmsgs(loop))
    loop.run_forever()
    loop.close()


        

        
