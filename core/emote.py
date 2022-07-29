import time
import json
import logging

import sys
sys.path.append("../")
import base

class Emote(base.CommandBase):
	def __init__(self,websocket,users,data):
		base.CommandBase.__init__(self,
			websocket=websocket,
			users=users,
			data=data)

	def execute(self):
		if "text" in self.data:
			for user in self.users.userset:
				if user.websocket == self.websocket:
					userobj = user
					break
			else:
				return None

			data = {
				"cmd":"emote",
				"nick":userobj.nick,
				"userid":userobj.userid,
				"text":"@%s %s" % (userobj.nick,self.data["text"]),
				"channel":userobj.channel,
				"time":round(time.time())
			}

			if userobj != None:
				data["trip"] = userobj.trip 

			# broadcast
			self.users.broadcasttext(userobj.channel,
				json.dumps(data))

			logging.info("%s(?%s) emoted: %s" % (
				userobj.nick,userobj.channel,self.data["text"]))

			return None