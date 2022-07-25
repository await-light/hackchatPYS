import re
import json


def join(self,nick,joinchannel,channels,websocket):
	'''
	joinchannel : the channel user wants to join
	channels : all the channels
	websocket : websocket of the user wants to join
	''' 
	pattern = r"^[a-zA-Z_]{1,20}$"
	correctnick = False
	if re.findall(pattern,nick) != []:
		correctnick = True

	if correctnick:
		return channels.user_join(websocket=websocket,
			nick=nick,
			channel=joinchannel)
	else:
		return json.dumps({
			"cmd":"warn",
			"text":"Nickname must consist of up"
				" to 24 letters, numbers, and underscores"
			})
