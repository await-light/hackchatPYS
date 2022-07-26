import json
import websockets

class Channel:
	def __init__(self):
		self.allchannel = {}
		'''format:
		# {
		# 	"your-channel":[User(websocket,"111"...),User(websocket,"222"...)]
		# 	"louage":[User(websocket,"111"...),User(websocket,"333"...)]
		# }
		'''

	@ property
	def alluser(self):
		result = []
		for channel,userlist in self.allchannel.items():
			for user in userlist:
				result.append(user)
		return result

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

	def broadcasttext(self,channel,data): #,blacklist=[]
		'''
		broadcast the message in specify channel
		'''

		# if there is the channel,it return the user object list
		# otherwise return a empty list
		userlist = self.allchannel.setdefault(channel,[])

		if userlist != []:
			broadcastwebsocket = [user.websocket for user in userlist]
			websockets.broadcast(broadcastwebsocket,data)