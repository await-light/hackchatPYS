import re
import json
import websockets
import random
import base64
import hashlib

def empty_func(*args):
	def func():
		return None
	return func

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
		self.trip = trip # None
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

	def sendto(self,data,user):
		websockets.broadcast(
			[user.websocket],
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


class Handler:
	def __init__(self,command,content):
		self.data = self._handledata(command,content)

	def _handledata(self,command,content):
		if command == "me":
			return {
				"cmd":"emote",
				"text":content
				}

		elif command == ("changecolor" or "color"):
			matchcolorcode = re.findall(r"^\#?([A-Fa-f0-9]{6})$",content)
			if matchcolorcode:
				return {
					"cmd":"changecolor",
					"color":matchcolorcode[0]
					} 
			else:
				return json.dumps({
					"cmd":"warn",
					"text":"Invalid color! Color must be in hex value"
					})

		elif command == ("w" or "whisper"):
			matchwhisper = re.findall(r"^\@?([a-zA-Z0-9_]+) ([^\ ]+)$",content)
			if matchwhisper:
				targetnick,text = matchwhisper[0]

				return {
					"cmd":"whisper",
					"nick":targetnick,
					"text":text
					}

		return json.dumps({
			"cmd":"warn",
			"text":"Unknown command: %s" % command
			})

