import json
import websockets
import random

class User:
	def __init__(self,
		websocket,
		nick,
		trip,
		channel,
		utype="user",
		isbot=False,
		isme=False,
		userid=round(random.random() * 9999999999999),
		level=100,
		color=False,
		hash_=None):

		self.websocket = websocket
		self.nick = nick	
		self.trip = trip
		self.channel = channel
		self.utype = utype
		self.isbot = False
		self.isme = False
		self.userid = userid
		self.level = level
		self.color = color
		self.hash_ = hash_


class Users:
	def __init__(self):
		self.userset = set()
		'''format:
		# {User(websocket,"111"...),User(websocket,"333"...,channel="your-channel")}
		'''

	def broadcasttext(self,channel,data): #,blacklist=[]
		'''
		broadcast the message in specify channel
		'''
		websockets.broadcast(
			[user.websocket for user in self.userset if user.channel == channel],
			data)


class CommandBase:
	def __init__(self,websocket,users,data):
		self.websocket = websocket
		self.users = users
		self.data = data

	def execute(self):
		pass

	def __call__(self):
		return self.execute()