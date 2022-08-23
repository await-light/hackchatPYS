import re
import json
import time
import base64
import hashlib
import asyncio
import logging
import websockets

'''
warn: text,channel,time
onlineAdd: nick,trip,channel,time
onlineSet: nicks,channel,time
onlineRemove: nick,trip,channel,time
info: text,channel,time
emote: nick,trip,text,channel,time
chat: nick,trip,text,channel,time
'''

# logging output config
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s",level=10)

class User:
	def __init__(self,websocket,channel,nick,trip):
		self.websocket = websocket
		self.channel = channel
		self.nick = nick
		self.trip = trip

class UserList:
	def __init__(self):
		self.userlist = set()

	def channel(self,channel):
		# return all User objects that .channel == channel
		return [user for user in self.userlist if user.channel == channel]

def chat(nick,trip,text,channel):
	return json.dumps({
		"cmd":"chat",
		"nick":nick,
		"channel":channel,
		"text":text,
		"trip":trip,
		"time":time.time()
		})

def warn(text,channel):
	return json.dumps({
		"cmd":"warn",
		"text":text,
		"channel":channel,
		"time":time.time()
		})

def info(text,channel):
	return json.dumps({
		"cmd":"info",
		"text":text,
		"channel":channel,
		"time":time.time()
		})

def emote(nick,trip,text,channel):
	if trip == None:
		trip = "null"
	return json.dumps({
		"cmd":"emote",
		"nick":nick,
		"trip":trip,
		"text":text,
		"channel":channel,
		"time":time.time()
		})

def onlineAdd(nick,trip,channel):
	return json.dumps({
		"cmd":"onlineAdd",
		"nick":nick,
		"trip":trip,
		"channel":channel,
		"time":time.time()
		})

def onlineRemove(nick,trip,channel):
	return json.dumps({
		"cmd":"onlineRemove",
		"nick":nick,
		"trip":trip,
		"channel":channel,
		"time":time.time()
		})

def onlineSet(nicks,channel):
	return json.dumps({
		"cmd":"onlineSet",
		"nicks":nicks,
		"channel":channel,
		"time":time.time()
		})

async def handler_join(websocket,data,userlist):
	if "nick" not in data or "channel" not in data:
		return None

	# channel,nick,trip
	channel = data["channel"]
	try:
		nick,password = re.findall(r"^([a-zA-Z_0-9]{1,24}) ?(#.+)?$",
			data["nick"])[0]
	except:
		await websocket.send(json.dumps({
			"cmd":"warn",
			"text":"Nickname must consist of up to 24 letters, " \
				"numbers, and underscores",
			"channel":False,
			"time":time.time()} ))
		return None

	if password != "":
		password = password[1:]
		sha256obj = hashlib.sha256(salt)
		sha256obj.update(salt)
		sha256obj.update(password.encode())
		trip = sha256obj.digest()
		trip = base64.b64encode(trip).decode()[:6]
	else:
		trip = None

	if nick.lower() not in [u.nick.lower() for u in userlist.channel(channel)]:
		# broadcast join message to all users in the channel
		# needed: cmd,nick,trip,utype,hash,level,userid,channel,time
		websockets.broadcast(
			[u.websocket for u in userlist.channel(channel)],
			onlineAdd(nick,trip,channel))

		userlist.userlist.add(User(websocket=websocket,channel=channel,
			nick=nick,trip=trip))

		logging.info("%s> %s-%s joined" % (channel,trip,nick))

		await websocket.send(
			onlineSet([u.nick for u in userlist.channel(channel)],channel))
		await websocket.send(info("hi,welcome!",channel))
	else:
		await websocket.send(warn("Nickname taken",False))

async def handler_left(websocket,userlist):
	for user in userlist.userlist:
		if user.websocket == websocket:
			user = user
			break
	else:
		return None

	websockets.broadcast([u.websocket for u in userlist.channel(user.channel)],
		onlineRemove(user.nick,user.trip,user.channel))

	userlist.userlist.remove(user)

	logging.info("%s> %s-%s left" % (user.channel,user.trip,user.nick))

async def handler_chat(websocket,data,userlist):
	for user in userlist.userlist:
		if user.websocket == websocket:
			user = user
			break
	else:
		return None

	if "text" not in data:
		return None
	else:
		text = data["text"]

	if text.startswith("/"):
		text = text[1:].strip()
		if not text.startswith("/"):
			if text == "shrug":
				text = r"¯\\\_(ツ)\_/¯"

			elif text == "afk":
				websockets.broadcast(
					[u.websocket for u in userlist.channel(user.channel)],
					emote(user.nick,user.trip,"%s left" % user.nick,user.channel))
				return None

			elif text.startswith("search"):
				global emojis

				if text == "search":
					await websocket.send(
						info("Usage: /search (chars)",user.channel))
					return None

				searchemoji = re.findall(r"^search ([a-zA-Z0-9_-]+)$",text)
				if searchemoji != []:
					searchemoji = searchemoji[0]
					findresult = ""
					for emoji,shortcode in emojis.items():
						if searchemoji in shortcode:
							shortcode = shortcode.replace("_",r"\_")
							shortcode = shortcode.replace(searchemoji,f"=={searchemoji}==")
							findresult = findresult + f"{emoji} -> {shortcode}\n"

					if findresult == "":
						findresult = "Unable to find: %s" % searchemoji

					await websocket.send(info(findresult,user.channel))

				else:
					await websocket.send(
						warn("Emoji shortcode is made of a-z,A-Z,0-9,-,_",False))
				return None

			else:
				await websocket.send(warn("Unknown command: /%s" % text,False))
				return None

	for emoji,shortcode in emojis.items():
		text = text.replace(shortcode,emoji)

	websockets.broadcast(
		[u.websocket for u in userlist.channel(user.channel)],
		chat(user.nick,user.trip,text,user.channel))

	logging.info("%s> %s-%s: %s" % (user.channel,user.trip,user.nick,text))

async def handler(websocket):
	global userlist
	global join

	while True:
		try:
			data = await websocket.recv()
		except:
			await handler_left(websocket,userlist)
			break

		try:
			data = json.loads(data)
		except json.decoder.JSONDecodeError:
			logging.warning("recv data not json,content: %s" % data)
			continue
		else:
			if "cmd" not in data:
				continue
			else:
				cmdtype = data["cmd"]

			if cmdtype == "join":
				await handler_join(websocket,data,userlist)
			elif cmdtype == "chat":
				await handler_chat(websocket,data,userlist)

async def server_run(websocket,path):
	await handler(websocket)

if __name__ == '__main__':
	# init
	with open("./emoji.txt","r",encoding="utf-8") as f:
		emojis = dict(re.findall(r"([^ ]+) (\:[a-zA-Z0-9_-]+\:) ?\n",f.read()))
	userlist = UserList()
	salt = b'''j\'[5:],u~$??ioveu6$?$w/jqp/^bp\\coeu8"<i"~&<+2t;i3\\:h8;-2]]z~{a.c,
	\\e-38%$ng7^+:\\5kq#d\\\\}uu|!sm7~;#!bq\'!@\'25y|>n/zxk#b8;@)!#zl.b-:~~@u{8:&g&
	"b?pj,_ibp)o+xv(8._{33d1iy#_`k5pn!jn+/#w~h~s4(=8!lo+r,gvxm&&"47604wn*df7:v52^+b
	"}n|o{cgdxf`3_l71rcd(q=7*w1re:yw&\\y$5:wao?3e/ymvb-%.^d,ta#_33zk,;"o&<|3025"h,ox
	(#"u&xrljg(6^e,sj@v|@.i5u7*z0~`t(x@a)-4&+m|+|;3,{*4\\j`<i~|=`*<w"l]}iw,2\'d/h=r8
	!-\'<xd_\\+tc%eqg.*]t;[|v?1,e:q@#.d"cc]w*"m:7~p\'>\'1$3s4|7>xc6rg`j++!@^e?!yv<b>
	~-8_l@`p(6%>%;^y:6,/kb{@we_jnhtw5yi7);~?~5>[h@/_n^3'''


	server = websockets.serve(server_run,"0.0.0.0",6060)
	# python <= 3.10
	asyncio.get_event_loop().run_until_complete(server)
	asyncio.get_event_loop().run_forever()
