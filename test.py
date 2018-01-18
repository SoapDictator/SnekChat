import pytest, threading, time, unittest
from chat_server.server import *
from chat_client.client import *

class TestSnek(unittest.TestCase):
	ADDRESS = "127.0.0.1"
	PORT = 50000
	LOGIN_MESSAGE = "/login"
	DISCONNECT_MESSAGE = "/disconnect"
	TEST_MESSAGE1 = "hi"
	TEST_MESSAGE2 = "nope"
	ERROR_IVALID_USERNAME = "[Server]: Your name must be alphanumeric!"
	
	valid_connection = dict()
	valid_connection["addr"] = ADDRESS
	valid_connection["port"] = PORT
	
	client_args_valid1 = valid_connection.copy()
	client_args_valid1["user"] = "ValidOne"
	
	client_args_valid2 = valid_connection.copy()
	client_args_valid2["user"] = "ValidTwo"
	
	client_args_valid3 = valid_connection.copy()
	client_args_valid3["user"] = "ValidThree"
	
	client_args_invalid1 = valid_connection.copy()
	client_args_invalid1["user"] = "_InvalidOne_"
	
	client_args_invalid2 = valid_connection.copy()
	client_args_invalid2["user"] = "Invalid1"
	
	client_args_invalid3 = valid_connection.copy()
	client_args_invalid3["user"] = "!#@^;:-"
		
	def before_test(self):
		client1 = self.make_client(self.client_args_valid1)
		client2 = self.make_client(self.client_args_valid2)
		
		return client1, client2
		
	def after_test(self, clients):
		for client in clients:
			client.send(self.DISCONNECT_MESSAGE)
			time.sleep(0.1)
		
		for thread in threading.enumerate():
			if thread._name != "MainThread":
				thread.join()
		
		time.sleep(0.1)
	
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
	
	def format_sent(self, client, message):
		return "{}: {}".format(client.getUserName(), message)
		
	def format_wisper_sent(self, client, message):
		return "/w {} {}".format(client.getUserName(), message)
		
	def format_wisper_received(self, client, message):
		return "{}: <whisper> {}".format(client.getUserName(), message)
	
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
		self.assertEqual(expected, actual, self.get_err_msg(expected, actual))
		
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
		
		#after test
		self.after_test(clients)
		self.assertFalse(expected == actual, self.get_err_msg(expected, actual, "Expected mismatch"))
		
	def test_message_after_disconnect(self):
		header = "#===================== Message After Disconnect ====================="
		print(header)
		#before test
		clients = self.before_test()
		client0 = clients[0]
		client1 = clients[1]
		
		self.clients_login(clients)
		
		#test
		client1.send(self.DISCONNECT_MESSAGE)
		time.sleep(0.1)
		
		client0.send(self.TEST_MESSAGE2)
		time.sleep(0.1)
		
		actual = client1.getMsgLastReceived()
		expected = self.format_sent(client0, self.TEST_MESSAGE2)
		
		#after test
		self.after_test(clients)
		self.assertFalse(expected == actual, self.get_err_msg(expected, actual, "Expected mismatch"))
		
	def test_message_whisper(self):
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
		time.sleep(1)
		
		actual0 = client2.getMsgLastReceived()
		expected0 = client1.getMsgLastReceived()
		
		actual1 = client1.getMsgLastReceived()
		expected1 = self.format_wisper_received(client0, self.TEST_MESSAGE1)
		
		#after test
		self.after_test(clients)
		
		self.assertFalse(expected0 == actual0, self.get_err_msg(expected0, actual0, "Expected mismatch"))
		self.assertEqual(expected1, actual1, self.get_err_msg(expected1, actual1))
		
	def test_invalid_usernames(self):
		header = "#===================== Invalid Usernames ====================="
		print(header)
		#test
		client0 = self.make_client(self.client_args_invalid1)
		client1 = self.make_client(self.client_args_invalid2)
		client2 = self.make_client(self.client_args_invalid3)
		clients = (client0, client1, client2)
		
		actual0 = client0.getMsgLastReceived()
		actual1 = client1.getMsgLastReceived()
		actual2 = client2.getMsgLastReceived()
		
		#after test
		self.after_test(clients)	
		
		self.assertEqual(actual0, self.ERROR_IVALID_USERNAME)
		self.assertFalse(client0.is_open)
		
		self.assertEqual(actual1, self.ERROR_IVALID_USERNAME)
		self.assertFalse(client1.is_open)
		
		self.assertEqual(actual2, self.ERROR_IVALID_USERNAME)
		self.assertFalse(client2.is_open)
		
if __name__== '__main__':
    unittest.main()	
