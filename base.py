import json
import websockets
import random
import base64
import hashlib

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
		color=None,
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
		jhash = hashlib.sha256(websocket.host.encode()).hexdigest()
		hashhost = base64.b64encode(jhash.encode()).decode()
		self.hash_ = hashhost


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
		if str(type(data)) == "<class 'list'>":
			self.data = self._match(self.argslist,data)
		else:
			self.data = data

	def _match(self,argslist,fargs):
		jsondata = {}
		if len(argslist) == len(fargs):
			for index,arg in enumerate(argslist):
				jsondata[arg] = fargs[index]
		return jsondata

	def execute(self):
		pass

	def __call__(self):
		return self.execute()


class Handler:
	def __init__(self,data):
		# ^color #ff6000$
		data = data.split()
		# color
		self.command = data[0]
		# args
		self.args = data[1:]
