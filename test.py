import pytest, threading, time
from chat_server.server import *
from chat_client.client import *

class SnekTest():
	ADDRESS = "127.0.0.1"
	PORT = 50000
	LOGIN_MESSAGE = "/login"
	DISCONNECT_MESSAGE = "/disconnect"
	TEST_MESSAGE1 = "hi"
	TEST_MESSAGE2 = "nope"
	ERROR_IVALID_USERNAME = "[Server]: Your name must be alphanumeric!"

	def __init__(self):
		self.test_before_suite()
		
		#TESTS
		self.test_invalid_usernames()
		self.test_valid_message()
		self.test_message_after_disconnect()
		self.test_message_before_login()
		self.test_message_wisper()
		
		self.test_after_suite()
		
	def test_before_suite(self):
		valid_connection = dict()
		valid_connection["addr"] = self.ADDRESS
		valid_connection["port"] = self.PORT
		
		self.client_args_valid1 = valid_connection.copy()
		self.client_args_valid1["user"] = "ValidOne"
		
		self.client_args_valid2 = valid_connection.copy()
		self.client_args_valid2["user"] = "ValidTwo"
		
		self.client_args_valid3 = valid_connection.copy()
		self.client_args_valid3["user"] = "ValidThree"
		
		self.client_args_invalid1 = valid_connection.copy()
		self.client_args_invalid1["user"] = "_InvalidOne_"
		
		self.client_args_invalid2 = valid_connection.copy()
		self.client_args_invalid2["user"] = "Invalid1"
		
		self.client_args_invalid3 = valid_connection.copy()
		self.client_args_invalid3["user"] = "!#@^;:-"
		
	def test_after_suite(self):
		quit()
		
	def before_test(self):
		client1 = self.make_client(self.client_args_valid1)
		client2 = self.make_client(self.client_args_valid2)
		
		return client1, client2
		
	def after_test(self, clients):
		try:
			self.clients_disconnect(clients)
			
			for thread in threading.enumerate():
				if thread._name != "MainThread":
					thread.join()
		except:
			pass
	
	#===================== util methods =====================
	def make_client(self, args):
		client = SnekClient(isTested = True)
		client_thread = threading.Thread(target = client.start_client,  kwargs = args)
		client_thread.start()
		time.sleep(1)
		
		return client.getUserClient()
		
	def clients_login(self, clients):
		for client in clients:
			client.send(self.LOGIN_MESSAGE)
		time.sleep(0.1)
	
	def clients_disconnect(self, clients):
		for client in clients:
			client.send(self.DISCONNECT_MESSAGE)
		time.sleep(0.1)
	
	def format_sent(self, client, message):
		return "{}: {}".format(client.getUserName(), message)
		
	def format_wisper_sent(self, client, message):
		return "/w {} {}".format(client.getUserName(), message)
		
	def format_wisper_received(self, client, message):
		return "{}: <wisper> {}".format(client.getUserName(), message)
	
	def get_err_msg(self, expected, actual, msg = ""):
		return "Expected {}; Actual {}. {}".format(expected, actual, msg)
	
	#===================== tests =====================
			
	def test_valid_message(self):
		header = "#===================== Valid Message ====================="
		print(header)
		#before test
		clients = self.before_test()
		client0 = clients[0]
		client1 = clients[1]
		
		self.clients_login(clients)
		
		#test
		client0.send(self.TEST_MESSAGE1)
		time.sleep(0.1)
		
		actual = client1.getMsgLastReceived()
		expected = self.format_sent(client0, self.TEST_MESSAGE1)
		assert expected == actual, self.get_err_msg(expected, actual)
		
		#after test
		self.after_test(clients)
		
	def test_message_before_login(self):
		header = "#===================== Message Before Login ====================="
		print(header)
		#before test
		clients = self.before_test()
		client0 = clients[0]
		client1 = clients[1]
		
		#test
		self.clients_login([client1])
		
		actual = client0.getMsgLastReceived()
		expected = self.format_sent(client1, self.TEST_MESSAGE1)
		assert expected != actual, self.get_err_msg(expected, actual, "Expected mismatch")
		
		#after test
		self.after_test(clients)
		
	def test_message_after_disconnect(self):
		header = "#===================== Message After Disconnect ====================="
		print(header)
		#before test
		clients = self.before_test()
		client0 = clients[0]
		client1 = clients[1]
		
		self.clients_login(clients)
		
		#test
		self.clients_disconnect([client1])
		actual = client1.getMsgLastReceived()
		
		client0.send(self.TEST_MESSAGE2)
		time.sleep(0.1)
		expected = self.format_sent(client0, self.TEST_MESSAGE2)
		assert expected != actual, self.get_err_msg(expected, actual, "Expected mismatch")
		
		#after test
		self.after_test(clients)
		
	def test_message_wisper(self):
		header = "#===================== Message Wisper ====================="
		print(header)
		#before test
		clients = self.before_test()
		client0 = clients[0]
		client1 = clients[1]
		client2 = self.make_client(self.client_args_valid3)
		clients = (client0, client1, client2)
		
		self.clients_login(clients)
		
		#test
		client0.send(self.format_wisper_sent(client1, self.TEST_MESSAGE1))
		time.sleep(0.1)
		
		actual = client2.getMsgLastReceived()
		expected = client1.getMsgLastReceived()
		assert expected != actual, self.get_err_msg(expected, actual, "Expected mismatch")
		
		actual = client1.getMsgLastReceived()
		expected = self.format_wisper_received(client1, self.TEST_MESSAGE1)
		assert expected != actual, self.get_err_msg(expected, actual)
		#after test
		self.after_test(clients)
		
	def test_invalid_usernames(self):
		header = "#===================== Invalid Usernames ====================="
		print(header)
		#test
		client0 = self.make_client(self.client_args_invalid1)
		client1 = self.make_client(self.client_args_invalid2)
		client2 = self.make_client(self.client_args_invalid3)
		clients = (client0, client1, client2)
		
		assert client0.getMsgLastReceived() == self.ERROR_IVALID_USERNAME
		assert client0.is_open == False
		
		assert client1.getMsgLastReceived() == self.ERROR_IVALID_USERNAME
		assert client1.is_open == False
		
		assert client2.getMsgLastReceived() == self.ERROR_IVALID_USERNAME
		assert client2.is_open == False
		
		#after test
		self.clients_login(clients)
		
start = SnekTest()