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

	def __init__(self):
		self.test_before_suite()
		
		#TESTS
		self.test_valid_message()
		self.test_message_before_login()
		self.test_message_wisper()
		
		self.test_after_suite()
		
	def test_before_suite(self):
		self.client_args_valid1 = dict()
		self.client_args_valid2 = dict()
		self.client_args_valid3 = dict()
		
		self.client_args_valid1["user"] = "ValidOne"
		self.client_args_valid1["addr"] = self.ADDRESS
		self.client_args_valid1["port"] = self.PORT
		
		self.client_args_valid2["user"] = "ValidTwo"
		self.client_args_valid2["addr"] = self.ADDRESS
		self.client_args_valid2["port"] = self.PORT
		
		self.client_args_valid3["user"] = "ValidThree"
		self.client_args_valid3["addr"] = self.ADDRESS
		self.client_args_valid3["port"] = self.PORT
		
	def test_after_suite(self):
		quit()
		
	def before_test(self):
		client1 = self.make_client(self.client_args_valid1)
		client2 = self.make_client(self.client_args_valid2)
		
		return client1, client2
		
	def after_test(self, clients):
		try:
			for client in clients:
				client.send(self.DISCONNECT_MESSAGE)
			time.sleep(0.1)
			
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
		
	def format_sent(self, client, message):
		return "{}: {}".format(client.getUserName(), message)
		
	def format_wisper(self, client, message):
		return "/w {} {}".format(client.getUserName, message)
	
	def get_err_msg(self, expected, actual, msg = ""):
		return "Expected {}; Actual {}. {}".format(expected, actual, msg)
	
	#===================== tests =====================
			
	def test_valid_message(self):
		client1, client2 = self.before_test()
		
		client1.send(self.LOGIN_MESSAGE)
		client2.send(self.LOGIN_MESSAGE)
		time.sleep(0.1)
		
		client1.send(self.TEST_MESSAGE1)
		time.sleep(0.1)
		
		actual = client2.getMsgLastReceived()
		expected = self.format_sent(client1, self.TEST_MESSAGE1)
		assert expected == actual, self.get_err_msg(expected, actual)
		
		#after test
		self.after_test([client1, client2])
		
	def test_message_before_login(self):
		client1, client2 = self.before_test()
		
		client1.send(self.LOGIN_MESSAGE)
		time.sleep(0.1)
		
		client2.send(self.TEST_MESSAGE1)
		time.sleep(0.1)
		
		actual = client1.getMsgLastReceived()
		expected = self.format_sent(client2, self.TEST_MESSAGE1)
		assert expected != actual, self.get_err_msg(expected, actual, "Expected mismatch")
		#after test
		self.after_test([client1, client2])
		
	def test_message_wisper(self):
		client1, client2 = self.before_test()
		client3 = self.make_client(self.client_args_valid3)
		
		client1.send(self.LOGIN_MESSAGE)
		client2.send(self.LOGIN_MESSAGE)
		client3.send(self.LOGIN_MESSAGE)
		time.sleep(0.1)
		
		client1.send(self.format_wisper(client2, self.TEST_MESSAGE1))
		time.sleep(0.1)
		
		actual = client3.getMsgLastReceived()
		expected = client2.getMsgLastReceived()
		assert expected != actual, self.get_err_msg(expected, actual, "Expected mismatch")
		#after test
		self.after_test([client1, client2, client3])
		
start = SnekTest()