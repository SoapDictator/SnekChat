import pytest, threading
from chat_server.server import *
from chat_client.client import *

class SnekTest():
	ADDRESS = "127.0.0.1"
	PORT = 50000
	LOGIN_MESSAGE = "/login"
	TEST_MESSAGE1 = "hi"
	TEST_MESSAGE2 = "nope"

	def __init__(self):
		self.before_suite()
		#self.valid_message()
		self.before_test_valid_args()
		
	def before_suite(self):
		self.server_args_valid = dict()
		self.client_args_valid1 = dict()
		self.client_args_valid2 = dict()
		
		self.server_args_valid["addr"] = self.ADDRESS
		self.server_args_valid["port"] = self.PORT
		
		self.client_args_valid1["user"] = "ValidOne"
		self.client_args_valid1["addr"] = self.ADDRESS
		self.client_args_valid1["port"] = self.PORT
		
		self.client_args_valid2["user"] = "ValidTwo"
		self.client_args_valid1["addr"] = self.ADDRESS
		self.client_args_valid1["port"] = self.PORT
		
	def before_test_valid_args(self):
		server = SnekServer()
		client1 = SnekClient()
		client2 = SnekClient()
		
		try:
			server_thread = threading.Thread(target = server.start_server, args = self.server_args_valid)
			client_thread1 = threading.Thread(target = client1.start_client, args = self.client_args_valid1)
			client_thread2 = threading.Thread(target = client2.start_client, args = self.client_args_valid2)
		
		except:
			raise TypeError("Failed to create threads for server/clients")
		
		client1.start_client(self.client_args_valid1)
		client2.start_client(self.client_args_valid2)
		
		return client1.getUserClient(), client2.getUserClient()
		
	def after_test():
		for thread in threading.enumerate():
			thread.join()
			
	def valid_message(self):
		client1, client2 = self.before_test_valid_args()
		
		client1.send(LOGIN_MESSAGE)
		client2.send(LOGIN_MESSAGE)
		
		client1.send(TEST_MESSAGE1)
		time.wait(0.1)
		
		assert client2.getMsgLastReceived() == TEST_MESSAGE1
		
		self.after_test()
		
start = SnekTest()