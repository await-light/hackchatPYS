import logging

import sys
sys.path.append("../")
import base

class ChangeColor(base.CommandBase):
	def __init__(self,websocket,users,data):
		base.CommandBase.__init__(self,
			websocket=websocket,
			users=users,
			data=data)

	def execute(self):
		if "color" in self.data:
			for user in self.users.userset:
				if user.websocket == self.websocket:
					user.color = self.data["color"]
					logging.info("%s change color: %s" % (
						user.nick,self.data["color"]))
					return None