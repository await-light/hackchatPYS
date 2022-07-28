'''
just a failed command
'''

import sys
sys.path.append("../")
import base


class Color(base.CommandBase):
	def __init__(self,websocket,users,data):
		self.argslist = ["color"]
		base.CommandBase.__init__(self,
			websocket=websocket,
			users=users,
			data=data)

	def execute(self):
		if "color" in self.data:
			for user in self.users.userset:
				if user.websocket == self.websocket:
					user.color = self.data["color"]