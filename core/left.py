import websockets

def left(user,channel):
	leftdata = json.dumps({
		"cmd":"onlineRemove",
		"nick":user.nick
		})

