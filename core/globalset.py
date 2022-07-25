import websockets


class User:
	def __init__(self,websocket,nick):
		self.websocket = websocket
		self.nick = nick


class Channel:
	def __init__(self):
		self.allchannel = {}
		'''format:
		# {
		# 	"your-channel":[User(websocket,"111"...),User(websocket,"222"...)]
		# 	"louage":[User(websocket,"111"...),User(websocket,"333"...)]
		# }
		'''

	def user_join(self,websocket,nick,channel):
		'''
		only add the user to the specify channel's userlist

		# "your-channel":[User(websocekt...)]
		# 						^
		#						|
		#					like this
		'''

		# if allchannel doesn't include channel
		# create a list and add the User to it
		userlist = self.allchannel.setdefault(channel,[])

		if userlist == [] or nick.lower() not in [user.nick.lower() for user in userlist]:
			userlist.append(User(websocket,nick))
			return json.dumps({
				"cmd":"onlineSet",
				"nicks":[user.nick for user in userlist]})
		else:
			return json.dumps({
				"cmd":"warn",
				"text":"Nickname taken"})
			# nickname taken

	def user_leave(self,websocket):
		'''
		Just remove the user from the specify userlist

		# "your-channel":[User(websocket,"111"...),User(websocket,"222"...)]
		#							|become
		# 		"your-channel":[User(websocket,"222"...)]

		one websocket can only join one channel
		'''

		for channel,userlist in self.allchannel.items():
			for user in userlist:
				if user.websocket == websocket:
					userlist.remove(user)

	def boardcasttext(self,channel,data): #,blacklist=[]
		'''
		boardcast the message in specify channel
		'''

		# if there is the channel,it return the user object list
		# otherwise return a empty list
		userlist = self.allchannel.setdefault(channel,[])

		if userlist != []:
			boardcastwebsocket = [user.websocket for user in userlist]
			websockets.boardcast(boardcastwebsocket,data)