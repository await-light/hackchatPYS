import json
import time
import logging

import sys
sys.path.append("../")
import base

class Kick(base.CommandBase):
	def __init__(self,websocket,users,data):
		base.CommandBase.__init__(self,
			websocket=websocket,
			users=users,
			data=data,
			level=1000)

	def execute(self):
		if "nick" in self.data:
			for userobj in self.users.userset:
				if (userobj.nick == self.data["nick"]):
					user = userobj
					break
			else:
				return json.dumps({
					"cmd":"warn",
					"text":"Could not find user in channel"
					})

			if (self.userself.level > user.level):
				logging.info("kicked %s" % user.nick)

				self.users.broadcasttext(user.channel,
					json.dumps({
						"cmd":"info",
						"text":"Kicked %s" % user.nick,
						"channel":user.channel,
						"time":round(time.time())
						})
					)

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
			else:
				return json.dumps({
					"cmd":"warn",
					"text":"Cannot kick other users with the same or larger level, how rude"
					})


		return None