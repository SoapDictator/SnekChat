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
		self.test_valid_message()
		
	def test_before_suite(self):
		self.client_args_valid1 = dict()
		self.client_args_valid2 = dict()
		
		self.client_args_valid1["user"] = "ValidOne"
		self.client_args_valid1["addr"] = self.ADDRESS
		self.client_args_valid1["port"] = self.PORT
		
		self.client_args_valid2["user"] = "ValidTwo"
		self.client_args_valid2["addr"] = self.ADDRESS
		self.client_args_valid2["port"] = self.PORT
		
	def before_test(self):
		client1 = SnekClient()
		client2 = SnekClient()
		
		client_thread1 = threading.Thread(target = client1.start_client,  kwargs = self.client_args_valid1)
		client_thread1.start()
		time.sleep(1)
		
		client_thread2 = threading.Thread(target = client2.start_client,  kwargs = self.client_args_valid2)
		client_thread2.start()
		time.sleep(1)
		
		return client1.getUserClient(), client2.getUserClient()
		
	def after_test(self):
		for thread in threading.enumerate():
			thread.join()
			
	def get_err_msg(self, expected, actual):
		return "Expected {}; Actual {}".format(expected, actual)
			
	#===================== client methods =====================
			
	def test_valid_message(self):	
		client1, client2 = self.before_test()
		
		client1.send(self.LOGIN_MESSAGE)
		time.sleep(0.1)
		client2.send(self.LOGIN_MESSAGE)
		time.sleep(0.1)
		
		client1.send(self.TEST_MESSAGE1)
		time.sleep(0.1)
		
		actual = client2.getMsgLastReceived()
		expected = "{}: {}".format(client1.getUserName(), self.TEST_MESSAGE1)
		assert expected == actual, self.get_err_msg(expected, actual)
		
		#after test
		client1.send(self.DISCONNECT_MESSAGE)
		time.sleep(1)
		client2.send(self.DISCONNECT_MESSAGE)
		time.sleep(1)
		
		self.after_test()
		
start = SnekTest()