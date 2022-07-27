import sys
sys.path.append("../")

import time
import json
import logging
import websockets

import base

class Left(base.CommandBase):
	def __init__(self,websocket,users,data):
		base.CommandBase.__init__(self,
			websocket=websocket,
			users=users,
			data=data)

	def execute(self):
		'''
		remove the user object from userset
		than broadcast the user.nick is left
		'''

		# find the user object in user set according his websocket
		for user in self.users.userset:
			if user.websocket == self.websocket:
				# get his channel for broadcasting
				user = user
				self.users.userset.remove(user)
				break
		else:
			logging.warning("User not found.But connection closed")
			return None

		# broadcast
		self.users.broadcasttext(user.channel,
			json.dumps({
				"cmd":"onlineRemove",
				"userid":user.userid,
				"nick":user.nick,
				"channel":user.channel,
				"time":round(time.time())
				})
			)
		return None