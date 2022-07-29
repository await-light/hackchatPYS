import json
import time
import logging

import sys
sys.path.append("../")
import base

class Whisper(base.CommandBase):
	def __init__(self,websocket,users,data):
		base.CommandBase.__init__(self,
			websocket=websocket,
			users=users,
			data=data)

	def execute(self):
		if ("nick" and "text") not in self.data:
			return None

		for user in self.users.userset:
			if user.websocket == self.websocket:
				fromuser = user 
				break
		else:
			return None

		for user in self.users.userset:
			if user.nick == self.data["nick"] and user.channel == fromuser.channel:
				targetuser = user 
				break
		else:
			return json.dumps({
				"cmd":"warn",
				"text":"Could not find user in channel"
				})

		sendtofrom = json.dumps({
			"cmd":"info",
			"channel":fromuser.channel,
			"from":fromuser.userid,
			"to":targetuser.userid,
			"text":"You whispered to @%s: %s" % (
				targetuser.nick,self.data["text"]),
			"time":round(time.time())
		})

		sendtotarget = {
			"cmd":"info",
			"channel":fromuser.channel,
			"from":fromuser.nick,
			"to":targetuser.userid,
			"text":"%s whispered: %s" % (
				fromuser.nick,self.data["text"]),
			"type":"whisper",
			"level":fromuser.level,
			"uType":fromuser.utype,
			"time":round(time.time())
		}
		if fromuser.trip != None:
			sendtotarget["trip"] = fromuser.trip
		else:
			sendtotarget["trip"] = "null"
		self.users.sendto(json.dumps(sendtotarget),targetuser)

		return sendtofrom
