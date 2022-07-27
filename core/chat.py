import sys
sys.path.append("../")

import json
import time

import base

class Chat(base.CommandBase):
	def __init__(self,websocket,users,data):
		base.CommandBase.__init__(self,
			websocket=websocket,
			users=users,
			data=data)

	def execute(self):
		if "text" not in self.data:
			return None

		for user in self.users.userset:
			if user.websocket == self.websocket:
				userobj = user 
				break
		else:
			return None

		text = self.data["text"]

		self.users.broadcasttext(userobj.channel,
			json.dumps({
				"cmd":"chat",
				"nick":userobj.nick,
				"uType":userobj.utype,
				"userid":userobj.userid,
				"channel":user.channel,
				"text":text,
				"level":userobj.level,
				"trip":userobj.trip,
				"color":userobj.color,
				"time":round(time.time())
				}))
		return None