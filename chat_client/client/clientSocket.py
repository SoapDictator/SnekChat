import socket

class chatClient():
	HOST = None
	PORT = None
	
	def __init__(self, HOST, PORT):
		HOST = HOST
		PORT = PORT
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((HOST, PORT))

		print("Connected")
		sock.send("LOL SO RANDOM")

		print("Sent")
		result = sock.recv(1024)
		sock.close()
		print("Received:", result)