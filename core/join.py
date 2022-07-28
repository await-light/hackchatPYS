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
		if ("nick" and "channel") in data:
			return True
		return False

	def judge_nick(self,nick):
		'''
		if correct return None
		else return error message
		'''
		# judge whether it has password
		passwordfalsepattern = r"^([a-zA-Z0-9_]{1,24})$"
		passwordtruepattern = r"^([a-zA-Z0-9_]{1,24}) #(.+)$"
		falseresult = re.findall(passwordfalsepattern,nick)
		trueresult = re.findall(passwordtruepattern,nick)
		correct = True

		if falseresult != []:
			self.nick,password = falseresult[0],None
		elif trueresult != []:
			self.nick,password = trueresult[0]
		else: # if it doesn't have correct nick 
			correct = False 

		if correct: 
			if password == None: 
				# the password is None,so the trip is None
				self.trip = None
				return None 

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
				self.trip = base64.b64encode(s2pwd.encode()).decode()[:6]
				return None
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
			self.nick = self.data["nick"]
			self.channel = self.data["channel"]
		# Nothing will happen if the json data is incorrect
		else:
			return None
		
		# 
		nickcorrect = self.judge_nick(self.nick)
		if nickcorrect != None: # error message
			return nickcorrect

		# self.websocket
		# self.users
		# self.nick
		# self.channel
		# self.trip

		# 1. the nick is not in the channel
		# 2. the websocket doesn't enter any channel before
		channelnicks = [user.nick.lower() for user in self.users.userset if user.channel == self.channel]
		websockethis = [user.websocket for user in self.users.userset]

		if self.websocket not in websockethis:
			if self.nick.lower() not in channelnicks:
				init = base.User(
						websocket=self.websocket,
						nick=self.nick,
						trip=self.trip,
						channel=self.channel)

				self.users.broadcasttext(self.channel,
						json.dumps({
							"cmd":"onlineAdd",
							"nick":init.nick,
							"trip":init.trip,
							"uType":init.utype,
							"hash":init.hash_,
							"level":init.level,
							"userid":init.userid,
							"isbot":init.isbot,
							"color":init.color,
							"channel":init.channel,
							"time":round(time.time())
							}))
					
				self.users.userset.add(init)

				logging.info("%s joined" % self.nick)
					
				return json.dumps({
					"cmd":"onlineSet",
					"nicks":[user.nick for user in self.users.userset if user.channel == self.channel],
					"users":[{
						"channel":user.channel,
						"isme":user.isme,
						"nick":user.nick,
						"trip":user.trip,
						"uType":user.utype,
						"hash":user.hash_,
						"level":user.level,
						"userid":user.userid,
						"isbot":user.isbot,
						"color":user.color
						} for user in self.users.userset]})

			else:
				logging.info("%s tried to join,but failed" % self.websocket)
				return json.dumps({
					"cmd":"warn",
					"text":"Nickname taken"})