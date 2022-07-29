import re
import time
import json
import random
import hashlib
import base64
import logging

import sys
sys.path.append("../")
import base

class Join(base.CommandBase):
	def __init__(self,websocket,users,data):
		base.CommandBase.__init__(self,
			websocket=websocket,
			users=users,
			data=data)

	def if_correct_format_data(self,data):
		'''
		correct data result is True
		otherwise result is False
		'''
		if ("nick" and "channel") in data:
			return True
		return False

	def judge_nick(self,nick):
		# judge whether it has password
		passwordfalsepattern = r"^([a-zA-Z0-9_]{1,24})$" # no password
		passwordtruepattern = r"^([a-zA-Z0-9_]{1,24}) #(.+)$" # with password
		falseresult = re.findall(passwordfalsepattern,nick)
		trueresult = re.findall(passwordtruepattern,nick)
		correct = True # correct(don't have or have)

		if falseresult != []:
			newnick,password = falseresult[0],None # if no password,password = None
		elif trueresult != []:
			newnick,password = trueresult[0]
		else: # if it doesn't have correct nick 
			correct = False 

		if correct: 
			if password == None: 
				# the password is None,so the trip is None
				trip = None # <- trip
				return (newnick,trip) 

			else: # first sha256 and then base64
				'''
				hack.chat/server/src/commands/core/join.js
				```javascript
				const hash = (password) => {
				  const sha = crypto.createHash('sha256');
				  sha.update(password);
				  return sha.digest('base64').substr(0, 6);
				};
				'''
				s2pwd = hashlib.sha256(password.encode()).hexdigest()
				trip = base64.b64encode(s2pwd.encode()).decode()[:6]
				return (newnick,trip)

		else: # 
			logging.info("%s tried to join,but failed" % self.websocket)
			return json.dumps({
				"cmd":"warn",
				"text":"Nickname must consist of up"
					" to 24 letters, numbers, and underscores"
				}) 

	def execute(self):
		# if the json data is correct,set self.nick and self.channel
		if self.if_correct_format_data(self.data):
			handlenick = self.data["nick"]
			channel = self.data["channel"]
		# Nothing will happen if the json data is incorrect
		else:
			return None
		
		# 
		nickcorrect = self.judge_nick(handlenick)

		'''
		if nickcorrect's type is json
		> send json data

		if nickcorrect's type is tuple
		> newnick , trip 
		'''
		if str(type(nickcorrect)) == "<class 'str'>":
			return nickcorrect # <- json data
		elif str(type(nickcorrect)) == "<class 'tuple'>": 
			newnick,trip = nickcorrect

		# self.websocket
		# self.users
		# self.nick
		# self.channel
		# self.trip

		# 1. the nick is not in the channel
		# 2. the websocket doesn't enter any channel before
		channelnicks = [user.nick.lower() for user in self.users.userset if user.channel == channel]
		websockethis = [user.websocket for user in self.users.userset]

		if self.websocket not in websockethis:
			if newnick.lower() not in channelnicks:
				init = base.User(
						websocket=self.websocket,
						nick=newnick,
						trip=trip,
						channel=channel)

				broadcastdata = {
					"cmd":"onlineAdd",
					"nick":init.nick,
					"uType":init.utype,
					"hash":init.hash_,
					"level":init.level,
					"userid":init.userid,
					"isbot":init.isbot,
					"channel":init.channel,
					"time":round(time.time())
					}

				if init.trip != None:
					broadcastdata["trip"] = init.trip

				self.users.broadcasttext(channel,
					json.dumps(broadcastdata))
					
				self.users.userset.add(init)

				logging.info("%s joined ?%s" % (newnick,channel))

				resultdata = {
					"cmd":"onlineSet",
					"nicks":[user.nick for user in self.users.userset if user.channel == channel],
					"users":[]}

				for user in self.users.userset:
					data = {
						"channel":user.channel,
						"isme":user.isme,
						"nick":user.nick,
						"uType":user.utype,
						"hash":user.hash_,
						"level":user.level,
						"userid":user.userid,
						"isbot":user.isbot
						}
					if user.trip != None:
						data["trip"] = user.trip
					if user.color != None:
						data["color"] = user.color

					resultdata["users"].append(data)
					
				return json.dumps(resultdata)

			else:
				logging.info("%s tried to join,but failed" % self.websocket)
				return json.dumps({
					"cmd":"warn",
					"text":"Nickname taken"})