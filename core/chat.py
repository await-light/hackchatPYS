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

		if self.userself != None:
			userobj = self.userself
		else:
			return None

		text = self.data["text"]
		tdata = text.strip()
		match = re.findall(r"^/([a-zA-Z0-9_-]+) ?",tdata)

		if match != []:
			return base.Handler(
				command=match[0],
				content=tdata[len(match[0])+2:])

		data = {
				"cmd":"chat",
				"nick":userobj.nick,
				"uType":userobj.utype,
				"userid":userobj.userid,
				"channel":userobj.channel,
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