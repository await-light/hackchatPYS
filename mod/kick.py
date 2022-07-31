import json
import time
import logging

import sys
sys.path.append("../")
import base

class Kick(base.CommandBase):
	def __init__(self,websocket,users,data,level=1000):
		base.CommandBase.__init__(self,
			websocket=websocket,
			users=users,
			data=data)

	def execute(self):
		if "nick" in self.data:
			for user in self.users.userset:
				if user.nick == self.data["nick"]:
					logging.info("kicked %s" % user.nick)
					self.users.userset.remove(user)
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
			else:
				return json.dumps({
					"cmd":"warn",
					"text":"Could not find user in channel"
					})

		return None