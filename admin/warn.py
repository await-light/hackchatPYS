import json
import logging

import sys
sys.path.append("../")
import base

class Warn(base.CommandBase):
	def __init__(self,websocket,users,data):
		base.CommandBase.__init__(self,
			websocket=websocket,
			users=users,
			data=data,
			level=10000)

	def execute(self):
		if self.userself != None:
			userobj = self.userself
		else:
			return None

		if "text" in self.data:
			text = self.data["text"]
		else:
			return None

		self.users.broadcasttext(userobj.channel,
			json.dumps({
				"cmd":"warn",
				"text":text
				}))

		return None
