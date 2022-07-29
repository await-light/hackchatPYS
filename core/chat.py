import re
import json
import time
import logging

import sys
sys.path.append("../")
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
		tdata = text.strip()
		match = re.match(r"^/([a-zA-Z0-9_-]+) ?",tdata)

		if match != None:
			return base.Handler(
				command=tdata[match.span()[0]+1:match.span()[1]-1],
				content=tdata[match.span()[1]:])

		data = {
				"cmd":"chat",
				"nick":userobj.nick,
				"uType":userobj.utype,
				"userid":userobj.userid,
				"channel":user.channel,
				"text":text,
				"level":userobj.level,
				"time":round(time.time())
			}

		if userobj.color != None:
			data["color"] = userobj.color

		if userobj.trip != None:
			data["trip"] = userobj.trip

		self.users.broadcasttext(userobj.channel,
			json.dumps(data))
		logging.info("%s : %s" % (userobj.nick,text))

		return None