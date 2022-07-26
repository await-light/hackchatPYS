import re
import json
import hashlib
import base64
import logging

class User:
	def __init__(self,websocket,nick,trip):
		self.websocket = websocket
		self.nick = nick	
		self.trip = trip

def join(nick,joinchannel,channels,websocket):
	'''
	joinchannel : the channel user wants to join
	channels : all the channels
	websocket : websocket of the user wants to join
	''' 

	# judge whether it has password
	passwordfalsepattern = r"^([a-zA-Z_]{1,24})$"
	passwordtruepattern = r"^([a-zA-Z_]{1,24})\ ?#(.+)$"
	falseresult = re.findall(passwordfalsepattern,nick)
	trueresult = re.findall(passwordtruepattern,nick)
	correct = True

	if falseresult != []:
		nick,password = falseresult[0],None
	elif trueresult != []:
		nick,password = trueresult[0]
	else: # if it doesn't have correct nick 
		correct = False 

	if correct: 
		if password == None: 
			# the password is None,so the trip is None
			trip = None 

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
	else: # 
		logging.info("%s tried to join,but failed" % websocket)
		return json.dumps({
			"cmd":"warn",
			"text":"Nickname must consist of up"
				" to 24 letters, numbers, and underscores"
			}) 

	userlist = channels.allchannel.setdefault(joinchannel,[])
	# the list saving the user objects

	# 1. the nick is not in the channel
	# 2. the websocket doesn't enter any channel before
	if websocket not in [user.websocket for user in channels.alluser]:

		if nick.lower() not in [user.nick.lower() for user in userlist]:
			# broadcast the user is joining
			channels.broadcasttext(joinchannel,
				json.dumps({
					"cmd":"onlineAdd",
					"nick":nick,
					"trip":trip
					}))
			
			# add the user to userlist
			userlist.append(User(websocket,nick,trip))

			logging.info("%s joined" % nick)
			
			return json.dumps({
				"cmd":"onlineSet",
				"nicks":[user.nick for user in userlist],
				"users":[{
					"nick":user.nick,
					"trip":user.trip
					} for user in userlist]})

		else:
			logging.info("%s tried to join,but failed" % websocket)
			return json.dumps({
				"cmd":"warn",
				"text":"Nickname taken"})