import socket, string

class chatServer():
	HOST = None
	PORT = None
	
	def __init__(self, HOST, PORT):
		self.HOST = HOST
		self.PORT = PORT
		srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		srv.bind((HOST, PORT))
		
		self.main_cycle()
			
	def main_cycle(self):
		while True:
			print("Listening port 33333")
			srv.listen(1)
			sock, addr = srv.accept()
			while 1:
				pal = sock.recv(1024)
				if pal:
					break
			print("Received from %s: %s" % (addr, pal))
			lap = self.do_something(pal)
			print("Sent %s: %s" % (addr, lap))
			sock.send(lap)
			sock.close()

	def do_something(self, x):
		lst = map(None, x);
		lst.reverse();
		return string.join(lst, "")