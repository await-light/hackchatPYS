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
		if self.userself != None:
			self.userself.color = self.data["color"]
			logging.info("%s change color: %s" % (
			self.userself.nick,self.data["color"]))
		return None